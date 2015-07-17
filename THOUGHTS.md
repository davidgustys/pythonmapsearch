App
-------
Tried to follow established convention(code that was already writen) as much as possible,
meaning storing configuration variables inside app.config, calling configuration blocks from inside create_app method


Database
--------
When reading the the requirements several things pop into my microseconds

1. I will need to read the csv files
2. Will need to query by geopoint and radius
2. To gain performance store/cache csv file content into variable by index

This lead me to using simple geo library and writing stupid simple database that does all the above.


Api
--------

1. As map.js was already written, looked what additional variables it was expecting and according to that wrote the `/search` endpoint, i.e product object was expected to have "shop" object, thus i wrote the response accordingly rather than changing the map.js .

2. Again to gain performance im caching(memoize) the response bassed on paramenets passed, it might not be the most efficient thing Resource vise, but at super large scale (facebook), i do think they are caching data even on coordinates..

3. Added serving client(static dir)


map.js
--------

1. Enabled srcoll zoom, not sure why it was disabled
2. Used jquery promise based ajax call for api query



Tests
--------

1. Had to get bit familiar pytest, added some basic tests to demonstrate understanding, though in real life application those test would be more sophisticated and i would test every edge case.

2. For in code "expected" error, im throwing exceptions.

3. In production application i would use BDD approach to do e2e(end to end) tests.


Other Notes
--------

1. To mention - prior to this test had no experience with Flask, Pytest, Mapbox, but their documentation was easy to read so it wasn't a problem.

2. I tried to fallow python code convention as much as i know them. As stated i used python only several years ago on my hobby projects, though now it reminds me of coffeescript and I always forget to put colons at the end of logic statements.

3. "Database" could be improved by abstracting it more adding compound keys, etc..
