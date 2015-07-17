# -*- coding: utf-8 -*-
import json, datetime, functools, cPickle
from flask import Blueprint, jsonify, render_template, request, make_response, current_app as app
from werkzeug.exceptions import BadRequest

api = Blueprint('api', __name__, template_folder='../client', static_folder='../client', static_url_path='')


#Will serve as a cache for us
#In Production we would probaby use memcached or redis
#We would also monitor the size of the cache, as caching on "coordinates" is not that good i think..
class MemoizeMutable:
    """Decorator for memorising/caching function output"""
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}
    def __call__(self, *args, **kwds):
        import cPickle
        str = cPickle.dumps(args, 1)+cPickle.dumps(kwds, 1)
        if not self.memo.has_key(str):
            # print "miss"  # DEBUG INFO
            self.memo[str] = self.fn(*args, **kwds)
        # else:
        #     print "hit"  # DEBUG INFO

        return self.memo[str]


@MemoizeMutable
def _search(json_request):
    """Does the actual searching for us.

    :param json_request: dict of search params
    :returns: list of dicts containing product information
    """

    ##--For reference
    #taggings - id,shop_id,tag_id
    #shops - id,name,lat,lng
    #products - id,shop_id,title,popularity,quantity
    #tags - id,tag

    #fetch data from tables
    shops_data_index_id = app.db.get_data('shops', 'id')
    products_data_index_shop_id = app.db.get_data('products', 'shop_id')
    taggings_data_index_shop_id = app.db.get_data('taggings', 'shop_id')
    taggings_data_index_tag = app.db.get_data('taggings', 'tag_id')
    tags_data_index_tag = app.db.get_data('tags', 'tag')


    #search in area
    shops_in_area = app.db.get_data('shops', 'latlng', (json_request['position']['lat'], json_request['position']['lng']), (float(json_request['radius'])/1000))

    #no products in area, less problems for us..
    if len(shops_in_area) <= 0:
        return []


    #match shops and tags
    products_to_search = []
    for single_tag in json_request['tags']:

        #check wether we have such tag at all
        if tags_data_index_tag.has_key(single_tag):

            #get the id of the tag
            tag_id = tags_data_index_tag[single_tag][0]['id']

            #search for tag in area shops
            for shop_id in shops_in_area:

                if taggings_data_index_shop_id.has_key(shop_id) \
                and taggings_data_index_tag.has_key(tag_id):

                    #add that shops products search list..
                    products_to_search.extend(products_data_index_shop_id[shop_id])



    #check if we had tags, but matched no shops
    if len(products_to_search) <= 0 and len(json_request['tags']) > 0:
        return []


    #check if we had no tags prvovided
    if len(json_request['tags']) <= 0:

        #then traverse all products
        for shop_id in shops_in_area:
            products_to_search.extend(products_data_index_shop_id[shop_id])


    #sort by populiarity
    #TODO: this could be done at database level
    products_to_search.sort(key=lambda x: float(x['popularity']), reverse=True)


    #now that we have the right products
    #append with shop data and limit by provided count
    products = []
    range_number = int(json_request['count'])

    #check if we have request number of products
    if range_number > len(products_to_search):
        range_number = len(products_to_search)

    #TODO: this could have been done earlier
    #Somewhere in the loops were we are adding products to the search list
    #but because we are sorting the the data just above  we need to that here
    for i in range(range_number):

        products_to_search[i]['shop'] = shops_data_index_id[products_to_search[i]['shop_id']][0]
        products.append(products_to_search[i])


    return products

#render index
@api.route('/', methods=['GET'])
def index():
    """Renders in the Index file"""
    return render_template('index.html')


@api.route('/search', methods=['POST'])
def search():
    """Api endpoint for product search"""
    try:
        json_request = request.get_json()
    except BadRequest, e:
        return json.dumps({'success':False}), 400, {'ContentType':'application/json'}


    timer = datetime.datetime.now()
    products = _search(json_request)
    timer = datetime.datetime.now() - timer

    #print products[0]
    return jsonify({'products': products, 'execution_time': timer.microseconds})
