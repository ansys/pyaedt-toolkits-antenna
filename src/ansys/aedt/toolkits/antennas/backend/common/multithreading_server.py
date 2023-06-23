# -*- coding: utf-8 -*-
import queue
import socket
import socketserver
import threading
import wsgiref.simple_server

# techniques described here taken from
# https://gist.github.com/coffeesnake/3093598
# https://bottlepy.org/docs/dev/recipes.html
# https://adamj.eu/tech/2019/05/27/the-simplest-wsgi-middleware/
# https://stackoverflow.com/questions/25155267/how-to-send-a-signal-to-the-main-thread-in-python-without-using-join
# https://en.wikipedia.org/wiki/Callable_object#In_Python

# The content of this file is copyright of the respective owners


class ThreadingWSGIServer(socketserver.ThreadingMixIn, wsgiref.simple_server.WSGIServer):
    pass


class Invoker:
    def __init__(self, func):
        self._func = func
        self._event = threading.Event()

    def invoke(self):
        self._result = self._func()
        self._event.set()

    def get_result(self):
        self._event.wait()
        return self._result


class SingleThreadResponseExecutor(object):
    def __init__(self, app):
        self._app = app
        self._queue = queue.Queue()

    def __call__(self, environ, start_response):
        invoker = Invoker(lambda: self._app(environ, start_response))
        self._queue.put(invoker)
        return invoker.get_result()

    def execute_responses_on_this_thread(self):
        print("press control-c to terminate")
        while True:
            try:
                self._queue.get().invoke()
            except KeyboardInterrupt:
                print("got keyboard interrupt")
                break


class MultithreadingServer:
    def run(self, host, port, app):
        executor = SingleThreadResponseExecutor(app)
        server_cls = ThreadingWSGIServer
        if ":" in host:  # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, "address_family") == socket.AF_INET:

                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        httpd = wsgiref.simple_server.make_server(host, port, app=executor, server_class=server_cls)

        print("listening on {}:{}".format(host, port))
        server_thread = threading.Thread(target=httpd.serve_forever)
        # ensure thread dies on termination
        # normally this would be dodgy but this tread doesn't hold anything other than sockets
        # the expectation is that the sockets will get released on process termination
        # - strange if they didn't
        server_thread.daemon = True
        server_thread.start()

        executor.execute_responses_on_this_thread()
