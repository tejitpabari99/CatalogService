import json
import os
import sys

from flask import Flask, Response
from flask import request
from flask import render_template

from database.database import database
from database.tutors import tutorsDatabase
from database.catalog import catalogDatabase
from database.categories import categoriesDatabase
from database.bookings import bookingsDatabase
db = database(host='catalogservice.cbufftirwvx9.us-east-2.rds.amazonaws.com', db='CatalogService', user=None, password=None)
cnx = db.cnx
tutorD = tutorsDatabase(cnx)
catalogD = catalogDatabase(cnx)
categoriesD = categoriesDatabase(cnx)
bookingsD = bookingsDatabase(cnx)

cwd = os.getcwd()
sys.path.append(cwd)

application = Flask('CatalogService')

def response400(e):
    return Response('Error: {}'.format(str(e)), status=400)

# This function performs a basic health check. We will flesh this out.
@application.route("/", methods=["GET"])
def health_check():
    return render_template('index.html')

@application.route('/catalog')
def catalog():
    try:
        data = catalogD.get_catalog(url=request.url_root)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

@application.route("/categories", methods=["GET"])
def catagories():
    try:
        data = categoriesD.get_categories(params=request.args, url=request.url_root)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

@application.route("/categories/<idCategories>", methods=["GET"])
def catagories_id(idCategories):
    try:
        data = categoriesD.get_categories_by_id(idCategories=idCategories, params=request.args, url=request.url_root)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

@application.route("/tutors", methods=["GET"])
def tutors():
    try:
        data = tutorD.get_tutors(params=request.args, url=request.url_root)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

@application.route("/tutors/<idTutors>", methods=["GET"])
def tutors_id(idTutors):
    try:
        data = tutorD.get_tutors_by_id(idTutors=idTutors, url=request.url_root)
        data['links'] = {'bookings': request.url_root+'tutors/'+str(idTutors)+'/bookings',
                         'book': request.url_root + 'tutors/' + str(idTutors) + '/book',
                         'comments': request.url_root+'tutors/'+str(idTutors)+'/comments'}
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

@application.route("/tutors/add", methods=["POST"])
def tutors_add():
    try:
        data = tutorD.add_tutor(params=request.json)
        rsp = response400('Error in data addition')
        if data: rsp = Response('Added', status=200, content_type="application/txt")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

@application.route("/tutors/<idTutors>/delete", methods=["POST"])
def tutors_delete(idTutors):
    try:
        data = tutorD.delete_tutor(idTutors)
        rsp = response400('Error in data deletion')
        if data: rsp = Response('Deleted', status=200, content_type="application/txt")
    except Exception as e:
        print('Error:',e)
        rsp = response400(e)
    return rsp

@application.route("/tutors/<idTutors>/update", methods=["POST"])
def tutors_update(idTutors):
    try:
        data = tutorD.update_tutor(idTutors, params=request.json, url=request.url_root)
        rsp = response400('Error in data update')
        if data: rsp = Response('Updated', status=200, content_type="application/txt")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

@application.route("/tutors/<idTutors>/bookings", methods=["GET"])
def tutors_bookings(idTutors):
    try:
        data = bookingsD.get_bookings(idTutors=idTutors, params=request.args, url=request.url_root)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

@application.route("/tutors/<idTutors>/bookings/<idBookings>", methods=["GET"])
def tutors_bookings_id(idTutors,idBookings):
    try:
        data = bookingsD.get_bookings_id(idBookings=idBookings, idTutors=idTutors, params=request.args, url=request.url_root)
        rsp = Response(json.dumps(data), status=200, content_type="application/json")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp
#
# @application.route("/tutors/<idTutors>/bookings/<idBookings>/approve", methods=["GET"])
# def tutors_bookings_id_approve(idTutors,idBookings):
#     try:
#         data = bookingsD.approve_bookings(idBookings=idBookings, idTutors=idTutors, url=request.url_root)
#         rsp = Response(json.dumps(data), status=200, content_type="application/json")
#     except Exception as e:
#         print('Error:', e)
#         rsp = response400(e)
#     return rsp
#
# @application.route("/tutors/<idTutors>/bookings/<idBookings>/reject", methods=["GET"])
# def tutors_bookings_id_reject(idTutors,idBookings):
#     try:
#         data = bookingsD.reject_bookings(idBookings=idBookings, idTutors=idTutors, url=request.url_root)
#         rsp = Response(json.dumps(data), status=200, content_type="application/json")
#     except Exception as e:
#         print('Error:', e)
#         rsp = response400(e)
#     return rsp

@application.route("/tutors/<idTutors>/book", methods=["POST"])
def tutors_book(idTutors):
    try:
        data = bookingsD.add_bookings(idTutors, params=request.json)
        rsp = response400('Error in data addition')
        if data: rsp = Response('Booking Added. The tutor will reply with an email confirmation.', status=200, content_type="application/txt")
    except Exception as e:
        print('Error:', e)
        rsp = response400(e)
    return rsp

if __name__ == "__main__":
    application.run(debug=True)
