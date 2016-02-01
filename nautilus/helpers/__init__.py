from flask.ext.jsontools import DynamicJSONEncoder

class JSONEncoder(DynamicJSONEncoder):
    def default(self, o):
        # Custom formats
        if isinstance(o, datetime.datetime):
            return o.isoformat(' ')
        if isinstance(o, datetime.date):
            return o.isoformat()
        if isinstance(o, set):
            return list(o)

        # Fallback
        return super(DynamicJSONEncoder, self).default(o)