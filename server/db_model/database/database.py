# -*- coding: UTF-8 -*-

import os
from peewee import *

# requirement PyMySQL
db = MySQLDatabase(
    database=os.environ.get('GEISTER_DATABASE_NAME' ,'geister'),
    user=os.environ.get('GEISTER_DATABASE_USER', 'peewee'),
    password=os.environ.get('GEISTER_DATABASE_PASS', 'peewee'),
    host=os.environ.get('GEISTER_DATABASE_HOST', 'localhost'),
    port=int( os.environ.get('GEISTER_DATABASE_PORT', 3306) )
)

