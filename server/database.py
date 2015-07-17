import os, csv
from geoindex import GeoGridIndex, GeoPoint


class GeoDb(object):
    """
    Super cool database that does exectly what we need :)
    """
    def __init__(self):
        """
        Fils the "db" and "indexes"
        """

        self.db = GeoGridIndex()
        self.tables = {}



    def data_path(self, filename):

        parent = os.path.dirname(__file__)
        data_path = os.path.join(parent, '..', 'data')
        return u"%s/%s" % (data_path, filename)


    def fill_table(self, table_name):


        nice_list = []
        header_line = ''
        with open(self.data_path(table_name + '.csv'), mode='r') as infile:

            reader = csv.reader(infile)

            header_line = next(reader)

            for row in reader:



                dict_entry = {}
                for i in range(len(row)):

                    dict_entry[header_line[i]] = row[i]

                nice_list.append(dict_entry)

        if not self.tables.has_key(table_name):
            self.tables[table_name] = {
                'field': {},
                'rawdata': {},
            }

        self.tables[table_name]['rawdata'] = nice_list


    def index_table(self, table_name, field_name):

        indexed_table = {}
        for row in self.tables[table_name]['rawdata']:

            if not self.tables[table_name]['field'].has_key(field_name):
                self.tables[table_name]['field'][field_name] = {}

            #special case
            if field_name == 'latlng':

                if row.has_key('lat') and row.has_key('lng'):

                    if not isinstance(self.tables[table_name]['field'][field_name], GeoGridIndex):
                        self.tables[table_name]['field'][field_name] = GeoGridIndex()

                    self.tables[table_name]['field'][field_name].add_point(GeoPoint(float(row['lat']), float(row['lng']), ref=row))

            else:
                if not self.tables[table_name]['field'][field_name].has_key(row[field_name]):
                    self.tables[table_name]['field'][field_name][row[field_name]] = []


                    self.tables[table_name]['field'][field_name][row[field_name]].append(row)


    def get_data(self, table_name, field_name, match_on=None, radius=None):

        if match_on is not None:
            if field_name == 'latlng':
                assert isinstance(match_on, tuple), \
                'For latlng fiel, match_on parameneter need to be tuple of coordinates'

                assert radius is not None, \
                "For latlng fields, radius needs to be provided"

                center_point = GeoPoint(*match_on)


                matched_rows = {}
                for point, distance in self.tables[table_name]['field'][field_name].get_nearest_points(center_point, radius, 'km'):

                    point.ref.update({'dinstance': format(distance, '.3f')})
                    #assuming that all db entries have id's
                    matched_rows[point.ref['id']] = point.ref

                return matched_rows

            else:
                if self.tables[table_name]['field'][field_name].has_key(match_on):
                    return self.tables[table_name]['field'][field_name][match_on]
                else:
                    return {}

        else:
            return self.tables[table_name]['field'][field_name]
