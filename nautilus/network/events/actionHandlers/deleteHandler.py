# local imports
from nautilus.conventions.actions import get_crud_action, change_action_status
from nautilus.models.serializers import ModelSerializer

def delete_handler(Model):
    """
        This factory returns an action handler that deletes a new instance of
        the specified model when a delete action is recieved, assuming the
        action follows nautilus convetions.

        Args:
            Model (nautilus.BaseModel): The model to delete when the action
                received.

        Returns:
            function(type, payload): The action handler for this model
    """
    # necessary imports
    from nautilus.database import db

    async def action_handler(service, action_type, payload, notify=True, **kwds):
        # if the payload represents a new instance of `model`
        if action_type == get_crud_action('delete', Model):
            try:
                # get the model matching the payload
                model_query = Model.select().where(Model.primary_key() == payload)
                # remove the model instance
                model_query.get().delete_instance()

                # if we need to tell someone about what happened
                if notify:
                    # publish the success event
                    await service.event_broker.send(
                        body=payload,
                        action_type=change_action_status(action_type, 'success')
                    )

            # if something goes wrong
            except Exception as err:
                # if we need to tell someone about what happened
                if notify:
                    # publish the error as an event
                    await service.event_broker.send(
                        body=str(err),
                        action_type=change_action_status(action_type, 'error')
                    )
                # otherwise we aren't supposed to notify
                else:
                    # raise the exception normally
                    raise err


    # return the handler
    return action_handler
