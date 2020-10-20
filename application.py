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

@application.route("/tutors", methods=["GET"])
def tutors():
    params = request.args
    fields = params.get('fields','*')
    data = td.get_all_tutors_data(params=params, fields=fields)
    rsp = Response(json.dumps(data), status=200, content_type="application/json")
    return rsp

@application.route("/tutors/add", methods=["GET"])
def tutors_add():
    params = request.args
    try:
        data = td.add_tutor(params=params)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:',e)
        rsp = Response('Error: {}'.format(str(e)), status=400)
    return rsp

if __name__ == "__main__":
    application.run(debug=True)
