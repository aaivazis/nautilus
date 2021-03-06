Keeping Track of Data
======================

Handling persistent data is a common task of any web application, wether
it's user's passwords or their horde of cat photos. In a nautilus application,
each piece of data is maintained by a sepecialized service known as a "model
service". The definition of a model service begins with the specification of
the underlying model. Like services, this is done by defining a python class.
Create a file called catPhoto.py and paste the following code:


.. code-block:: python

    from nautilus import models
    from nautilus.models import fields

    class CatPhoto(models.BaseModel):
        photo_location = fields.CharField()


This defines the underlying database table for our service. Once the model is
defined, creating a service to manage the data is relatively easy:


.. code-block:: python

    import nautilus
    from nautilus import models
    from nautilus.models import fields


    class CatPhoto(models.BaseModel):
        photo_location = fields.CharField()


    class ServiceConfig:
        database_url = 'sqlite:///catPhotos.db'

    class CatPhotoService(nautilus.ModelService):
        model = CatPhoto
        config = ServiceConfig


Before we can interact with the service we just made, let's create a local database
so we can store our records somewhere:


.. code-block:: bash

    $ python3 ./models.py syncdb


Querying for data
------------------

You should now see a file called ``nautilus.db`` in your directory. Run the model service
by executing ``python3 ./catPhoto.py runserver`` and navigate to
``http://localhost:8000/graphiql`` (notice the i).

Model services automatically generate a graphql (no i) api for the model.
Graphiql (with i) is a standard user interface for interacting with these sorts
APIs. For more information on graphql visit
`here <https://facebook.github.io/react/blog/2015/05/01/graphql-introduction.html>`_.
Try creating a cat photo record with a ``photo_location`` of "foo" in the
database either via the ``sqlite`` cli or an app like `SQLiteBrowser <https://github.com/sqlitebrowser/sqlitebrowser>`_.

Once you've done that, try executing the following query by entering it in the left panel
of `graphiql`:

.. code-block:: graphql

    {
        all_models {
            photo_location
        }
    }

You should see a json reply that looks like:

.. code-block:: json

    {
        "data": [{
            "photo_location": "foo"
        }],
        "errors": []
    }

It's useful to know that you can have graphiql provide an auto-complete by pressing
``alt+space`` allowing you to discover availble queries, fields, and mutations
without looking at a single line of source code! Give it a try.

In the next section you'll learn about how Nautilus helps you join data across
services to create very powerful applications out of highly reusable parts.

