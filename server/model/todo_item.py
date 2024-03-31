from peewee import *

from server.model.base_model import BaseDBModel, BasePydanticModel

class TodoItemPydantic(BasePydanticModel):
    title: str
    description: str
    completed: bool
    user_id: int

class TodoItem(BaseDBModel):
    title = CharField(max_length=255, null=False, verbose_name='标题')
    description = TextField(null=True, verbose_name='描述')
    completed = BooleanField(default=False, verbose_name='是否完成')
    user_id = IntegerField(null=False, verbose_name='用户ID')

    class Meta:
        db_table = 'todo_item'
        verbose_name = 'TODO事项表'