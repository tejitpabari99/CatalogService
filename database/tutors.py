from database.database import database
from database.functions import _parse_params, _paginateDict, _make_id_link, \
    get_from_db, get_last_id, add_db, delete_db, update_db, convert_datetime_str

class tutorsDatabase(object):
    def __init__(self, cnx=None, host='catalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService',
                 user=None, password=None, key_columns = None, notIncludedCols = None):
        self.cnx = cnx
        if not cnx:
            db = database(host=host, db=db, user=user, password=password)
            self.cnx = db.cnx
        self.key_columns, self.notIncludedCols = key_columns, notIncludedCols
        if not key_columns: self.key_columns = ['name', 'byline', 'categories', 'experience']
        if not notIncludedCols: self.notIncludedCols = ['fields', 'limit', 'offset']

    def get_tutors(self, params=None, url=''):
        custParams = params.copy()
        query = """select idTutors, name, byline, linkedin, website, imageLink, group_concat(category_name) as categories from
            (select idTutors, name, byline, linkedin, resume, website, imageLink, idCategories,
                (select category from categories where catalog.idCategories=categories.idCategories) as category_name
                from tutors
                join
                catalog
                using(idTutors)) as a
        group by idTutors, name"""
        limit, offset = int(params.get('limit', 10)), int(params.get('offset', 0))
        data = get_from_db(cnx=self.cnx, table='tutors', q=query, params=custParams,
                                paginate=True, limit=limit, offset=offset, url=url, notIncludedCols = self.notIncludedCols)
        data['data'] = _make_id_link(data['data'], url=url+'tutors/{}', key='idTutors')
        for d in data['data']: d['categories'] = d['categories'].split(',')
        return data
    
    def get_tutors_by_id(self, idTutors, url=''):
        custParams = {'idTutors': idTutors}
        query = """
        select idTutors, name, byline, linkedin, resume, website, imageLink, description, experience,
            group_concat(category_name) as categories from
            (select idTutors, name, byline, linkedin, resume, description, experience, website, imageLink, idCategories,
                (select category from categories where catalog.idCategories=categories.idCategories) as category_name
                from tutors
                join
                catalog
                using(idTutors)) as a"""
        data = get_from_db(cnx=self.cnx, q=query, params=custParams, paginate=False, url=url, notIncludedCols = self.notIncludedCols)
        data['data'][0]['categories'] = data['data'][0]['categories'].split(',')
        return data

    def add_tutor(self, idTutors, params, url=''):
        print(idTutors, params)
        custParams = params.copy()
        for col in self.key_columns:
            if col not in custParams:
                raise Exception('Tutors add must have columns {}'.format(self.key_columns))
        custParams['idTutors'] = idTutors
        categories = custParams.get('categories').split(',')
        del custParams['categories']

        data = add_db(self.cnx, 'tutors', custParams)
        idTutors = get_last_id(self.cnx)
        catalogAdd = [{'idTutors':idTutors, 'idCategories':c} for c in categories]
        data2 = add_db(self.cnx, 'catalog', catalogAdd)

        return self.get_tutors_by_id(idTutors, url=url)

    def delete_tutor(self, idTutors):
        custParams = {'idTutors':idTutors}
        data = delete_db(self.cnx, 'catalog', custParams)
        data2 = delete_db(self.cnx, 'tutors', custParams)
        return data2

    def update_tutor(self, idTutors, params, url=''):
        checkParams = {'idTutors':idTutors}
        addParams = params.copy()
        if "categories" in addParams:
            categories = addParams.get('categories').split(',')
            del addParams['categories']
            data = delete_db(self.cnx, 'catalog', checkParams)
            catalogAdd = [{'idTutors': idTutors, 'idCategories': c} for c in categories]
            data2 = add_db(self.cnx, 'catalog', catalogAdd)
        if addParams:
            data = update_db(self.cnx, 'tutors', checkParams=checkParams, addParams=addParams)
        return self.get_tutors_by_id(idTutors, url=url)


