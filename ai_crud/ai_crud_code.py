from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import OpenAI, ChatOpenAI

OpenAILLM = ChatOpenAI(
    openai_api_key="your-key",
    openai_api_base="your-proxy",
    temperature=0,
)

def chat_with_model(model, text):
    resp = model.invoke(text)
    content = resp if isinstance(resp, str) else resp.content
    return content

def generate_prompt():
    return ChatPromptTemplate.from_messages(
        [
            ("system", """
            ## 角色定位
            1.  你是一个专业的程序员，擅长使用 Python 语言进行 Web 开发。
            2.  你是一个乐于助人的程序员，可以帮助用户解决编程问题。
            3.  我将会问你一些问题，如果你回复代码，需要以markdown 的形式回复我。
            
            ## 技能特长：
            1. 精通 Tornado 框架进行 Web 开发
            2. 熟练使用百度的 AMIS 低代码平台
            3.能熟练运用 PeeWee ORM 库实现数据库操作
            """),
            ("human", "{human_question}"),
        ]
    )


def generate_openai_prompt(input_question):
    prompt = generate_prompt().invoke({
        "human_question": input_question
    })
    return prompt


question = """
我实现了一个amis 的低代码平台，接下来我将详细的介绍一下我的代码，你需要模仿我的代码去实现其他的能力。

下面是我的代码的逻辑，已经实现了一个CRUD 的逻辑。

## 路由定义

```python
        # 授权用户的新增 和批量获取
        (r"/api/auth_users", AuthUsersHandler),
        #  授权用户的单条数据的增删改查
        (r"/api/auth_user/(\d+)", AuthUserHandler),
```

## handler 处理的逻辑

```python
from server.control.user_auth_control import UserAuthControl
from server.handler.base_handler import BaseHandler


class AuthUsersHandler(BaseHandler):

    async def get(self):
        user_control = UserAuthControl()
        page = self.get_argument("page", 1)
        per_page = self.get_argument("perPage", 10)
        params = self.get_all_argument
        print(params)
        data = await user_control.get_page_table(page=int(page), per_page=int(per_page), id=params.get("id"),
                                                 name=params.get("name"), phone=params.get("phone"))
        self.success(data)

    async def post(self):
        print("新增接口", self.json_data)
        user_auth_control = UserAuthControl()
        public_key = "axxxx"
        private_key = "qwer"
        final_data = {
            **self.json_data,
            "public_key": public_key,
            "private_key": private_key
        }
        res = await user_auth_control.create_one(**final_data)
        self.success(res.id)

    async def delete(self):
        # ids 是一个 以逗号分隔的字符串
        ids = self.get_query_argument("id")
        id_list = ids.split(",")
        print(f"delete： {ids}， id_list： {id_list}")
        user_control = UserAuthControl()
        res = await user_control.delete_by_ids(id_list)
        self.success("ok")


class AuthUserHandler(BaseHandler):

    async def put(self, id):
        user_control = UserAuthControl()
        res = await user_control.update_one_by_id(id, **self.json_data)
        print("id", id)
        self.success("ok")

    async def delete(self, id):
        user_control = UserAuthControl()
        res = await user_control.delete_one_by_id(id)
        print("id", id)
        self.success("ok")

```

## control 处理的逻辑

```python
import asyncio
from typing import Dict, Optional

from playhouse.shortcuts import model_to_dict

from server.control.base_control import BaseControl
from server.db_manager import db_manager
from server.model.user_auth import UserAuth, UserAuthPydantic


class UserAuthControl(BaseControl):

    async def create_one(self, **kwargs) -> UserAuthPydantic:
        data = await db_manager.create(UserAuth, **kwargs)
        return UserAuthPydantic(**model_to_dict(data))

    async def get_one_by_id(self, user_id) -> Optional[Dict[str, str]]:
        res = await db_manager.get_or_none(UserAuth.select().where(UserAuth.id == user_id))
        if not res:
            return None
        serializer_data = BaseControl.serializer(res)
        return serializer_data

    async def update_one_by_id(self, user_id, **kwargs) -> Optional[Dict[str, str]]:
        query = UserAuth.update(**kwargs).where(UserAuth.id == user_id)
        return await db_manager.execute(query)

    async def delete_one_by_id(self, user_id) -> Optional[Dict[str, str]]:
        query = UserAuth.soft_delete().where(UserAuth.id == user_id)
        return await db_manager.execute(query)

    async def delete_by_ids(self, ids=None):

        if ids is None:
            ids = []
        # 多个 ids
        query = UserAuth.soft_delete().where(UserAuth.id.in_(ids))
        return await db_manager.execute(query)

    async def get_page_table(self, page, per_page, id, name, phone):
        search_query = UserAuth.is_deleted == 0
        if id:
            search_query &= (UserAuth.id == id)
        if not id:
            if name:
                search_query &= (UserAuth.name.contains(name))
            if phone:
                search_query &= (UserAuth.phone.contains(phone))

        res = await asyncio.gather(
            db_manager.execute(
                UserAuth.select().where(search_query).paginate(page=page, paginate_by=per_page)),
            db_manager.count(UserAuth.select().where(search_query)),
        )
        serializer_list = BaseControl.serializer_list(res[0])
        list_data = {
            "rows": serializer_list,
            "count": res[1]
        }
        return list_data

```

## model 层的定义

```python
from datetime import datetime

from peewee import *

from server.model.base_model import BaseDBModel, BasePydanticModel, Field as PyField


class UserAuthPydantic(BasePydanticModel):
    name: str
    phone: str
    mac: str
    expire_time: datetime
    create_time: datetime = PyField(default_factory=datetime.now)
    public_key: str
    private_key: str
    remark: str = None


class UserAuth(BaseDBModel):
    name = CharField(max_length=100, verbose_name="客户名称")
    phone = CharField(max_length=100, verbose_name="电话")
    mac = CharField(max_length=100, verbose_name="MAC地址")
    expire_time = DateTimeField(formats="%Y-%m-%d %H:%M:%S", verbose_name="到期时间")
    auth_time = DateTimeField(default=datetime.now, formats="%Y-%m-%d %H:%M:%S", verbose_name="授权时间")
    public_key = TextField(verbose_name="公钥")
    private_key = TextField(verbose_name="私钥")
    remark = TextField(default="", verbose_name="备注")

    class Meta:
        db_table = 'user_auth'
        verbose_name = '用户授权'
```

## 列表的json定义

```json
{
  "title": "客户授权管理",
  "remark": "客户列表",
  "name": "user_auth_CRUD",
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
          "api": "post:${API_HOST}/api/post/auth_user",
          "body": [
            {
              "type": "input-text",
              "name": "name",
              "label": "客户名称",
              "required": true
            },
            {
              "type": "divider"
            },
            {
              "type": "input-text",
              "name": "phone",
              "label": "手机号",
              "required": true
            },
            {
              "type": "divider"
            },
            {
              "type": "input-text",
              "name": "mac",
              "label": "Mac地址",
              "required": true
            },
            {
              "type": "divider"
            },
            {
              "type": "input-datetime",
              "name": "auth_time",
              "label": "授权时间",
              "required": true,
              "closeOnSelect": false,
              "isEndDate": true,
              "valueFormat": "YYYY-MM-DD HH:mm:ss",
              "displayFormat": "YYYY-MM-DD HH:mm:ss",
              "clearable": true
            },
            {
              "type": "divider"
            },
            {
              "type": "input-datetime",
              "name": "expire_time",
              "label": "过期时间",
              "required": true,
              "closeOnSelect": false,
              "isEndDate": true,
              "valueFormat": "YYYY-MM-DD HH:mm:ss",
              "displayFormat": "YYYY-MM-DD HH:mm:ss",
              "clearable": true
            },
            {
              "type": "divider"
            },
            {
              "type": "input-text",
              "name": "remark",
              "label": "备注",
              "required": true
            }
          ]
        }
      }
    }
  ],
  "body": {
    "type": "crud",
    "api": "/api/auth_users",
    "keepItemSelectionOnPageChange": true,
    "maxKeepItemSelectionLength": 11,
    "autoFillHeight": true,
    "syncLocation": false,
    "labelTpl": "${id} ${engine}",
    "autoGenerateFilter": true,
    "placeholder": "暂无数据",
    "bulkActions": [
      {
        "label": "批量删除",
        "actionType": "ajax",
        "api": "delete:${API_HOST}/api/auth_users?id=${ids|raw}",
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
        "tpl": "当前共有 ${count} 个客户",
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
            "api": "post:${API_HOST}/api/auth_users",
            "body": [
              {
                "type": "input-text",
                "name": "name",
                "label": "客户名称",
                "required": true
              },
              {
                "type": "divider"
              },
              {
                "type": "input-text",
                "name": "phone",
                "label": "手机号",
                "required": true
              },
              {
                "type": "divider"
              },
              {
                "type": "input-text",
                "name": "mac",
                "label": "Mac地址",
                "required": true
              },
              {
                "type": "divider"
              },
              {
                "type": "input-datetime",
                "name": "auth_time",
                "label": "授权时间",
                "required": true,
                "closeOnSelect": false,
                "valueFormat": "YYYY-MM-DD HH:mm:ss",
                "displayFormat": "YYYY-MM-DD HH:mm:ss",
                "clearable": true
              },
              {
                "type": "divider"
              },
              {
                "type": "input-datetime",
                "name": "expire_time",
                "label": "过期时间",
                "required": true,
                "closeOnSelect": false,
                "isEndDate": true,
                "valueFormat": "YYYY-MM-DD HH:mm:ss",
                "displayFormat": "YYYY-MM-DD HH:mm:ss",
                "clearable": true
              },
              {
                "type": "divider"
              },
              {
                "type": "input-text",
                "name": "remark",
                "label": "备注",
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
        "name": "name",
        "label": "客户名称",
        "sortable": true,
        "searchable": {
          "type": "input-text",
          "name": "name",
          "label": "客户名称",
          "placeholder": "输入客户名称",
          "mode": "horizontal"
        }
      },
      {
        "name": "phone",
        "label": "手机号",
        "sortable": true,
        "searchable": {
          "type": "input-text",
          "name": "phone",
          "label": "客户手机号",
          "placeholder": "输入手机号",
          "mode": "horizontal"
        }
      },
      {
        "name": "mac",
        "label": "Mac地址",
        "sortable": true
      },
      {
        "name": "auth_time",
        "label": "授权时间"
      },
      {
        "name": "expire_time",
        "label": "过期时间"
      },
      {
        "name": "public_key",
        "label": "公钥",
        "classname": "word-break",
        "width": 200
      },
      {
        "name": "private_key",
        "label": "私钥",
        "classname": "word-break",
        "width": 200
      },
      {
        "name": "remark",
        "label": "备注"
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
                    "name": "name",
                    "label": "客户名称",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "phone",
                    "label": "手机号",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "mac",
                    "label": "Mac地址",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-datetime",
                    "name": "auth_time",
                    "label": "授权时间",
                    "required": true,
                    "closeOnSelect": false,
                    "isEndDate": true,
                    "valueFormat": "YYYY-MM-DD HH:mm:ss",
                    "displayFormat": "YYYY-MM-DD HH:mm:ss",
                    "clearable": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-datetime",
                    "name": "expire_time",
                    "label": "过期时间",
                    "required": true,
                    "closeOnSelect": false,
                    "isEndDate": true,
                    "valueFormat": "YYYY-MM-DD HH:mm:ss",
                    "displayFormat": "YYYY-MM-DD HH:mm:ss",
                    "clearable": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "remark",
                    "label": "备注",
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
                "api": "put:${API_HOST}/api/auth_user/$id",
                "body": [
                  {
                    "type": "input-text",
                    "name": "name",
                    "label": "客户名称",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "phone",
                    "label": "手机号",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "mac",
                    "label": "Mac地址",
                    "required": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-datetime",
                    "name": "auth_time",
                    "label": "授权时间",
                    "required": true,
                    "closeOnSelect": false,
                    "isEndDate": true,
                    "valueFormat": "YYYY-MM-DD HH:mm:ss",
                    "displayFormat": "YYYY-MM-DD HH:mm:ss",
                    "clearable": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-datetime",
                    "name": "expire_time",
                    "label": "过期时间",
                    "required": true,
                    "closeOnSelect": false,
                    "isEndDate": true,
                    "valueFormat": "YYYY-MM-DD HH:mm:ss",
                    "displayFormat": "YYYY-MM-DD HH:mm:ss",
                    "clearable": true
                  },
                  {
                    "type": "divider"
                  },
                  {
                    "type": "input-text",
                    "name": "remark",
                    "label": "备注",
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
            "api": "delete:${API_HOST}/api/auth_user/$id"
          }
        ],
        "toggled": true
      }
    ]
  }
}

```

## 新增单个项的json定义

```json
{
  "type": "page",
  "title": "新增",
  "remark": null,
  "toolbar": [
    {
      "type": "button",
      "actionType": "link",
      "link": "/user_auth/list",
      "label": "返回列表"
    }
  ],
  "body": {
    "type": "form",
    "name": "sample-edit-form",
    "api": "post:${API_HOST}/api/auth_users",
    "body": [
      {
        "type": "input-text",
        "name": "name",
        "label": "客户名称",
        "required": true
      },
      {
        "type": "divider"
      },
      {
        "type": "input-text",
        "name": "phone",
        "label": "手机号",
        "required": true
      },
      {
        "type": "divider"
      },
      {
        "type": "input-text",
        "name": "mac",
        "label": "Mac地址",
        "required": true
      },
      {
        "type": "divider"
      },
      {
        "type": "input-datetime",
        "name": "auth_time",
        "label": "授权时间",
        "required": true,
        "closeOnSelect": false,
        "valueFormat": "YYYY-MM-DD HH:mm:ss",
        "displayFormat": "YYYY-MM-DD HH:mm:ss",
        "clearable": true
      },
      {
        "type": "divider"
      },
      {
        "type": "input-datetime",
        "name": "expire_time",
        "label": "过期时间",
        "required": true,
        "closeOnSelect": false,
        "isEndDate": true,
        "valueFormat": "YYYY-MM-DD HH:mm:ss",
        "displayFormat": "YYYY-MM-DD HH:mm:ss",
        "clearable": true
      },
      {
        "type": "divider"
      },
      {
        "type": "input-text",
        "name": "remark",
        "label": "备注",
        "required": true
      }
    ]
  }
}

```

## 上面的就是我写的全部的代码内容，接下来，我将会把新的模型定义提供给你，你需要写出j基于此模型定义的如下内容

1. 新模型的路由定义
2. 新模型的handler 处理的逻辑
3. 新模型的 control 处理的逻辑
4. 新模型的列表的json定义
5. 新模型的新增单个项的json定义


##  新的模型定义

```python
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

"""
# content = chat_with_model(OpenAILLM, generate_openai_prompt("你好，你是谁？"))
content = chat_with_model(OpenAILLM, generate_openai_prompt(question))

with open("output_todo.md", "w", encoding="utf-8") as f:
    f.write(content)
print(content)
