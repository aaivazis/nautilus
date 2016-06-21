# local imports
from nautilus.api import create_model_schema
from nautilus.network.events import combine_action_handlers
from nautilus.network.events.actionHandlers import noop_handler
from nautilus.conventions.services import connection_service_name
from nautilus.conventions.actions import get_crud_action
from .modelService import ModelService
from nautilus.models.util import create_connection_model


class ConnectionService(ModelService):
    """
        This service manages a "one-way" connection between two services.
        The underlying schema and database are automatically generated to
        match the primary keys of the linked services.

        This service will listen for actions indicating the deletion of a related
        model and remove any related fields to maintain consistency. And provides
        a way for the api gateway to deduce the relationship between services when
        summarizing the cloud.

        Args:
            services (list of nautilus.Service): The list of services to connect.

        Example:

            .. code-block:: python

                # external imports
                import nautilus

                # the services to connect
                from local.directory import service as service_one
                from other.local.directory import service as service_two

                class ServiceConfig:
                    database_url = 'sqlite:////tmp/connections.db'

                class MyConnection(nautilus.ConnectionService):
                    config = ServiceConfig

                    from_service = service_one
                    to_service = service_two

    """

    from_service = None
    to_service = None


    def __init__(self, **kwargs):

        # if there is no to service
        if not self.to_service:
            raise ValueError("Please provide a 'to_service'.")

        # if there is no to service
        if not self.from_service:
            raise ValueError("Please provide a 'from_service'.")

        # the models of each service
        self._service_models = [
            self.from_service.model, self.to_service.model
        ]

        # make sure there is a unique name for every service
        if len({model.model_name for model in self._service_models}) \
               != len(self._service_models):
            raise ValueError("Can only connect models with different name")

        # create the service
        super().__init__(
            model=create_connection_model(self._service_models),
            name=connection_service_name(*self._service_models),
            **kwargs
        )


    @property
    def action_handler(service):

        class ConnectionActionHandler(super().action_handler):
            async def handle_action(self, action_type, payload):
                # a connection service should listen for deletes on linked services
                # connected_action_handlers = [self._create_linked_handler(model)
                #                              for model in self._service_models]

                # bubble up
                await super().handle_action(action_type, payload)

                # for each model we care about
                for model in service._service_models:
                    # TODO: make this only happen once (not on every action)
                    # create the appropriate action handler
                    handler = service._create_linked_handler(model)
                    # call the handler
                    await handler(action_type, payload)

        return ConnectionActionHandler


    def _create_linked_handler(self, model):
        # the related action type
        related_action_type = get_crud_action('delete', model, status='success')
        # the action handler
        async def action_handler(action_type, payload):
            """
                an action handler to remove related entries in the
                connection db.
            """
            # if the action designates a successful delete of the model
            if action_type == related_action_type:
                # the id of the deleted model
                related_id = payload['id']
                # the query for matching fields
                matching_records = getattr(self.model, model.model_name.lower()) == related_id
                # find the matching records
                self.model.delete().where(matching_records).execute()


        # pass the action handler
        return action_handler



    def get_base_models(self):
        """
            Returns the models managed by this service.

            Returns:
                (list): the models managed by the service
        """
        return self._service_models
