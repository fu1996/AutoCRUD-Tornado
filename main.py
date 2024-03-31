import asyncio
import tornado
import os
from server.db_manager import db_manager
from server.handler.heart_beat_handler import HeartBeatHandler
from server.handler.main_handler import MainHandler
from server.handler.todo_handler import TodoItemsHandler, TodoItemHandler
from server.util.create_db import init_db_table

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ROOT = os.path.join(ROOT, 'template')
STATIC_ROOT = os.path.join(ROOT, 'static')

print("ROOT:", ROOT)
print("TEMPLATE_ROOT:", TEMPLATE_ROOT)
print("STATIC_ROOT:", STATIC_ROOT)


def make_app(**settings):
    # 遵循 restful 规范：https://ruanyifeng.com/blog/2014/05/restful_api.html
    return tornado.web.Application([
        (r"/success", HeartBeatHandler),
        (r"/api/todo_items", TodoItemsHandler),
        (r"/api/todo_item/(\d+)", TodoItemHandler),
        (r"/", MainHandler),
    ], **settings)


async def main():
    settings = {
        "debug": True,
        "static_path": os.path.join(ROOT, "static"),
        "template_loader": tornado.template.Loader(TEMPLATE_ROOT)
    }
    # 初始化一下数据库表
    init_db_table()
    app = make_app(**settings)
    app.listen(9999)
    # 可以在app实例上绑定一些资源【单例模式】
    app.db_manager = db_manager
    # print("====：新增模型README.md时候，记得需要执行 util 目录下的 init_db_table 方法初始化表结构")
    print(f"Server started on http://localhost:9999")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
