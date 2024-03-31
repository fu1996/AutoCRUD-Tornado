# 新模型的control处理的逻辑
import asyncio
from typing import Dict, Optional

from playhouse.shortcuts import model_to_dict

from server.control.base_control import BaseControl
from server.db_manager import db_manager
from server.model.todo_item import TodoItem, TodoItemPydantic


class TodoItemControl(BaseControl):

    async def create_one(self, **kwargs) -> TodoItemPydantic:
        data = await db_manager.create(TodoItem, **kwargs)
        return TodoItemPydantic(**model_to_dict(data))

    async def get_one_by_id(self, item_id) -> Optional[Dict[str, str]]:
        res = await db_manager.get_or_none(TodoItem.select().where(TodoItem.id == item_id))
        if not res:
            return None
        serializer_data = BaseControl.serializer(res)
        return serializer_data

    async def update_one_by_id(self, item_id, **kwargs) -> Optional[Dict[str, str]]:
        query = TodoItem.update(**kwargs).where(TodoItem.id == item_id)
        return await db_manager.execute(query)

    async def delete_one_by_id(self, item_id) -> Optional[Dict[str, str]]:
        query = TodoItem.soft_delete().where(TodoItem.id == item_id)
        return await db_manager.execute(query)

    async def delete_by_ids(self, ids=None):
        if ids is None:
            ids = []
        query = TodoItem.soft_delete().where(TodoItem.id.in_(ids))
        return await db_manager.execute(query)

    async def get_page_table(self, page, per_page, id, title, user_id):
        search_query = TodoItem.is_deleted == 0
        if id:
            search_query &= (TodoItem.id == id)
        if not id:
            if title:
                search_query &= (TodoItem.title.contains(title))
            if user_id:
                search_query &= (TodoItem.user_id == user_id)

        res = await asyncio.gather(
            db_manager.execute(
                TodoItem.select().where(search_query).paginate(page=page, paginate_by=per_page)),
            db_manager.count(TodoItem.select().where(search_query)),
        )
        serializer_list = BaseControl.serializer_list(res[0])
        list_data = {
            "rows": serializer_list,
            "count": res[1]
        }
        return list_data