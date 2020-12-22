from database.database import database
from database.functions import _parse_params, _paginateDict, _make_id_link, get_from_db


class categoriesDatabase(object):
    def __init__(self, cnx=None, host='catalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService',
                 user=None, password=None, key_columns=None, notIncludedCols=None):
        self.cnx = cnx
        if not cnx:
            db = database(host=host, db=db, user=user, password=password)
            self.cnx = db.cnx
        self.key_columns, self.notIncludedCols = key_columns, notIncludedCols
        if not notIncludedCols: self.notIncludedCols = ['fields', 'limit', 'offset']

        self.category_ids = [1, 2, 3, 4, 5]

    def get_categories(self, params=None, url=''):
        limit, offset = int(params.get('limit', 10)), int(params.get('offset', 0))
        fields = params.get('fields', '*')
        custParams = params.copy()
        data = get_from_db(cnx=self.cnx, table='categories', params=custParams, fields=fields,
                                paginate=True, limit=limit, offset=offset, url=url, notIncludedCols = self.notIncludedCols)
        data['data'] = _make_id_link(data['data'], url=url + 'categories/{}', key='idCategories')
        return data

    def get_categories_by_id(self, idCategories, params=None, url=''):
        limit, offset = int(params.get('limit', 10)), int(params.get('offset', 0))
        fields = params.get('fields', '*')
        custParams = params.copy()
        query = """
                SELECT catalog.idTutors as idTutors, name, byline, linkedin, resume, website, imageLink
                FROM catalog JOIN tutors
                ON catalog.idTutors = tutors.idTutors
                WHERE catalog.idCategories={}
            """.format(str(idCategories))
        table = 'categories/{}'.format(idCategories)
        data = get_from_db(cnx=self.cnx, table=table, q=query, params=custParams, fields=fields, paginate=True, limit=limit, offset=offset,
                           url=url, notIncludedCols = self.notIncludedCols)
        data['data'] = _make_id_link(data['data'], url=url+'tutors/{}', key='idTutors')
        return data