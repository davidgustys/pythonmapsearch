# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, jsonify, render_template, request


api = Blueprint('api', __name__, template_folder='../client', static_folder='../client', static_url_path='')


def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)



@api.route('/', methods=['GET'])
def index():

    return render_template('index.html')


@api.route('/search', methods=['POST'])
def search():

    #taggings - id,shop_id,tag_id
    #shops - id,name,lat,lng
    #products - id,shop_id,title,popularity,quantity
    #tags - id,tag

    json =  request.get_json()



    #join tables :)
    app = current_app
    shops_data = app.db.get_data('shops', 'id')
    products_data = app.db.get_data('products', 'shop_id')
    taggings_data = app.db.get_data('taggings', 'shop_id')
    taggings_data_index_tag = app.db.get_data('taggings', 'tag_id')
    tags_data = app.db.get_data('tags', 'id')
    tags_data_index_tag = app.db.get_data('tags', 'tag')


    #search in area
    shops_in_area = app.db.get_data('shops', 'latlng', (json['position']['lat'], json['position']['lng']), (int(json['radius'])/1000))


    products_to_search = []
    shops_with_tags = {}
    for single_tag in json['tags']:

        #check wether we have such tag at all
        if tags_data_index_tag.has_key(single_tag):

            tag_id = tags_data_index_tag[single_tag][0]['id']

            #if we do search in the are shops
            for shop_id in shops_in_area:

                if taggings_data.has_key(shop_id):

                    if taggings_data_index_tag.has_key(tag_id):

                        products_to_search.extend(products_data[shop_id])



    #check we had any tags, if not we have to search through all the shops
    if len(products_to_search) <= 0:

        for shop_id in products_data:
            products_to_search.extend(products_data[shop_id])


    #sort by populiarity
    products_to_search.sort(key=lambda x: float(x['popularity']), reverse=True)


    #now that we have the right products
    #append with shop data and limit by provided count
    products = []
    for i in range(json['count']):

        products_to_search[i]['shop'] = shops_data[products_to_search[i]['shop_id']][0]
        products.append(products_to_search[i])



    return jsonify({'products': products})
