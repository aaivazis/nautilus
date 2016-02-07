# external imports
import graphene
from flask_graphql import GraphQLView, GraphQL
from graphene.contrib.sqlalchemy import SQLAlchemyObjectType
# local imports
from nautilus.api.fields import Connection
from nautilus.api.filter import args_for_model, filter_model
from nautilus.network.registry import service_location_from_name
from nautilus.network import query_graphql_service
from nautilus.conventions import root_query_for_model_service

def init_service(service, schema):
    """ Add GraphQL support to the given Flask app """
    # add default graphql endpoints
    GraphQL(service.app, schema=schema)
    # add the index query per service agreement
    service.app.add_url_rule('/', view_func=GraphQLView.as_view('index', schema=schema))


def create_model_schema(Model):
    """ This function creates a graphql schema that provides a single model """

    from nautilus import db

    # create the schema instance
    schema = graphene.Schema(
        session = db.session,
        auto_camelcase = False
    )

    # create a graphene object registered with the schema
    @schema.register
    class ModelObjectType(SQLAlchemyObjectType):
        class Meta:
            model = Model

    class Query(graphene.ObjectType):
        """ the root level query """
        all_models = Connection(ModelObjectType,
            args = args_for_model(Model)
        )

        def resolve_all_models(self, args, info):
            # filter the model query according to the arguments
            return filter_model(Model, args)


    # add the query to the schema
    schema.query = Query

    return schema


def query_model_service(service, fields, filters = {}):
    ''' This function performs a query against a registered model service '''
    # todo: go through nginx reverse proxy (service proxy service)
    # get the location for the appropriate service
    location = "http://{}".format(service_location_from_name(service))

    # query the location using model service conventions
    return query_graphql_service(
        url = location,
        name = root_query_for_model_service(service),
        filters = filters,
        fields = fields,
    )
