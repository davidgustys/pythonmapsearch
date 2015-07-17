# -*- coding: utf-8 -*-

import json
from flask import Blueprint, current_app, jsonify, render_template, request, make_response
from werkzeug.exceptions import BadRequest

api = Blueprint('api', __name__, template_folder='../client', static_folder='../client', static_url_path='')


def data_path(filename):
    data_path = current_app.config['DATA_PATH']
    return u"%s/%s" % (data_path, filename)



@api.route('/', methods=['GET'])
def index():

    return render_template('index.html')


@api.route('/search', methods=['POST'])
def search():

    app = current_app


    try:
        json_request = request.get_json()
    except BadRequest, e:
        return json.dumps({'success':False}), 500, {'ContentType':'application/json'}



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

    #match shops and tags
    products_to_search = []
    for single_tag in json_request['tags']:

        #check wether we have such tag at all
        if tags_data_index_tag.has_key(single_tag):

            tag_id = tags_data_index_tag[single_tag][0]['id']

            #if we do search in the are shops
            for shop_id in shops_in_area:

                if taggings_data_index_shop_id.has_key(shop_id):

                    if taggings_data_index_tag.has_key(tag_id):

                        products_to_search.extend(products_data_index_shop_id[shop_id])



    #check if we had tags, but matched no shops
    if len(products_to_search) <= 0 and len(json_request['tags']) > 0:
        print 'no products'
        return jsonify({'products':[]})


    #check if we had no tags prvovided
    if len(json_request['tags']) <= 0:
        #then traverse all products

        for shop_id in shops_in_area:
            products_to_search.extend(products_data_index_shop_id[shop_id])


    #sort by populiarity
    products_to_search.sort(key=lambda x: float(x['popularity']), reverse=True)


    #now that we have the right products
    #append with shop data and limit by provided count
    products = []
    range_number = int(json_request['count'])

    #check if we have request number of products
    if range_number > len(products_to_search):
        range_number = len(products_to_search)

    for i in range(range_number):

        products_to_search[i]['shop'] = shops_data_index_id[products_to_search[i]['shop_id']][0]
        products.append(products_to_search[i])


    #print products[0]
    return jsonify({'products': products})
