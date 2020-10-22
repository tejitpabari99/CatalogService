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

@application.route('/tutors', defaults={'page':1})
@application.route("/tutors/page/<int:page>", methods=["GET"])
def tutors(page):
    params = request.args.copy()
    fields = params.get('fields','*')
    limit = params.get('limit',10)
    data = td.get_tutor(params=params, fields=fields, paginate=True, page=page, limit=limit, url=request.url_root)
    rsp = Response(json.dumps(data), status=200, content_type="application/json")
    return rsp

@application.route("/tutors/profile/<username>", methods=["GET"])
def tutors_by_username(username):
    params = request.args.copy()
    fields = params.get('fields','*')
    custParams = {k:v for k,v in params.items()}
    custParams['username']=username
    data = td.get_tutor(params=custParams, fields=fields)
    rsp = Response(json.dumps(data), status=200, content_type="application/json")
    return rsp

@application.route("/tutors/add", methods=["GET"])
def tutors_add():
    params = request.args.copy()
    try:
        data = td.add_tutor(params=params)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:',e)
        rsp = Response('Error: {}'.format(str(e)), status=400)
    return rsp

@application.route("/tutors/delete/<usrEmail>", methods=["GET"])
def tutors_delete(usrEmail):
    email = True if '@' in usrEmail else False
    try:
        data = td.delete_tutor(usrEmail,email)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:',e)
        rsp = Response('Error: {}'.format(str(e)), status=400)
    return rsp

@application.route("/tutors/update/<usrEmail>", methods=["GET"])
def tutors_update(usrEmail):
    email = True if '@' in usrEmail else False
    params = request.args.copy()
    try:
        data = td.update_tutor(usrEmail,email, params)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:',e)
        rsp = Response('Error: {}'.format(str(e)), status=400)
    return rsp

if __name__ == "__main__":
    application.run(debug=True)
