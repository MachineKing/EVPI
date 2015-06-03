#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as sql
import sys

table = "raw_pack"
test = [5.0, 3.0]
try: 
    con = sql.connect("pack.db")
    cur = con.cursor()
    cur.execute("DROP TABLE IF EXISTS {0}".format(table))  
    cur.execute("CREATE TABLE {0}(Id REAL, Name REAL, Price REAL)".format(table))
    cur.execute("INSERT INTO {0} VALUES({1} ,{2} ,{3} )".format(table,test[1], test[0], test[1]))
except sql.Error, e:
    print "Error %s:" % e.args[0]
    sys.exit(1)
    
finally:
    con.commit()
    con.close()
        
