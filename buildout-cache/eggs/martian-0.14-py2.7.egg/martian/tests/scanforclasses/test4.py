# this is a module has a single Context subclass in it.
# this module is used in a scan_for_context.txt test.

import os
from martian.tests.scanforclasses import IContext, Context
from zope.interface import implements

foo = "Bar"

class Qux(object):
    pass

class Hallo:
    pass

class MyContext(object):
    implements(IContext)

class MyContext2(Context):
    pass

class MyContext3(MyContext):
    pass

class MyContext4(MyContext2):
    pass

qux = Qux()
hallo = Hallo()
mycontext = MyContext()
