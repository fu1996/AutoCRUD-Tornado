## 项目说明

AutoCRUD-Tornado是一个基于 GPT、Tornado 和 PeeWee 的 AI 自动编写 CRUD 代码框架。
该框架可以帮助开发者快速生成数据库操作的代码，提高开发效率和减少重复工作。
无需手动编写 CRUD 操作代码，让 AI 来为您完成！欢迎加入我们，一起探索自动化编程的未来！

### 项目技术栈：

- amis 低代码工具
- tornado + peewee ORM 框架
- mysql 数据库
- ChatGPT 自动生成CRUD机器人【见`ai_crud`目录】

### 本地项目启动：

1. 安装依赖包：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple `
2. 配置数据库环境：`server/db_manager/__init__.py`
3. 启动项目：

```shell
python main.py
```

4. 访问项目：`http://127.0.0.1:9999`
5. 推荐开启自动格式化代码（免插件）：https://blog.csdn.net/weixin_45638544/article/details/132206994

### 代码目录说明：

一些核心的实现方法都在一些 `base` 开头的文件中，使用之前应该先查看这些文件。

> 比如 针对前端的请求的处理 查看 `base_handler.py`

```shell
├── main.py #  项目启动入口
├── requirements.txt #  依赖包文件
├── server #   项目代码目录
│   ├── __init__.py
│   ├── control #    控制层目录 【重要】
│   ├── db_manager #   数据库操作目录
│   ├── handler #    处理层目录 【重要】
│   ├── model #     模型层目录【重要】
│   └── util #      工具类目录
├── static #    静态文件目录
│   ├── pages
│   └── public
└── template #     模板文件目录
    └── index.html

```

### 接口开发规范：

- 遵循 restful API 规范。参考：https://ruanyifeng.com/blog/2014/05/restful_api.html
- 遵循 amis
  接口格式：https://aisuda.bce.baidu.com/amis/zh-CN/docs/types/api#%E6%8E%A5%E5%8F%A3%E8%BF%94%E5%9B%9E%E6%A0%BC%E5%BC%8F-%E9%87%8D%E8%A6%81-

### ORM 使用帮助

- Peewee: https://www.osgeo.cn/peewee/peewee/quickstart.html#quickstart
- ORM 使用帮助：https://blog.csdn.net/ch_improve/article/details/114177508

## 经验总结

### 1. 优雅的使用数据库 db 对象

文档地址：https://www.tornadoweb.org/en/stable/guide/structure.html

理论支持：在 url 中的第三个参数会传递给 handler 对象的`initialize`方法，可以在这里初始化数据库连接。

```python
import asyncio
import tornado
from tornado.web import url, RequestHandler


class StoryHandler(RequestHandler):
    def initialize(self, db):
        self.db = db

    def get(self, story_id):
        print("db_manager", self.db)
        self.write("this is story %s" % story_id)


db = "123"


def make_app():
    return tornado.web.Application([
        url(r"/story/([0-9]+)", StoryHandler, dict(db=db), name="story")
    ], debug=True)


async def main():
    app = make_app()
    app.listen(8888)
    print("Server started on http://localhost:8888")
    shutdown_event = asyncio.Event()
    await shutdown_event.wait()


if __name__ == "__main__":
    asyncio.run(main())

```

### 2. 直接返回 字典 会被解析为 JSON

```python
from tornado.web import url, RequestHandler


class JsonHandler(RequestHandler):
    def get(self):
        self.write({"name": "world"})
```

## TODO:

- [ ] 封装数据库迁移记录的能力
- [ ] GPT直接生成相关文件，不需要再从生产的markdown里复制粘贴
