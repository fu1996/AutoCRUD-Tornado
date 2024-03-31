import json
from datetime import datetime


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        if isinstance(obj, bytes):
            return str(obj, 'utf-8')
        return json.JSONEncoder.default(self, obj)

