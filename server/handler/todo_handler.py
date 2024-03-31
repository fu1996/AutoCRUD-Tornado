# 新模型的handler处理的逻辑
from server.control.todo_item_control import TodoItemControl
from server.handler.base_handler import BaseHandler


class TodoItemsHandler(BaseHandler):

    async def get(self):
        todo_control = TodoItemControl()
        page = self.get_argument("page", 1)
        per_page = self.get_argument("perPage", 10)
        params = self.get_all_argument
        data = await todo_control.get_page_table(page=int(page), per_page=int(per_page), id=params.get("id"),
                                                 title=params.get("title"), user_id=params.get("user_id"))
        self.success(data)

    async def post(self):
        todo_control = TodoItemControl()
        res = await todo_control.create_one(**self.json_data)
        self.success(res.id)

    async def delete(self):
        ids = self.get_query_argument("id")
        id_list = ids.split(",")
        todo_control = TodoItemControl()
        res = await todo_control.delete_by_ids(id_list)
        self.success("ok")


class TodoItemHandler(BaseHandler):

    async def put(self, id):
        todo_control = TodoItemControl()
        res = await todo_control.update_one_by_id(id, **self.json_data)
        self.success("ok")

    async def delete(self, id):
        todo_control = TodoItemControl()
        res = await todo_control.delete_one_by_id(id)
        self.success("ok")