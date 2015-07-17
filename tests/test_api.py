# -*- coding: utf-8 -*-
class TestApi(object):

    sample_request_data =  {'count': 50, 'radius': 1000, 'position': {'lat': 59.33258, 'lng': 18.0649}, 'tags': ["clothes"]}

    def test_response_code_api(self, post):

        response = post('/search', data=self.sample_request_data)
        assert response.status_code == 200

    def test_response_static_dir(self, get):

        response = get('/map.js')
        assert response.status_code == 200

    def test_product_availability(self, post):

        response = post('/search', data=self.sample_request_data).json
        assert len(response['products']) == 50


    def test_hitting_cache(self, post):

        response1 = post('/search', data=self.sample_request_data).json
        response2 = post('/search', data=self.sample_request_data).json

        assert response1['execution_time'] > response2['execution_time']



#TODO: we could add more tests, but for test app it will be enough i think
