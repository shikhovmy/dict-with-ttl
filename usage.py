__author__ = 'mshikhov'
import logging
import random
from storage import Storage
from time import sleep

if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format="%(message)s")


    def cb(x):
        randint = random.randint(1, 5)
        print "%s. callback begin. gonna wait for %d sec" % (x, randint)
        sleep(randint)
        print("%s. done. dying" % x)


    s = Storage(ttl=10, cleanup_interval=1.0, purge_callback=cb)
    i = 0
    while True:
        s[i] = i
        i += 1
        sleep(1)
        if i %5 == 0:
            print 5
