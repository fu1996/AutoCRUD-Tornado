import tornado
import json
from amis.components import App


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        # page = App(title='标题', brandName="Admin", logo="/static/public/logo.png", api="/api/get/site-menu")
        # self.write(page.amis_html())
        self.render("index.html")
