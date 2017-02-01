# -*- coding: utf-8 -*-
"""Init and utils."""

from zope.i18nmessageid import MessageFactory
from sqlalchemy.ext import declarative


_ = MessageFactory('ex.nba')

ORMBase = declarative.declarative_base()

