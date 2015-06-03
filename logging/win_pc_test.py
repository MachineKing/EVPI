#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as sql
import os, sys, time, datetime
stackA = "stack_one"
stackB = "stack_two"
stackC = "stack_three"
stackD = "stack_four"

cell_value =[3.5, 3.6, 3.9, 4.0, 3.88]*2
stack_current = [10.0, 2.67, 3.4, 6.789]

def create_table(db_name, table_name):
	db_con = sql.connect(db_name)
	try:
           	with db_con:
          		cur = db_con.cursor()
          		cur.execute("DROP TABLE IF EXISTS {0}".format(table_name))
          		cur.execute("CREATE TABLE IF NOT EXISTS {0}(cell_1 REAL, cell_2 REAL, cell_3 REAL,cell_4 REAL, cell_5 REAL, cell_6 REAL, cell_7 REAL, cell_8 REAL, cell_9 REAL, cell_10 REAL,  current INT, time NONE)".format(table_name))	
        except sql.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)		
	return

def pack_state(table_name, ten_v, four_i, status):
	con = None
        try:
            timeNow = time.time()
        except:
            e = sys.exc_info()[0]
            print e
	    
	try:
		con = sql.connect("pack.db")
		cur = con.cursor()
		cur.execute("INSERT INTO {0} VALUES({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12})".format(table_name, ten_v[0], ten_v[1], ten_v[2], ten_v[3], ten_v[4], ten_v[5], ten_v[6], ten_v[7], ten_v[8], ten_v[9], four_i[0], timeNow))
	except sql.Error, e:
		print "Error %s:" %e.args[0]
		sys.exit(1)
	finally:
		if con:
		    con.commit()
                    con.close()
	return

create_table("pack.db", stackA)
create_table("pack.db", stackB)
create_table("pack.db", stackC)
create_table("pack.db", stackD)

pack_state(stackA, cell_value, stack_current, "charging")
pack_state(stackB, cell_value, stack_current, "charging") 
pack_state(stackC, cell_value, stack_current, "charging") 
pack_state(stackD, cell_value, stack_current, "charging")  

