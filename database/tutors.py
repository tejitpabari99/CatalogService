import pymysql.cursors
import os

class tutorsDatabase(object):
    def __init__(self, host='cccatalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService',
                 user=None, password=None, key_columns = None, notIncludedCols = None):
        if not user: user = os.getenv('dbuser','admin')
        if not password: password = os.getenv('dbpass','adminpass')
        self.key_columns, self.notIncludedCols = key_columns, notIncludedCols
        if not key_columns: self.key_columns = ['username', 'name', 'email']
        if not notIncludedCols: self.notIncludedCols = ['fields', 'limit']

        self.cnx =  pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    def parse_params(self, params=None, joinTerm=' and ', quote=True):
        if not params: return ''
        paramsList = ['{}="{}"'.format(k, v) if quote else '{}={}'.format(k, v)
                      for k, v in params.items() if k not in self.notIncludedCols]
        return joinTerm.join(paramsList)

    def paginate(self, link, params=None, currPage=1, nextPage=True, limit=10):
        params['limit']=limit
        paramsStr = '' if not params else self.parse_params(params,'&', quote=False)
        currStr = link.format(currPage)
        prevStr = link.format(currPage-1) if currPage-1>0 else None
        nextStr = link.format(currPage+1) if nextPage else None
        return {
            'currPage': currStr+'?'+paramsStr,
            'prevPage': None if prevStr is None else prevStr+'?'+paramsStr,
            'nextPage': None if nextStr is None else nextStr+'?'+paramsStr,
        }

    def get_tutor(self, params = None, fields = '*', paginate=False, page=1, limit=10, url=''):
        cursor = self.cnx.cursor()
        offset = (page - 1) * limit
        # if fields != '*':
        #     fields = ', '.join(['"{}"'.format(f) for f in fields.split(',')])
        query = """Select {} from CatalogService.Tutors""".format(fields)
        paramsStr = self.parse_params(params, ' and ')
        if paramsStr: query += """\nwhere {}""".format(paramsStr)
        if paginate: query += """\nlimit {}, {}""".format(offset,limit)
        cursor.execute(query)
        data = {'data':cursor.fetchall()}
        cursor.close()
        if paginate and data:
            nextPage = len(data['data'])>0
            data['paginate'] = self.paginate(url+'tutors/page/{}', params=params,
                                             currPage=page, nextPage=nextPage, limit=limit)
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
        query = """UPDATE CatalogService.Tutors SET {} WHERE {};""".format(self.parse_params(params,', '), self.parse_params({col:inp}))
        cursor.execute(query)
        self.cnx.commit()
        cursor.close()
        data = self.get_tutor(params)
        return data


