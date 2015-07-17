import os, csv
from geoindex import GeoGridIndex, GeoPoint


class GeoDb(object):
    """
    Super cool database that does exectly what we need :)
    """
    def __init__(self):

        self.tables = {}

    def data_path(self, filename):
        """Return full path to our "tables"/data sources

        :param filename: the name of the csv file to use as a source
        :returns: full file path
        """

        parent = os.path.dirname(__file__)
        data_path = os.path.join(parent, '..', 'data')
        return u"%s/%s" % (data_path, filename)


    def fill_table(self, table_name):
        """Fills our "database"/cache variable with data from csv file

        :param table_name: the name of "table"(data file name without 'csv' postfix)
        :returns: void
        """


        nice_list = []
        header_line = ''

        #open csv file for reading
        with open(self.data_path(table_name + '.csv'), mode='r') as infile:

            reader = csv.reader(infile)

            #read the first/header line for dict key names
            header_line = next(reader)

            #iterate over csv and fill our "tables"/cache variable
            for row in reader:

                dict_entry = {}
                for i in range(len(row)):

                    dict_entry[header_line[i]] = row[i]

                nice_list.append(dict_entry)

        #just making sure our dicts are declared nicily so that we don't key KeyError's
        if not self.tables.has_key(table_name):
            self.tables[table_name] = {
                'field': {},
                'rawdata': {},
            }

        #we are calling it "rawdata" as the date is unIndexed
        self.tables[table_name]['rawdata'] = nice_list


    def index_table(self, table_name, field_name):
        """Indexes the "tables" on specified field

        :param table_name: the name of "table"(data file name without 'csv' postfix)
        :param field_name: the name of field on which we want to index our table
        :returns: void
        """

        #iterating over raw data for indexing..
        for row in self.tables[table_name]['rawdata']:

            #making sure "holder" variables are defined for use..
            if not self.tables[table_name]['field'].has_key(field_name):
                self.tables[table_name]['field'][field_name] = {}

            #for "latlng" field we use "special" indexing..
            if field_name == 'latlng':

                assert row.has_key('lat') and row.has_key('lng')

                #initializing "latlng" field as "Geo" field
                if not isinstance(self.tables[table_name]['field'][field_name], GeoGridIndex):
                    self.tables[table_name]['field'][field_name] = GeoGridIndex()

                #indexing coordinates/geo points
                self.tables[table_name]['field'][field_name].add_point(GeoPoint(float(row['lat']), float(row['lng']), ref=row))

            #indexing regular fields
            else:
                #making sure "holder" variables are defined for use..
                if not self.tables[table_name]['field'][field_name].has_key(row[field_name]):
                    self.tables[table_name]['field'][field_name][row[field_name]] = []

                self.tables[table_name]['field'][field_name][row[field_name]].append(row)


    def get_data(self, table_name, field_name, center_point=None, radius=None):
        """Get data from table by indexed field name or search for nearby geopoints

        :param table_name: the name of "table"(data file name without 'csv' postfix)
        :param field_name: the name of field on which we want to index our table
        :param center_point: tuple coordinates variable from were we are "drawing" our radius
        :param radius: radius(in meters) in which we are looking for geopoints
        :returns: dict "query" results
        """

        #check if we are searching for geo points
        if field_name == 'latlng':

            #some basic checking
            if not isinstance(center_point, tuple):
                raise ValueError('For latlng fiel, match_on parameneter needs to be tuple of coordinates')

            if radius is None:
                raise ValueError('For latlng fields, radius needs to be provided')

            #the center point from were we are "drawing" our radius
            center_point = GeoPoint(*center_point)

            matched_rows = {}
            for point, distance in self.tables[table_name]['field'][field_name].get_nearest_points(center_point, radius, 'km'):

                point.ref.update({'dinstance': format(distance, '.3f')})

                #assuming that all db entries have id's
                matched_rows[point.ref['id']] = point.ref

            return matched_rows

        #match on index field
        else:
            return self.tables[table_name]['field'][field_name]
