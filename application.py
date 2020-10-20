import json
import os
import sys
import platform
import socket

from datetime import datetime

from flask import Flask, Response
from flask import request
from flask import render_template


cwd = os.getcwd()
sys.path.append(cwd)

application = Flask('CatalogService')

# This function performs a basic health check. We will flesh this out.
@application.route("/", methods=["GET"])
def health_check():
    return render_template('index.html')

@application.route("/tutors", methods=["GET"])
def tutors():
    tutorDict = {
        'Tutor Name': 'Tejit'
    }
    rsp = Response(json.dumps(tutorDict), status=200, content_type="application/json")
    return rsp

if __name__ == "__main__":
    application.run(debug=True)
