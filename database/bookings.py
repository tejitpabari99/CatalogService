import datetime
import requests

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
        if not key_columns: self.key_columns = ['idTutors', 'meetingDate', 'bookingDate', 'idCategories', 'meetingTime',
                                                'imageLink', 'tuteeName', 'tuteeEmail']
        if not notIncludedCols: self.notIncludedCols = ['fields', 'limit', 'offset', 'idTutors']


    def get_bookings(self, idTutors, params=None, url=''):
        custParams = params.copy()
        custParams['idTutors'] = idTutors
        limit, offset = int(custParams.get('limit', 10)), int(custParams.get('offset', 0))
        custUrl = url + 'tutors/'+str(idTutors)+'/bookings'
        data = get_from_db(cnx=self.cnx, table='bookings', params=custParams,
                           paginate=True, limit=limit, offset=offset, url=url,
                           custUrl=custUrl, notIncludedCols=self.notIncludedCols, urlNotIncludedCols=['idTutors', 'idProfile'])
        data['data'] = _make_id_link(data['data'], url=url + 'tutors/'+str(idTutors)+'/bookings/{}', key='idBookings')
        data['data'] = convert_datetime_str(data['data'], cols=['meetingDate', 'bookingDate'])
        return data

    def get_bookings_id(self, idBookings, idTutors, params=None, url=''):
        if params: custParams = params.copy()
        else: custParams = {}
        custParams['idTutors'] = idTutors
        custParams['idBookings']=idBookings
        data = get_from_db(cnx=self.cnx, table='bookings', params=custParams,
                           paginate=False, url=url, notIncludedCols=self.notIncludedCols)
        data['data'] = convert_datetime_str(data['data'], cols=['meetingDate', 'bookingDate'])
        return data

    def add_bookings(self, idTutors, params=None, url=''):
        custParams = params.copy()
        custParams['idTutors'] = idTutors
        for col in self.key_columns:
            if col not in custParams:
                raise Exception('Bookings add must have columns {}'.format(self.key_columns))
        data = add_db(self.cnx, 'bookings', custParams)
        idBookings = get_last_id(self.cnx)
        custParams['idBookings'] = idBookings
        custParams['token'] = "sfsdfsdfsadfdsf"
        r = requests.post('https://ux5wwtq0bl.execute-api.us-east-2.amazonaws.com/default/approveBooking', params=custParams)
        return True

    # def approve_bookings(self, idBookings, idTutors, params=None, url=''):
    #     checkParams = {}
    #     checkParams['idTutors'] = idTutors
    #     checkParams['idBookings'] = idBookings
    #     data = update_db(self.cnx, 'bookings', checkParams=checkParams, addParams={'meetingStatus':'APPROVED'})
    #     return self.get_bookings_id(idBookings,idTutors)
    #
    # def reject_bookings(self, idBookings, idTutors, params=None, url=''):
    #     checkParams = {}
    #     checkParams['idTutors'] = idTutors
    #     checkParams['idBookings'] = idBookings
    #     data = update_db(self.cnx, 'bookings', checkParams=checkParams, addParams={'meetingStatus':'CANCELLED'})
    #     return self.get_bookings_id(idBookings,idTutors)


