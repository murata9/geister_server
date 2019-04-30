# -*- coding: UTF-8 -*-

from peewee import *

# requirement PyMySQL
db = MySQLDatabase(
    database='geister',
    user='peewee',
    password="peewee",
    host="127.0.0.1",
    port=3306)

