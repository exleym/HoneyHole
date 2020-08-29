from flask_accepts import accepts, responds
from flask_restx import Resource
from flask_filter.schemas import vali1date_operator
import marshmallow as ma

import logging
from . import queries as queries
from .. util import default_list_parser

logger = logging.getLogger(__name__)


class PostFilterSchema(ma.Schema):
    field = ma.fields.String(required=True, allow_none=False)
    op = ma.fields.String(required=True, attribute="OP", validate=vali1date_operator)
    value = ma.fields.Raw(required=True, allow_none=False)


class SearchSchema(ma.Schema):
    filters = ma.fields.List(ma.fields.Nested(PostFilterSchema))


def generate_collection(api, namespace, db, Schema, Model,
                        resource_name: str = None, order_by = None) -> type(Resource):
    resource_name = resource_name or Schema.__name__.replace("Schema", "")
    schema = Schema()
    order_by = order_by or Model.id

    @namespace.route("")
    class Collection(Resource):
        parser = default_list_parser(namespace=namespace)

        @accepts(dict(name="limit", type=int), dict(name="offset", type=int), api=api)
        @responds(schema=Schema(many=True), status_code=200, api=api)
        def get(self):
            args = self.parser.parse_args()
            return queries.list_resources(Model, order_by=order_by, **args)

        @accepts(schema=Schema, api=api)
        @responds(resource_name, schema=Schema, api=api, status_code=201)
        def post(self):
            data = schema.load(namespace.payload)
            obj = Model(**data)
            db.session.add(obj)
            db.session.commit()
            return obj

    return Collection


def generate_resource_manager(api, namespace, Schema, Model, resource_name: str = None) -> type(Resource):

    resource_name = resource_name or Schema.__name__.replace("Schema", "")
    schema = Schema()

    @namespace.route("/<int:id>")
    @namespace.response(404, f"{resource_name} not found")
    @namespace.param("id", f"The {resource_name} identifier")
    class ResourceManager(Resource):
        @namespace.doc(f"get {resource_name} by id")
        @responds(schema=Schema, api=api)
        def get(self, id: int):
            x = queries.get_resource(id, Model)
            return x

        @namespace.doc(f"update {resource_name}")
        @accepts(schema=Schema, api=api)
        @responds(schema=Schema, api=api)
        def put(self, id: int):
            object_id = namespace.payload.pop("id", id)
            if object_id != id:
                raise ValueError(f"If you PUT a full object with an 'id' field, it "
                                 f"must match the 'id' you supply in the path. You "
                                 f"sent path id = {id} and object id = {object_id}.")
            data = schema.load(namespace.payload, partial=True)
            return queries.edit_resource(id, data, Model)

        @namespace.doc(f"delete {resource_name}")
        @responds("", 204, api=api)
        def delete(self, id: int):
            queries.remove_resource_by_id(id, Model)
            return ""

    return ResourceManager


def generate_search_manager(api, namespace, Schema, Model, filtr, resource_name: str = None) -> type(Resource):
    resource_name = resource_name or Schema.__name__.replace("Schema", "")
    schema = Schema()

    @namespace.route("/search")
    class ResourceSearch(Resource):

        @namespace.doc(f"execute a resource search for {resource_name}")
        @accepts(schema=SearchSchema, api=api)
        @responds(schema=Schema(many=True), status_code=200, api=api)
        def post(self):
            filters = namespace.payload.get("filters")
            return filtr.search(
                DbModel=Model,
                filters=filters,
                ModelSchema=schema
            )

    return ResourceSearch


def generate_standard_endpoints(api, namespace, Schema, Model, db, filtr,
                                resource_name: str = None, order_by = None):
    generate_collection(
        api=api,
        namespace=namespace,
        db=db,
        Schema=Schema,
        Model=Model,
        resource_name=resource_name,
        order_by=order_by
    )
    generate_resource_manager(
        api=api,
        namespace=namespace,
        Schema=Schema,
        Model=Model,
        resource_name=resource_name
    )
    generate_search_manager(
        api=api,
        namespace=namespace,
        Schema=Schema,
        Model=Model,
        filtr=filtr,
        resource_name=resource_name
    )
