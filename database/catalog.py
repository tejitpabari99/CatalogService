import json
import pandas as pd

from database.database import database
from database.functions import _parse_params, _paginateDict, _make_id_link


class catalogDatabase(object):
    def __init__(self, cnx=None, host='catalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService',
                 user=None, password=None, key_columns=None, notIncludedCols=None):
        self.cnx = cnx
        if not cnx:
            db = database(host=host, db=db, user=user, password=password)
            self.cnx = db.cnx
        self.key_columns, self.notIncludedCols = key_columns, notIncludedCols
        if not notIncludedCols: self.notIncludedCols = ['fields', 'limit', 'offset']

        self.category_ids = [1, 2, 3, 4, 5]

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
        data = {'data': []}
        for i, (name, group) in enumerate(pd.DataFrame(resp).groupby('category')):
            catID = group['idCategories'].iloc[0]
            data['data'].append({
                'category': name,
                'data': _make_id_link(json.loads(group.head(tutors_per_cat).to_json(orient='records')),
                                      url=url + 'tutors/{}', key='idTutors'),
                'links': [
                    {'categories': url + 'categories/{}'.format(catID)}
                ]

            })
        cursor.close()
        json.dump(data, open('data.json', 'w'), indent=2)
        return data
