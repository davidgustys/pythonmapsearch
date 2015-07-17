# -*- coding: utf-8 -*-


def test_search(post):

    sample_request_data =  {'count': 50, 'radius': 1000, 'position': {'lat': 59.33258, 'lng': 18.0649}, 'tags': ["clothes"]}

    response = post('/search', data=sample_request_data)

    print response.data

    assert 0
