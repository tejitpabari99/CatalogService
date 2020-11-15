import pymysql.cursors
import os
import json
import pandas as pd

class tutorsDatabase(object):
    def __init__(self, host='catalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService',
                 user=None, password=None, key_columns = None, notIncludedCols = None):
        if not user: user = os.getenv('dbuser','admin')
        if not password: password = os.getenv('dbpass','adminpass')
        self.key_columns, self.notIncludedCols = key_columns, notIncludedCols
        if not key_columns: self.key_columns = ['username', 'name', 'email']
        if not notIncludedCols: self.notIncludedCols = ['fields', 'limit', 'offset']

        self.cnx =  pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
        self.category_ids = [1,2,3,4,5]

    def _parse_params(self, params=None, joinTerm=' and ', quote=True, notIncluded=True):
        notIncludedCols = self.notIncludedCols if notIncluded else []
        if not params: return ''
        paramsList = ['{}="{}"'.format(k, v) if quote else '{}={}'.format(k, v)
                      for k, v in params.items() if k not in notIncludedCols]
        return joinTerm.join(paramsList)

    def _paginateDict(self, data, link, params=None, limit=10, offset=0):
        currParams, nextParams, prevParams = params.copy(),params.copy(),params.copy()
        currParamsStr, nextParamsStr, prevParamsStr = '', '', ''

        currParams['limit']=limit
        currParams['offset']=offset
        currParamsStr = link+ '?' + self._parse_params(currParams, '&', quote=False, notIncluded=False)

        nextOffset = offset + limit
        nextPaginate = len(data['data']) > 0
        if nextPaginate:
            nextParams['limit'] = limit
            nextParams['offset'] = nextOffset
            nextParamsStr = link+ '?' + self._parse_params(nextParams, '&', quote=False, notIncluded=False)

        prevOffset = -1
        if offset - limit > 0: prevOffset = offset-limit
        elif offset > 0: prevOffset = 0
        prevPaginate = prevOffset>-1
        if prevPaginate:
            prevParams['limit'] = limit
            prevParams['offset'] = prevOffset
            prevParamsStr = link+ '?' + self._parse_params(prevParams, '&', quote=False, notIncluded=False)
        data['paginate'] = {
            'currPage': currParamsStr,
            'prevPage': prevParamsStr,
            'nextPage': nextParamsStr
        }
        return data

    def _make_id_link(self, data, url, key):
        for d in data:
            d['link'] = url.format(d[key])
        return data

    def _get_category_from_ids(self, category_ids):
        query = """
                Select idCategories, category
                FROM categories 
                WHERE idCategories in ({})
                """.format(', '.join([str(i) for i in category_ids]))
        cursor = self.cnx.cursor()
        cursor.execute(query)
        resp = cursor.fetchall()
        categories = [r['category'] for r in resp]
        return categories

    def get_catalog(self, url='', category_ids=None, tutors_per_cat=5):
        if not category_ids: category_ids = self.category_ids
        query = """
        SELECT A.idTutors as idTutors, A.idCategories as idCategories, 
		name, byline, linkedin, resume, website, imageLink, category
        FROM
            (Select catalog.idCategories, catalog.idTutors, category
            FROM catalog JOIN categories on catalog.idCategories = categories.idCategories
            WHERE categories.idCategories in ({})) as A
            JOIN tutors on A.idTutors = tutors.idTutors
        ORDER BY category
        """.format(', '.join([str(i) for i in category_ids]))
        cursor = self.cnx.cursor()
        cursor.execute(query)
        resp = cursor.fetchall()
        data = {'data':[]}
        for i,(name,group) in enumerate(pd.DataFrame(resp).groupby('category')):
            catID = group['idCategories'].iloc[0]
            data['data'].append({
                'category': name,
                'data': self._make_id_link(json.loads(group.head(tutors_per_cat).to_json(orient='records')),
                                           url=url+'tutors/{}', key='idTutors'),
                'links': [
                    {'categories': url+'categories/{}'.format(catID)}
                ]

            })
        cursor.close()
        json.dump(data, open('data.json','w'), indent=2)
        return data

    def get_from_db(self, table='', q=None, params=None, fields='*', paginate=True, limit=10, offset=0, url=''):
        cursor = self.cnx.cursor()
        query = """Select {} from CatalogService.{}""".format(fields, table)
        if q: query = q
        paramsStr = self._parse_params(params, ' and ')
        if paramsStr: query += """\nwhere {}""".format(paramsStr)
        if paginate: query += """\nlimit {}, {}""".format(offset, limit)
        cursor.execute(query)
        data = {'data': cursor.fetchall()}
        cursor.close()
        if paginate:
            data = self._paginateDict(data, url + table, params=params, limit=limit, offset=offset)
        return data

    def get_tutors(self, params=None, paginate=True, limit=10, offset=0, url=''):
        fields = 'idTutors,name,byline,linkedin,resume,website,imageLink,categories'
        data = self.get_from_db(table='tutors',params=params, fields=fields,
                                paginate=paginate, limit=limit, offset=offset, url=url)
        data['data'] = self._make_id_link(data['data'], url=url+'tutors/{}', key='idTutors')
        # for d in data['data']:
        #     d['categories'] = self._get_category_from_ids(d['categories'].split(','))
        return data
    
    def get_tutors_by_id(self, idTutors, params=None, fields='*', url=''):
        params['idTutors'] = idTutors
        data = self.get_from_db(table='tutors', params=params, fields=fields,
                                paginate=False, url=url)
        data['data'][0]['categories'] = self._get_category_from_ids(data['data'][0]['categories'].split(','))
        return data

    def get_categories(self, params=None, fields='*', paginate=True, limit=10, offset=0, url=''):
        data = self.get_from_db(table='categories', params=params, fields=fields,
                                paginate=paginate, limit=limit, offset=offset, url=url)
        data['data'] = self._make_id_link(data['data'], url=url + 'categories/{}', key='idCategories')
        return data

    def get_categories_by_id(self, idCategories, params=None, fields='*', paginate=True, limit=10, offset=0, url=''):
        query = """
                SELECT catalog.idTutors as idTutors, name, byline, linkedin, resume, website, imageLink
                FROM catalog JOIN tutors
                ON catalog.idTutors = tutors.idTutors
                WHERE catalog.idCategories={}
            """.format(str(idCategories))
        table = 'categories/{}'.format(idCategories)
        data = self.get_from_db(table=table, q=query, params=params, fields=fields, paginate=paginate, limit=limit, offset=offset, url=url)
        data['data'] = self._make_id_link(data['data'], url=url+'tutors/{}', key='idTutors')
        return data

    def add_tutor(self, params):
        for col in self.key_columns:
            if col not in params:
                raise Exception('Tutors add must have columns {}'.format(self.key_columns))
        cursor = self.cnx.cursor()
        paramList = [(k,v) for k,v in params.items()]
        cols = ', '.join([i[0] for i in paramList])
        vals = ', '.join(['"{}"'.format(i[1]) for i in paramList])
        query = """INSERT into CatalogService.Tutors ({}) values ({})""".format(cols, vals)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        data = self.get_tutor({"username":params['username']})
        return data

    def delete_tutor(self, inp, email):
        col = "email" if email else "username"
        cursor = self.cnx.cursor()
        data = self.get_tutor({col:inp})
        if not data['data']: raise Exception('Tutor not present in database')
        query = """DELETE FROM CatalogService.Tutors WHERE {}="{}";""".format(col, inp)
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        return data

    def update_tutor(self, inp, email, params):
        col = "email" if email else "username"
        cursor = self.cnx.cursor()
        if not params: raise Exception('Please provide update params')
        query = """UPDATE CatalogService.Tutors SET {} WHERE {};""".format(self._parse_params(params,', '), self._parse_params({col:inp}))
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        data = self.get_tutor(params)
        return data


