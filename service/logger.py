# logging
#from  asyncio import *
#import asyncio
import threading

import traceback
#My old code: https://github.com/sohale/snippets/blob/master/python/deb.py

CRED = '\033[91m'
C_PLAIN = '\033[0m'

CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

#logger_lock = asyncio.Lock()
logger_lock = threading.Lock()
global logger_lock

def log(message):
    #async with logger_lock:
    global logger_lock
    logger_lock.acquire()
    print(C_PLAIN)
    if True:
        print(C_PLAIN)
        print("api server:", message)
    print('',end='',flush=True)
    logger_lock.release()

def log_warn(message):
    #async with logger_lock:
    global logger_lock
    logger_lock.acquire()
    print(C_PLAIN)
    if True:
        print(CYELLOW)
        print("api server WARNING:", message)
        print(C_PLAIN)
    print('',end='',flush=True)
    logger_lock.release()

def log_err(message):
    #async with logger_lock:
    global logger_lock
    logger_lock.acquire()
    if True:
        print(CRED)
        print("1api server ERROR:", message)
        if False:
            """
            r = traceback.extract_stack()
            line_number=r[-2][1]
            funcname=r[-2][2]
            text=r[-3][3]
            print("-------------------- %r: %r         %s %r"%(line_number,text,funcname, tuple(args)))
            """
            pass
        print(C_PLAIN)
    print('',end='',flush=True)
    logger_lock.release()
