import pymysql.cursors
import os

class database(object):
    def __init__(self,host='catalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService',
                 user=None, password=None):
        if not user: user = os.getenv('dbuser','admin')
        if not password: password = os.getenv('dbpass','adminpass')
        self.cnx = pymysql.connect(host=host,
                                   user=user,
                                   password=password,
                                   db=db,
                                   charset='utf8mb4',
                                   cursorclass=pymysql.cursors.DictCursor)
