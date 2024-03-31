import tornado
import json


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        if self.request.method in ['POST', 'PUT', 'PATCH'] and self.request.headers[
            "Content-Type"] == "application/json":
            try:
                self.json_data = json.loads(self.request.body)
            except json.JSONDecodeError:
                self.set_status(400)
                self.finish("Invalid JSON data")
        elif self.request.method == 'GET':
            all_argument = {}
            for key in self.request.arguments:
                all_argument[key] = self.get_argument(key)
            self.get_all_argument = all_argument
        else:
            self.json_data = None

    def success(self, data, msg="成功"):
        self.write({
            "status": 0,
            "data": data,
            "msg": msg
        })

    def fail(self, data, msg="失败"):
        self.write({
            "status": 400,
            "data": data,
            "msgTimeout": 3000,  # 弹框时间，单位是毫秒
            "msg": msg
        })
