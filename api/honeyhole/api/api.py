from flask import Blueprint
from flask_restx import Api


blueprint = Blueprint("api", __name__)


api = Api(
    blueprint,
    title="MyToob Core API",
    version="1.0",
    description="API for managing MyToob Movies"
)

from . resources.trip import ns_trips

api.add_namespace(ns_trips)
