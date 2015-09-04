import pandas as pd
import sys, time, datetime, math
import sqlite3 as sql

iBat = [0.1]
vBat = [0.1]
iCont = [0.1]
vCont = [0.1]
iMot = [0.1]
vMot = [0.1]
tBat=[unicode(datetime.datetime.now())]
tMot=[unicode(datetime.datetime.now())]
tCont=[unicode(datetime.datetime.now())]

tempBat=[25.0]
tempBms=[25.0]
tempMot=[25.0]
rpmMot=[0.1]
tSense=[unicode(datetime.datetime.now())]
cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8, cell9, cell10 =[0], [0], [0], [0], [0], [0], [0], [0], [0], [0]

EvData = zip(iBat, vBat, tBat, iCont, vCont, tCont, iMot, vMot, tMot, tempBat, tempBms, rpmMot, tSense)
BatData = zip(iBat, vBat, tBat, cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8, cell9, cell10)

powerFrame=pd.DataFrame(data = EvData, columns = ['iBat', 'vBat', 'tBat', 'iCont', 'vCont', 'tCont', 'iMot', 'vMot', 'tMot', 'tempBat', 'tempBms', 'rpmMot', 'tSense'])

con = None
try:
    con = sql.connect("pack.db")
    cur = con.cursor()
except sql.Error, e:
    print "Error %s:" %e.args[0]


powerFrame.to_sql('power', con, flavor='sqlite', schema=None, if_exists='replace', index=True, index_label=None, chunksize=None, dtype=None)

print powerFrame
powerFrame=pd.DataFrame(data = EvData, columns = ['iBat', 'vBat', 'tBat', 'iCont', 'vCont', 'tCont', 'iMot', 'vMot', 'tMot', 'tempBat', 'tempBms', 'rpmMot', 'tSense'])
print powerFrame
powerFrame.to_sql('power', con, flavor='sqlite', schema=None, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)
