import json
import os
import sys

from flask import Flask, Response
from flask import request
from flask import render_template

from database.tutors import tutorsDatabase
td = tutorsDatabase()

cwd = os.getcwd()
sys.path.append(cwd)

application = Flask('CatalogService')

# This function performs a basic health check. We will flesh this out.
@application.route("/", methods=["GET"])
def health_check():
    return render_template('index.html')

@application.route('/catalog')
def catalog():
    data = td.get_catalog(url=request.url_root)
    rsp = Response(json.dumps(data), status=200, content_type="application/json")
    return rsp

@application.route("/categories", methods=["GET"])
def catagories():
    params = request.args.copy()
    fields = params.get('fields', '*')
    limit, offset = int(params.get('limit', 10)), int(params.get('offset', 0))
    custParams = {k:v for k,v in params.items()}
    data = td.get_categories(params=custParams, fields=fields, limit=limit, offset=offset, url=request.url_root)
    rsp = Response(json.dumps(data), status=200, content_type="application/json")
    return rsp

@application.route("/categories/<idCategories>", methods=["GET"])
def catagories_id(idCategories):
    params = request.args.copy()
    fields = params.get('fields', '*')
    limit, offset = int(params.get('limit', 10)), int(params.get('offset', 0))
    custParams = {k:v for k,v in params.items()}
    data = td.get_categories_by_id(idCategories=idCategories, params=custParams, fields=fields, limit=limit, offset=offset, url=request.url_root)
    rsp = Response(json.dumps(data), status=200, content_type="application/json")
    return rsp

@application.route("/tutors", methods=["GET"])
def tutors():
    params = request.args.copy()
    limit, offset = int(params.get('limit', 10)), int(params.get('offset', 0))
    custParams = {k:v for k,v in params.items()}
    data = td.get_tutors(params=custParams, limit=limit, offset=offset, url=request.url_root)
    rsp = Response(json.dumps(data), status=200, content_type="application/json")
    return rsp

@application.route("/tutors/<idTutors>", methods=["GET"])
def tutors_id(idTutors):
    params = request.args.copy()
    custParams = {k:v for k,v in params.items()}
    data = td.get_tutors_by_id(idTutors=idTutors, params=custParams, url=request.url_root)
    rsp = Response(json.dumps(data), status=200, content_type="application/json")
    return rsp
# 
# @application.route("/tutors/add", methods=["GET"])
# def tutors_add():
#     params = request.args.copy()
#     try:
#         data = td.add_tutor(params=params)
#         rsp = Response(json.dumps(data), status=200, content_type="application/json")
#     except Exception as e:
#         print('Error:',e)
#         rsp = Response('Error: {}'.format(str(e)), status=400)
#     return rsp
#
# @application.route("/tutors/delete/<usrEmail>", methods=["GET"])
# def tutors_delete(usrEmail):
#     email = True if '@' in usrEmail else False
#     try:
#         data = td.delete_tutor(usrEmail,email)
#         rsp = Response(json.dumps(data), status=200, content_type="application/json")
#     except Exception as e:
#         print('Error:',e)
#         rsp = Response('Error: {}'.format(str(e)), status=400)
#     return rsp
#
# @application.route("/tutors/update/<usrEmail>", methods=["GET"])
# def tutors_update(usrEmail):
#     email = True if '@' in usrEmail else False
#     params = request.args.copy()
#     try:
#         data = td.update_tutor(usrEmail,email, params)
#         rsp = Response(json.dumps(data), status=200, content_type="application/json")
#     except Exception as e:
#         print('Error:',e)
#         rsp = Response('Error: {}'.format(str(e)), status=400)
#     return rsp

if __name__ == "__main__":
    application.run(debug=True)
