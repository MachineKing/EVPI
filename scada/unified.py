import pygame, sys, time, serial, datetime, math
from pygame.locals import *
import pandas as pd
import sqlite3 as sql



# ###################################################################################################################################	
# ###################################################################################################################################
#zero crossing detection flags


#display variables
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)

#database variables
rpm = [0]*3 #rpm 0 is motor rpm 1 is axle
temp = [0]*3 #temp 0 is motor temp 1 is controller temp 2 is battery
bat_levels = [1]*40
cell_value = [2.0]*40 #lists 40 elements long initialized with value [#]
bat_cell_height = 10
bat_pack_height = 1
temp_v=[0]
temp_i=[0]
bat_voltage_roll=[]
# database seeds for creation of new tables
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


# ###################################################################################################################################	
# ###################################################################################################################################		
try:
	bms_ser = serial.Serial('/dev/ttyACMa0', 9600, timeout=0)
	print "BMS present"
except:
	print "BMS not plugged in"
try:
	sense_ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0)
	print "Sensor Node present"
except:
	print "Sensor Node not plugged in"

try:  
	pygame.init()
	pygame.font.init()
	display = pygame.display.set_mode((500, 500))
	pygame.display.set_caption('Battery Level indicator')
	print "pygame initialized"
except:
	print "pygame failed miserably"
	
	
font = pygame.font.SysFont("arial", 20)

# ###################################################################################################################################	
# ###################################################################################################################################	
def setup_frames():
	for x in range(0, 40):
		pygame.draw.rect(display, white, (x*12,500-0,bat_cell_height*10,11), 1)
	return
# ###################################################################################################################################	
# ###################################################################################################################################		
def stack_current(current, stack):
	pygame.draw.rect(display, white, (0,152,32,104), 1)	
	for L in range(0, int(current*10)):
		pygame.draw.rect(display, blue, (1,250-int(L*bat_pack_height),30,1), 1)		

