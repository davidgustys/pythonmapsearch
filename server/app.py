# -*- coding: utf-8 -*-

import os
from flask import Flask
from server.api import api
from server.database import GeoDb

from geoindex import GeoGridIndex, GeoPoint

def create_app(settings_overrides=None):

    app = Flask(__name__, static_url_path='/static')
    configure_settings(app, settings_overrides)
    configure_database(app)
    configure_blueprints(app)

    return app


def configure_settings(app, settings_override):
    parent = os.path.dirname(__file__)
    data_path = os.path.join(parent, '..', 'data')
    static_folder = os.path.join(parent, '..', 'client')
    app.config.update({
        'DEBUG': True,
        'TESTING': False,
        'DATA_PATH': data_path,
        'STATIC_FOLDER': static_folder
    })
    if settings_override:
        app.config.update(settings_override)

def configure_database(app):

    app.db = GeoDb()


    app.config.update({
        'DB': {
            'table_index': {
                'products': ['shop_id'],
                'tags': ['tag', 'id'],
                'taggings': ['tag_id', 'shop_id'],
                'shops': ['latlng', 'id'],
            }
        }
    })

    with app.app_context():

        #cache table data
        for table in os.listdir(app.config['DATA_PATH']):
            table_name = table.replace('.csv', '').lower()
            app.db.fill_table(table_name)

            #index table on fields
            for field_name in app.config['DB']['table_index'][table_name]:
                app.db.index_table(table_name, field_name)


def configure_blueprints(app):
    app.register_blueprint(api)
