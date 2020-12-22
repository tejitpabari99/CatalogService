import datetime

from database.database import database
from database.functions import _parse_params, _paginateDict, _make_id_link, \
    get_from_db, get_last_id, add_db, delete_db, update_db, convert_datetime_str


class bookingsDatabase(object):
    def __init__(self, cnx=None, host='catalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService',
                 user=None, password=None, key_columns=None, notIncludedCols=None):
        self.cnx = cnx
        if not cnx:
            db = database(host=host, db=db, user=user, password=password)
            self.cnx = db.cnx
        self.key_columns, self.notIncludedCols = key_columns, notIncludedCols
        if not key_columns: self.key_columns = ['idTutors', 'idProfile', 'meetingDate', 'bookingDate', 'idCategories', 'meetingTime']
        if not notIncludedCols: self.notIncludedCols = ['fields', 'limit', 'offset', 'idTutors']


    def get_bookings(self, idTutors='', idProfile='', params=None, url=''):
        if not idTutors and not idProfile: raise Exception('No idTutors or idProfile')
        custParams = params.copy()
        if idTutors: custParams['idTutors'] = idTutors
        elif idProfile: custParams['idProfile'] = idProfile
        limit, offset = int(custParams.get('limit', 10)), int(custParams.get('offset', 0))
        custUrl = url + 'tutors/'+str(idTutors)+'/bookings'
        data = get_from_db(cnx=self.cnx, table='bookings', params=custParams,
                           paginate=True, limit=limit, offset=offset, url=url,
                           custUrl=custUrl, notIncludedCols=self.notIncludedCols, urlNotIncludedCols=['idTutors', 'idProfile'])
        data['data'] = _make_id_link(data['data'], url=url + 'tutors/'+str(idTutors)+'/bookings/{}', key='idBookings')
        data['data'] = convert_datetime_str(data['data'], cols=['meetingDate', 'bookingDate'])
        return data

    def get_bookings_id(self, idBookings, idTutors='', idProfile='', params=None, url=''):
        if not idTutors and not idProfile: raise Exception('No idTutors or idProfile')
        custParams = params.copy()
        if idTutors: custParams['idTutors'] = idTutors
        elif idProfile: custParams['idProfile'] = idProfile
        custParams['idBookings']=idBookings
        data = get_from_db(cnx=self.cnx, table='bookings', params=custParams,
                           paginate=False, url=url, notIncludedCols=self.notIncludedCols)
        data['data'] = convert_datetime_str(data['data'], cols=['meetingDate', 'bookingDate'])
        return data

    def add_bookings(self, idTutors, params=None, url=''):
        custParams = params.copy()
        custParams['']
        for col in self.key_columns:
            if col not in custParams:
                raise Exception('Bookings add must have columns {}'.format(self.key_columns))


