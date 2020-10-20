import pymysql.cursors
import os

class tutorsDatabase(object):
    def __init__(self, host='cccatalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService',
                 user=None, password=None, key_columns = None):
        if not user: user = os.getenv('dbuser','admin')
        if not password: password = os.getenv('dbpass','adminpass')
        self.key_columns = key_columns
        if not key_columns: self.key_columns = ['username', 'name', 'email']

        self.cnx =  pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    def get_all_tutors_data(self, params = None, fields = '*'):
        cursor = self.cnx.cursor()
        # if fields != '*':
        #     fields = ', '.join(['"{}"'.format(f) for f in fields.split(',')])
        query = """Select {} from CatalogService.Tutors""".format(fields)
        if params:
            paramsList = ['{}="{}"'.format(k,v) for k,v in params.items() if k!='fields']
            query += """\nwhere {}""".format(' and '.join(paramsList))
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()
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
        data = cursor.fetchall()
        cursor.close()
        return data


