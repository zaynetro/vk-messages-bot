"""
Poller class (long polls vk api for new message events)
"""

from threading import Thread
import requests
from queue import Queue
from vk import LongPollServer
from telegram.dispatcher import run_async

class Poller():
    def __init__(self):
        self.is_running = False
        self.servers = Queue()
        self.cb = Poller.noop

    def async_run(self, cb):
        self.is_running = True
        self.cb = cb
        poll_thread = Thread(target=self._run,
                             name='poll')

        poll_thread.start()

    def _run(self):
        print 'In _run'
        while self.is_running:
            if not self.servers.empty():
                server = self.servers.get()
                server, updates = self.poll(server)
                print 'Poll resulted in ' + str(server) + ', ' + str(updates)
                self.add(server)
                self.exec_cb(updates=updates, server=server)

        print 'Exit _run'

    def stop(self):
        self.is_running = False

    @run_async
    def exec_cb(self, updates, server):
        self.cb(updates=updates, server=server)

    @staticmethod
    def noop():
        pass

    def add(self, server):
        if server == None:
            return

        self.servers.put(server)

    def poll(self, server):
        server, key, ts, chat_id = server
        url = 'http://' + server
        params = {'key':key, 'ts':ts, 'wait': 25, 'act':'a_check', 'mode':2}
        r = requests.get(url, params=params)
        if r.status_code != requests.codes.ok:
            return None

        json = r.json()
        if 'failed' in json:
            return None

        return LongPollServer(server, key, json['ts'], chat_id), json['updates']
