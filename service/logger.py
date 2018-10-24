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

global logger_lock

#logger_lock = asyncio.Lock()
logger_lock = threading.Lock()

def log(message, *a,**kw):
    check_none_brutal(a)
    check_none_brutal(kw)

    #async with logger_lock:
    global logger_lock
    logger_lock.acquire()
    print(C_PLAIN, end="")
    if True:
        print(CGREEN, end="")
        print("Log: api server: ", end="")
        print(C_PLAIN, end="")
        print(message)
    print('',end='',flush=True)
    logger_lock.release()

def log_highlight(message, *a,**kw):
    check_none_brutal(a)
    check_none_brutal(kw)
    global logger_lock
    logger_lock.acquire()
    if True:
        print(CGREEN, end="")
        print("Log: api server: ", end="")
        print(CYELLOW, end="")
        print(message, end="")
        print(C_PLAIN)
    print('',end='',flush=True)
    logger_lock.release()

def log_warn(message, *a,**kw):
    check_none_brutal(a)
    check_none_brutal(kw)

    #async with logger_lock:
    global logger_lock
    logger_lock.acquire()
    print(C_PLAIN, end="")
    if True:
        print(CGREEN, end="")
        print("Log: api server WARNING: ", end="")
        print(CYELLOW, end="")
        print(message, end="")
        print(C_PLAIN)
    print('',end='',flush=True)
    logger_lock.release()

def log_err(message, *a,**kw):
    check_none_brutal(a)
    check_none_brutal(kw)
    #async with logger_lock:
    global logger_lock
    logger_lock.acquire()
    if True:
        print(CGREEN, end="")
        print("Log: api server ERROR: ", end="")
        print(CRED, end="")
        #print("api server ERROR:      ", C_PLAIN, message)
        print(message, end="")
        if  False:
            #r = "\n",join(reduce(traceback.extract_stack()))
            r = traceback.extract_stack()
            #print(r)
            ctr = 0
            for l in r:
                ctr += 1
                print(ctr, l)
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


def check_none_brutal(a):
    #""" Makes sure the usage of log() is itself correct."""
    if not a == () and not  a == {} and not (type(a) == list and len(a)==0 ):
        if a is not None:
            print(CRED, "too many arguments", a)
            exit(1)
