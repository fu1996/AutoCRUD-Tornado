import json

from playhouse.shortcuts import model_to_dict

from server.util import DateTimeEncoder


class BaseControl(object):
    """
    Base class for control
    TODO：db_manager 已经提供了 很多的能力了，这里考虑是否要再封装一层 --by:fjk
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    @staticmethod
    def serializer(model_data):
        dict_data = model_to_dict(model_data)
        return json.loads(json.dumps(dict_data, cls=DateTimeEncoder))

    @staticmethod
    def serializer_list(model_datas):
        data = [BaseControl.serializer(model_data) for model_data in model_datas]
        return data

    #
    # def __init__(self, model_cls):
    #     self.model_cls = model_cls
    #
    # async def create_one(self, **kwargs):
    #     res = await db_manager.create(self.model_cls, **kwargs)
    #     return res
