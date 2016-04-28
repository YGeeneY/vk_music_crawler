import json

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options, parse_command_line

from vk_crawl import PhantomVkCrawler

define("port", default=8800, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @tornado.web.asynchronous
    def get(self):
        self.render("templates/index.html")


class AudioWS(tornado.websocket.WebSocketHandler):

    def data_received(self, chunk):
        pass

    def check_origin(self, origin):
        return True

    def open(self):
        self.crawler = PhantomVkCrawler()

    def on_message(self, message):
        songs = self.crawler.query_vk_audio(message)
        self.write_message(json.dumps(songs))

    def on_close(self):
        pass
settings = {'auto_reload': True, 'debug': True}
app = tornado.web.Application([
    (r'/vklovely/', IndexHandler),
    (r'/websocket/', AudioWS),
], **settings)


if __name__ == '__main__':
    parse_command_line()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()