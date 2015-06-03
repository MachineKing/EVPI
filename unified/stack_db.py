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
timeNow = datetime.datetime.now()

def create_table(db_name, table_name):
	db_con = sql.connect(db_name)
	try:
           	with db_con:
          		cur = db_con.cursor()
          		cur.execute("DROP TABLE IF EXISTS {0}".format(table_name))
          		cur.execute("CREATE TABLE IF NOT EXISTS {0}(cell_1 REAL, cell_2 REAL, cell_3 REAL,cell_4 REAL, cell_5 REAL, cell_6 REAL, cell_7 REAL, cell_8 REAL, cell_9 REAL, cell_10 REAL,  current INT, time TEXT)".format(table_name))	
        except sql.Error, e:
            print "Error %s:" % e.args[0]
            sys.exit(1)		
	return

def pack_state(table_name, ten_v, current, status, time):
        time = "\"" + str(time).rstrip("0") + "\"" # convert datetime object into a string suitable for insertion into SQLite command
	con = None
	     
	try:
		con = sql.connect("pack.db")
		cur = con.cursor()
		cur.execute("INSERT INTO {0} VALUES({1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12})".format(table_name, ten_v[0], ten_v[1], ten_v[2], ten_v[3], ten_v[4], ten_v[5], ten_v[6], ten_v[7], ten_v[8], ten_v[9], current, time))
	except sql.Error, e:
		print "Error %s:" %e.args[0]
		sys.exit(1)
	finally:
		if con:
		    con.commit()
                    con.close()
	return
def new_db():
    dir_t = str(datetime.datetime.now()).rstrip("0")
    dir_t=dir_t.replace("-", "")
    dir_t=dir_t.replace(" ", "-")
    print dir_t
    os.system("cd /home/pi/evpi && sudo cp pack.db /home/pi/evpi/db_backup/{0}.db".format(dir_t[2:17]))
    create_table("pack.db", stackA)
    create_table("pack.db", stackB) 
    create_table("pack.db", stackC)
    create_table("pack.db", stackD)
    return  
    
def to_csv(table_name, db_name):
    con = None
    dir_t = datetime.datetime.now()
    
    try:
        con = sql.connect(db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM {0}".format(table_name)) 
        rows = cur.fetchall()
        output_file = open("{0}.csv".format(dir_t[2:17]))
        
        for row in rows:
            for item in row:
                thingy = ","+ str(item)
                output_file.write(thingy)
            output_file.write("\n")
        output_file.close()
            
    except sql.Error, e:
        print "Error %s:" % e.args[0]
        return False
    finally:
        con.close()
        
        return True 
    return 


if to_csv(stackD,"pack.db"):
   print "SUCCESS" 

 
"""
create_table("pack.db", stackA)
create_table("pack.db", stackB)
create_table("pack.db", stackC)
create_table("pack.db", stackD)
    

pack_state(stackA, cell_value, stack_current[0], "charging", timeNow)
pack_state(stackB, cell_value, stack_current[1], "charging", timeNow) 
pack_state(stackC, cell_value, s  tack_current[2], "charging", timeNow) """
pack_state(stackD, cell_value, stack_current[3], "charging", timeNow) 

 