```python
# 新模型的路由定义
(r"/api/todo_items", TodoItemsHandler),
(r"/api/todo_item/(\d+)", TodoItemHandler),

```

```python
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

```

```python
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

```

```json
# 新模型的列表的json定义
{
  "title": "TODO事项管理",
  "remark": "事项列表",
  "name": "todo_item_CRUD",
  "headerToolbar": [
    {
      "type": "button",
      "actionType": "dialog",
      "label": "新增",
      "icon": "fa fa-plus pull-left",
      "primary": true,
      "dialog": {
        "title": "新增",
        "body": {
          "type": "form",
          "name": "sample-edit-form",
          "api": "post:${API_HOST}/api/todo_items",
          "body": [
            {
              "type": "input-text",
              "name": "title",
              "label": "标题",
              "required": true
            },
            {
              "type": "divider"
            },
            {
              "type": "input-text",
              "name": "description",
              "label": "描述"
            },
            {
              "type": "divider"
            },
            {
              "type": "input-checkbox",
              "name": "completed",
              "label": "是否完成",
              "required": true
            },
            {
              "type": "divider"
            },
            {
              "type": "input-text",
              "name": "user_id",
              "label": "用户ID",
              "required": true
            }
          ]
        }
      }
    }
  ],
  "body": {
    "type": "crud",
    "api": "/api/todo_items",
    "keepItemSelectionOnPageChange": true,
    "maxKeepItemSelectionLength": 11,
    "autoFillHeight": true,
    "syncLocation": false,
    "labelTpl": "${id} ${title}",
    "autoGenerateFilter": true,
    "placeholder": "暂无数据",
    "bulkActions": [
      {
        "label": "批量删除",
        "actionType": "ajax",
        "api": "delete:${API_HOST}/api/todo_items?id=${ids|raw}",
        "confirmText": "确定要批量删除?"
      }
    ],
    "quickSaveApi": "${API_HOST}/amis/api/sample/bulkUpdate",
    "quickSaveItemApi": "${API_HOST}/amis/api/sample/$id",
    "filterTogglable": true,
    "headerToolbar": [
      "bulkActions",
      {
        "type": "tpl",
        "tpl": "当前共有 ${count} 个事项",
        "className": "v-middle"
      },
      {
        "type": "columns-toggler",
        "align": "right"
      },
      {
        "type": "button",
        "actionType": "dialog",
        "label": "新增",
        "icon": "fa fa-plus pull-left",
        "primary": true,
        "align": "right",
        "dialog": {
          "title": "新增",
          "body": {
            "type": "form",
            "name": "sample-edit-form",
            "api": "post:${API_HOST}/api/todo_items",
            "body": [
              {
                "type": "input-text",
                "name": "title",
                "label": "标题",
                "required": true
              },
              {
                "type": "divider"
              },
              {
                "type": "input-text",
                "name": "description",
                "label": "描述"
              },
              {
                "type": "divider"
              },
              {
                "type": "input-checkbox",
                "name": "completed",
                "label": "是否完成",
                "required": true
              },
              {
                "type": "divider"
              },
              {
                "type": "input-text",
                "name": "user_id",
                "label": "用户ID",
                "required": true
              }
            ]
          }
        }
      }
    ],
    "footerToolbar": [
      "statistics",
      {
        "type": "pagination",
        "layout": "perPage,pager,go"
      }
    ],
    "columns": [
      {
        "name": "id",
        "label": "ID",
        "width": 20,
        "sortable": true,
        "searchable": {
          "type": "input-text",
          "name": "id",
          "label": "主键",
          "placeholder": "输入id"
        },
        "fixed": "left"
      },
      {
        "name": "title",
        "label": "标题",
        "sortable": true,
        "searchable": {
          "type": "input-text",
          "name": "title",
          "label": "标题",
          "placeholder": "输入标题",
          "mode": "horizontal"
        }
      },
      {
        "name": "description",
        "label": "描述",
        "sortable": true
      },
      {
        "name": "completed",
        "label": "是否完成",
        "sortable": true
      },
      {
        "name": "user_id",
        "label": "用户ID",
        "sortable": true
      },
      {
        "type": "operation",
        "label": "操作",
        "width": 100,
        "buttons": [
          {
            "type": "button",
            "icon": "fa fa-eye",
            "actionType": "dialog",
            "tooltip": "查看",
            "dialog": {
              "title": "查看",
              "body": {
                "type": "form",
                "submitText": "",
                "body": [
                  {
                    "type": "input-text",
                    "name": "title",
                    "label": "标题",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "description",
                    "label": "描述"
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-checkbox",
                    "name": "completed",
                    "label": "是否完成",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "user_id",
                    "label": "用户ID",
                    "required": true
                  }
                ]
              }
            }
          },
          {
            "type": "button",
            "icon": "fa fa-pencil",
            "tooltip": "编辑",
            "actionType": "drawer",
            "drawer": {
              "position": "right",
              "size": "lg",
              "title": "编辑",
              "body": {
                "type": "form",
                "name": "sample-edit-form",
                "api": "put:${API_HOST}/api/todo_item/$id",
                "body": [
                  {
                    "type": "input-text",
                    "name": "title",
                    "label": "标题",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "description",
                    "label": "描述"
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-checkbox",
                    "name": "completed",
                    "label": "是否完成",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "user_id",
                    "label": "用户ID",
                    "required": true
                  }
                ]
              }
            }
          },
          {
            "type": "button",
            "icon": "fa fa-times text-danger",
            "actionType": "ajax",
            "tooltip": "删除",
            "confirmText": "您确认要删除?",
            "api": "delete:${API_HOST}/api/todo_item/$id"
          }
        ],
        "toggled": true
      }
    ]
  }
}

```

```json
# 新模型的新增单个项的json定义
{
  "type": "page",
  "title": "新增",
  "remark": null,
  "toolbar": [
    {
      "type": "button",
      "actionType": "link",
      "link": "/todo_item/list",
      "label": "返回列表"
    }
  ],
  "body": {
    "type": "form",
    "name": "sample-edit-form",
    "api": "post:${API_HOST}/api/todo_items",
    "body": [
      {
        "type": "input-text",
        "name": "title",
        "label": "标题",
        "required": true
      },
      {
        "type": "divider"
      },
      {
        "type": "input-text",
        "name": "description",
        "label": "描述"
      },
      {
        "type": "divider"
      },
      {
        "type": "input-checkbox",
        "name": "completed",
        "label": "是否完成",
        "required": true
      },
      {
        "type": "divider"
      },
      {
        "type": "input-text",
        "name": "user_id",
        "label": "用户ID",
        "required": true
      }
    ]
  }
}

```