class TestDB(object):

    def test_db_conf_present(self, app):

        assert app.config.has_key('DB')
        assert len(app.config['DB']) > 0

    def test_all_tables_filled(self, app):

        db_config = app.config['DB']

        for table_name in db_config['table_index']:
            assert len(app.db.tables[table_name]['rawdata']) > 0

    def test_query_regular_data_by_index(self, app):

        tags = app.db.get_data('tags', 'tag')

        assert isinstance(tags, dict)
        assert tags.has_key('lights')
        assert isinstance(tags['lights'], list)
        assert tags['lights'][0]['tag'] == 'lights'

    def test_query_point_match(self, app):

        matched_points = app.db.get_data('shops', 'latlng', (59.33258, 18.0649), 1)
        assert len(matched_points) > 0


#TODO: again, we could add  way more tests, but for test app it will be enough i think
