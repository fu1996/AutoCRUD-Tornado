from server.handler.base_handler import BaseHandler


class HeartBeatHandler(BaseHandler):
    def get(self):
        self.success("heartbeat success")
