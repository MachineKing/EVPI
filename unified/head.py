import datetime, os, sys
#import bat_lev as disp
import stack_db as db
"""
pack_state(table_name, ten_v, current, status, time)
create_table(db_name, table_name)
db.pack_state(stackA, cell_value, 4, "charging", timeNow)

"""

stackA = "stack_one"
stackB = "stack_two"
stackC = "stack_three"
stackD = "stack_four"

cell_value =[3.5, 3.6, 3.9, 4.0, 3.88]*2

# check if bms is plugged in
try:
	bms_ser = serial.Serial('/dev/ttyACM0', 9600)
	print "BMS present"
except:
	print "BMS not plugged in"

	
# initialize pygame display module	
try:  
	pygame.init()
	pygame.font.init()
	display = pygame.display.set_mode((500, 500))
	pygame.display.set_caption('Battery Level indicator')
	print "pygame initialized"
except:
	print "pygame failed miserably"
		
font = pygame.font.SysFont("arial", 9)


def read_bat(line, pack):
	f10 = line.split(' ')
	if(pack ==1):
		for x in range(0, 10):
			try:
				cell_value[x] = float(f10[x])
				bat_levels[x] = int(((cell_value[x]-3))*10) #translate 2-4V to a range of 0-10 (2V = empty)
			except:
				bat_levels[x]=0
	return