# ###################################################################################################################################	
# ###################################################################################################################################		
"""
battery cell receives the voltage level of a single cell and plots a bar graph at the specified location
"""	
def battery_cell(level, cell_val, locX, locY):
	if level < 5:
		color = red
	elif cell_val>4:
		colour = blue
	else:
		color = green
	for L in range(0, level):
		pygame.draw.rect(display, color, (locX,500-locY-L*bat_cell_height,bat_cell_height,bat_cell_height), 1)
	
	temp_text = str(cell_val)
	if len(temp_text)>3:
		temp_text = temp_text[:-1] #strip the last character from the string
	text = font.render(temp_text, True, white)
	display.blit(text,(locX // 1, 520-locY - text.get_height() // 1))
	return
# ###################################################################################################################################	
# ###################################################################################################################################		
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
# ###################################################################################################################################	
#display sensor values
# ###################################################################################################################################	
def display_speed(speed):
	text = font.render(str(speed[0]), True, white)
	display.blit(text,(250, 300))
	return
def display_temp(temps):
	text = font.render(str(temps[0]), True, white)
	display.blit(text,(250, 250))
	return	


# ###################################################################################################################################	
# ###################################################################################################################################	
def rms_volt(voltage):
	voltage_sum=0
	voltage_wave=[]
	voltage_mean=0
	zero_cross=0
	vrms=0
	period_flag=False
	end_period_flag=False
	#convert each adc reading to a current and sum
	for element in voltage:
	#try:
		if 2000<=int(element)<=2100:
			if not period_flag:
				zero_cross+=1
			period_flag=True
		elif 1<=zero_cross<=2:
			period_flag=False
			voltage_sum += ((float(element)*5/4096)*49.17)#**2
			voltage_wave.append((float(element)*5/4096)*49.17)
		else:
			pass
	"""except:
		print "that funny base 10 error"
		voltage_wave.append(voltage_wave[len(voltage_wave)-1])"""
						
	#get mean of squared values
	voltage_mean=voltage_sum/len(voltage)
	#get square root of mean = rms value
	vrms=math.sqrt(voltage_mean)

	print max(voltage_wave)-min(voltage_wave)
	del voltage_wave[:]	
	return
	
	return
def rms_amp(current):
	current_sum=0
	current_wave=[]
	current_mean=0
	zero_cross=0
	irms=0
	period_flag=False
	end_period_flag=False
	#convert each adc reading to a current and sum
	for element in current:
	#try:
		if 2000<=int(element)<=2100:
			if not period_flag:
				zero_cross+=1
			period_flag=True
		elif 1<=zero_cross<=2:
			period_flag=False
			current_sum += ((float(element)*5/4096)*49.17)#**2
			current_wave.append((float(element)*5/4096)*49.17)
		else:
			pass
	"""except:
		print "that funny base 10 error"
		current_wave.append(current_wave[len(current_wave)-1])"""
			
	#get mean of squared values
	current_mean=current_sum/len(current)
	#get square root of mean = rms value
	irms=math.sqrt(current_mean)

	print max(current_wave)-min(current_wave)
	del current_wave[:]	
	
	return
# ###################################################################################################################################	
#Battery voltage calculator
# ###################################################################################################################################
def bat_volts(in_serial, sense_ser):
	bat_voltage_sum=0
	voltage=0
	roll_avg=0
	volt_div=243.03
	iso_amp_gain=4.04
	amp_gain=3
	
	print "motor voltage"
	while(in_serial != "end\n"):
		if(sense_ser.inWaiting() !=0):
			in_serial = sense_ser.readline()
			if(in_serial!="end\n"):
				temp_v.append(in_serial)
	sense_ser.write("a")
		
	for element in temp_v:
		voltage += (((float(element)*5/4096)/amp_gain)/iso_amp_gain)*volt_div
	mean_voltage=voltage/len(temp_v)
	#keep a rolling average of battery voltage
	bat_voltage_roll.append(mean_voltage)
	if(len(bat_voltage_roll)>10):
		del bat_voltage_roll[0]
	for element in bat_voltage_roll:
		bat_voltage_sum+=element
	roll_avg = bat_voltage_sum/len(bat_voltage_roll)
	bat_voltage_sum=0
	text = font.render(str(roll_avg), True, white)
	display.blit(text,(100, 300))
	del temp_v[:]
	print roll_avg
	return roll_avg	 

def bat_amps(in_serial, sense_ser):
	voltage=0
	iso_amp_gain=4.04
	amp_gain=3
	print "battery current"
	while(in_serial != "end\n"):
		if(sense_ser.inWaiting() !=0):
			in_serial = sense_ser.readline()
			if(in_serial!="end\n"):
				temp_i.append(in_serial)
	
	for element in temp_i:
		voltage += (((float(element)*5/4096)/amp_gain)/iso_amp_gain)/0.005
	mean_voltage=voltage/len(temp_i)
	print mean_voltage
	text = font.render(str(mean_voltage), True, white)
	display.blit(text,(100, 150))
	del temp_i[:]
	return mean_voltage
# ###################################################################################################################################	
#Write All Data to database
# ###################################################################################################################################
def build_frames():
	EvData = zip(iBat, vBat, tBat, iCont, vCont, tCont, iMot, vMot, tMot, tempBat, tempBms, rpmMot, tSense)
	BatData = zip(iBat, vBat, tBat, cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8, cell9, cell10)
	evFrame=pd.DataFrame(data = EvData, columns = ['iBat', 'vBat', 'tBat', 'iCont', 'vCont', 'tCont', 'iMot', 'vMot', 'tMot', 'tempBat', 'tempBms', 'rpmMot', 'tSense'])
	batFrame=pd.DataFrame(data = BatData, columns = ['iBat', 'vBat', 'tBat', 'cell1', 'cell2', 'cell3', 'cell4', 'cell5', 'cell6', 'cell7', 'cell8', 'cell9', 'cell10'])
	return evFrame, batFrame
	
def to_db(operation, evFrame, batFrame): #operation = 'fail', 'replace', 'append'
	con = None
	try:
		con = sql.connect("pack.db")
		cur = con.cursor()
	except sql.Error, e:
		print "Error %s:" %e.args[0]
	evFrame.to_sql('EV', con, flavor='sqlite', schema=None, if_exists=operation, index=True, index_label=None, chunksize=None, dtype=None)
	batFrame.to_sql('BAT', con, flavor='sqlite', schema=None, if_exists=operation, index=True, index_label=None, chunksize=None, dtype=None)
	return
# ###################################################################################################################################	
# ###################################################################################################################################	
# 	                                            MAIN LOOP
# ###################################################################################################################################	
# ###################################################################################################################################	

status_bits = 0
evFrame, batFrame=build_frames()
to_db('replace',evFrame, batFrame)
while 1:
	display.fill(black)
	pygame.display.update()
	evFrame, batFrame=build_frames()
	to_db('append',evFrame, batFrame)
	try:
		while bms_ser.inWaiting() !=0:
			in_serial = bms_ser.readline()
			if(in_serial == "cell voltages = \r\n"):
				in_serial = bms_ser.readline()# get stack voltages
				
				read_bat(in_serial, 1) #process the battery cell value readings place them in bat_levels variable
				for x in range(0, len(bat_levels)): 		# create a column for each cell
					battery_cell(bat_levels[x], cell_value[x], x*12 , 20) #pass the cell you want to render and its value.
				 
			elif(in_serial == "status bits = \r\n"):
				status_bits = bms_ser.readline()
				
				 
			elif(in_serial == "Pack Current = \r\n"):
				pack_current = float(bms_ser.readline()) # get stack current
				
				stack_current(pack_current, 1)# display current as a bar
				 
				 
				db.pack_state(stackA, cell_value, pack_current, status_bits, datetime.datetime.now())# write cell voltages, stack current, and status to database
	except:
		pass #if bms not plugged in do nothing
	#try:		
	# ###################################################################################################################################
	while sense_ser.inWaiting() !=0:
		in_serial=sense_ser.readline()
		if(in_serial=="temperatures = \r\n"):
			in_serial = sense_ser.readline() # get temperatures 
			temp = in_serial.split() #split on whitespace
			display_temp(temp)
			tempBat[0]=temp[0]
			tempBms[0]=temp[1]
			tempMot[0]=temp[2]
			print temp
		elif(in_serial == "rpm = \r\n"):
			t = unicode(datetime.datetime.now())
			in_serial = sense_ser.readline() # get hall effect speeds 
			rpm = in_serial.split()
			print rpm
			display_speed(rpm)
			rpmMot[0]=552.1 #float(rpm)
			
			tSense[0]=t
		elif(in_serial == "battery voltage = \n"):
			vBat[0]=bat_volts(in_serial, sense_ser)
		elif(in_serial == "battery current = \n"):
			t = unicode(datetime.datetime.now())
			iBat[0]=bat_amps(in_serial, sense_ser)
			
			tBat[0]=t
# ###################################################################################################################################					
	#except:
		#pass
			
	

	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				print 'stop'
				pygame.quit()
				sys.exit()
			if event.key == pygame.K_r:
				pygame.display.update()
# ###################################################################################################################################	
# ###################################################################################################################################	

