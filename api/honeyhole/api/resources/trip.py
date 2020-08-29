import datetime as dt
from flask_restx import Namespace
import marshmallow as ma
from .. autocrud import generate_standard_endpoints
from ... extensions import db, filtr
from .. api import api


ns_trips = Namespace("trips", description="Fishing Trips")


class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    location_id = db.Column(db.Integer)
    surface_temperature = db.Column(db.Float)
    water_clarity = db.Column(db.Float)
    wind = db.Column(db.Float)
    barometric_pressure = db.Column(db.Float)

    def duration(self):
        return (self.end_time - self.start_time).hours


class TripSchema(ma.Schema):
    id = ma.fields.Integer(dump_only=True)
    startTime = ma.fields.DateTime(attribute="start_time")
    endTime = ma.fields.DateTime(attribute="end_time")
    locationId = ma.fields.Integer(load_only=True, attribute="location_id")
    surfaceTemperature = ma.fields.Float(attribute="surface_temperature")
    waterClarity = ma.fields.Float(attribute="water_clarity")
    wind = ma.fields.Float()
    barometricPressure = ma.fields.Float(attribute="barometric_pressure")



generate_standard_endpoints(
    api=api,
    namespace=ns_trips,
    Schema=TripSchema,
    Model=Trip,
    db=db,
    filtr=filtr,
    order_by=Trip.start_time
)