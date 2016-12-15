from UserDict import UserDict
from time import time
import threading
import signal
import logging


class CachedObject(object):
    def __init__(self, key, value, date, ttl):
        self.key = key
        self.value = value
        self.date = date
        self.ttl = ttl

    def __str__(self):
        return "key: %s, value: %s, date: %s, ttl: %d" % (self.key, self.value, self.date, self.ttl)

    def is_expired(self, when):
        return when - self.date > self.ttl

    def is_expired_now(self):
        return self.is_expired(time())


class Storage(UserDict):
    def __init__(self, ttl=60, cleanup_interval=60, purge_callback=(lambda dictionary: None)):
        UserDict.__init__(self)
        self.__ttl = ttl
        self.__cleanup_interval = cleanup_interval
        self.__purge_callback = purge_callback
        self.lock = threading.RLock()
        self.timer = self.__start_timer()
        self.__graceful_shutdown_setup()

    def __len__(self):
        with self.lock:
            return len(self.data)

    def __getitem__(self, key):
        with self.lock:
            if key in self.data and not self.data[key].is_expired_now():
                self.data[key].date = time()
                return self.data[key].value

    def __setitem__(self, key, value):
        with self.lock:
            obj = CachedObject(key, value, time(), self.__ttl)
            self.data[key] = obj

    def __delitem__(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]

    def __iter__(self):
        with self.lock:
            now = time()
            for key, obj in self.data.iteritems():
                if not obj.is_expired(now):
                    yield key, obj.value

    def __contains__(self, key):
        with self.lock:
            return key in self.data and not self.data[key].is_expired_now()

    def __start_timer(self):
        t = threading.Timer(self.__cleanup_interval, self.__purge)
        t.setDaemon(True)
        t.start()
        return t

    def __purge(self):
        self.timer = self.__start_timer()
        now = time()
        deleted = {}
        with self.lock:
            for key, obj in self.data.items():
                if obj.is_expired(now):
                    deleted[key] = self.data[key].value
                    del self.data[key]
        if deleted:
            self.__purge_callback(deleted)

    def __graceful_shutdown_setup(self):
        old_signals = {sig: signal.getsignal(sig) for sig in
                       [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]}

        def helper(sig, frame):
            self.timer.cancel()
            logging.info("shutting down. waiting for completion")
            self.__purge_callback({key: obj.value for key, obj in self.data.iteritems()})
            old_signals[sig](sig, frame)

        for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
            signal.signal(sig, helper)
