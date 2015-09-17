import pygame, sys, time, serial, datetime, math, os
from pygame.locals import *
import pandas as pd
import sqlite3 as sql
import wiringpi2 as wp



# ###################################################################################################################################	
# ###################################################################################################################################
#zero crossing detection flags

logged = datetime.datetime.now()
displayed = logged
current_time=logged
serial_time=logged
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
cell_value = [2.0]*10 #lists 40 elements long initialized with value [#]
bat_cell_height = 20
bat_pack_height = 1
temp_v=[0]
temp_i=[0]
bat_voltage_roll=[]
mot_voltage_roll=[]
status_bits = 0
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
tempCont=[25.0]
rpmMot=[0.1]
tSense=[unicode(datetime.datetime.now())]
cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8, cell9, cell10 =[0], [0], [0], [0], [0], [0], [0], [0], [0], [0]

EvData = zip(iBat, vBat, tBat, iCont, vCont, tCont, iMot, vMot, tMot, tempBat, tempBms, tempCont, rpmMot, tSense)
BatData = zip(iBat, vBat, tBat, cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8, cell9, cell10)

time_log=0
new_log=2
rpm_log=3

#setup wiringpi and set button pins as inputs (internal pullup enabled)
wp.wiringPiSetup()
wp.pinMode(time_log, 0)
wp.pinMode(new_log, 0)
wp.pinMode(rpm_log, 0)
wp.pullUpDnControl(time_log, 2)
wp.pullUpDnControl(new_log, 2)
wp.pullUpDnControl(rpm_log, 2)


# ###################################################################################################################################	
# ###################################################################################################################################		
try:
	bms_ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)
	print "BMS present"
except:
	print "BMS not plugged in"
try:
	sense_ser = serial.Serial('/dev/ttyACM1', 115200, timeout=0)
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
def stack_current(current, stack):
	pygame.draw.rect(display, white, (0,152,32,104), 1)	
	for L in range(0, int(current*10)):
		pygame.draw.rect(display, blue, (1,250-int(L*bat_pack_height),30,1), 1)		


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
# ###################################################################################################################################	
def rms_volts(in_serial, sense_ser):
	voltage_sum=0
	voltage_wave=[]
	voltage_mean=0
	zero_cross=0
	vrms=0
	period_flag=False
	end_period_flag=False
	
	print "motor voltage"
	while(in_serial != "end\n"):
		if(sense_ser.inWaiting() !=0):
			in_serial = sense_ser.readline()
			if(in_serial!="end\n"):
				temp_v.append(in_serial)
		
	#convert each adc reading to a current and sum
	for element in temp_v:
	#try:
		if 2000<=int(element)<=2100:	#zero crossing detection ensures one full period is sampled
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
	voltage_mean=voltage_sum/len(temp_v)
	#get square root of mean = rms value
	vrms=math.sqrt(voltage_mean)

	#print max(voltage_wave)-min(voltage_wave)
	del voltage_wave[:]	
	del temp_v[:]
	sense_ser.write("a")#acknowledge that voltage has been received
	return vrms
	
def rms_amps(in_serial, sense_ser):
	current_sum=0
	current_wave=[]
	current_mean=0
	zero_cross=0
	irms=0
	period_flag=False
	end_period_flag=False
	
	print "motor current"
	while(in_serial != "end\n"):
		if(sense_ser.inWaiting() !=0):
			in_serial = sense_ser.readline()
			if(in_serial!="end\n"):
				temp_i.append(in_serial)
	
	
	#convert each adc reading to a current and sum
	for element in temp_i:
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
	current_mean=current_sum/len(temp_i)
	#get square root of mean = rms value
	irms=math.sqrt(current_mean)
	#print max(current_wave)-min(current_wave)
	del current_wave[:]	
	del temp_i[:]
	sense_ser.write("a") #acknowledge
	return irms
# ###################################################################################################################################	
#Battery voltage calculator
# ###################################################################################################################################
def mot_volts(in_serial, sense_ser):
	bat_voltage_sum=0
	voltage=0
	roll_avg=0
	volt_div=243.03
	iso_amp_gain=4.04
	amp_gain=7
	
	print "battery voltage"
	while(in_serial != "end\n"):
		if(sense_ser.inWaiting() !=0):
			in_serial = sense_ser.readline()
			if(in_serial!="end\n"):
				temp_v.append(in_serial)
	
	for element in temp_v:
		voltage += (((float(element)*5/4096)/amp_gain)/iso_amp_gain)*volt_div
	mean_voltage=voltage/len(temp_v)
	#keep a rolling average of battery voltage
	mot_voltage_roll.append(mean_voltage)
	if(len(mot_voltage_roll)>2):
		del mot_voltage_roll[0]
	for element in mot_voltage_roll:
		bat_voltage_sum+=element
	roll_avg = bat_voltage_sum/len(mot_voltage_roll)
	bat_voltage_sum=0
	text = font.render(str(roll_avg), True, white)
	display.blit(text,(100, 300))
	del temp_v[:]
	#print roll_avg
	sense_ser.write("a") #acknowledge that voltage has been received
	return roll_avg	 

def bat_volts(in_serial, sense_ser):
	bat_voltage_sum=0
	voltage=0
	roll_avg=0
	volt_div=243.03
	iso_amp_gain=4.04
	amp_gain=3
	
	print "battery voltage"
	while(in_serial != "end\n"):
		if(sense_ser.inWaiting() !=0):
			in_serial = sense_ser.readline()
			if(in_serial!="end\n"):
				temp_v.append(in_serial)
	
	for element in temp_v:
		voltage += (((float(element)*5/4096)/amp_gain)/iso_amp_gain)*volt_div
	mean_voltage=voltage/len(temp_v)
	#keep a rolling average of battery voltage
	bat_voltage_roll.append(mean_voltage)
	if(len(bat_voltage_roll)>2):
		del bat_voltage_roll[0]
	for element in bat_voltage_roll:
		bat_voltage_sum+=element
	roll_avg = bat_voltage_sum/len(bat_voltage_roll)
	bat_voltage_sum=0
	text = font.render(str(roll_avg), True, white)
	display.blit(text,(100, 300))
	del temp_v[:]
	#print roll_avg
	sense_ser.write("a") #acknowledge that voltage has been received
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
		voltage += ((((float(element)-2040)*5/4096)/amp_gain)/iso_amp_gain)/0.005
	mean_voltage=voltage/len(temp_i)
	#print mean_voltage
	text = font.render(str(mean_voltage), True, white)
	display.blit(text,(100, 150))
	del temp_i[:]
	sense_ser.write("a") #acknowledge
	return mean_voltage
# ###################################################################################################################################	
#Write All Data to database
# ###################################################################################################################################
def build_frames():
	cell1[0], cell2[0], cell3[0], cell4[0], cell5[0], cell6[0], cell7[0], cell8[0], cell9[0], cell10[0] = cell_value[0], cell_value[1], cell_value[2], cell_value[3], cell_value[4], cell_value[5], cell_value[6], cell_value[7], cell_value[8], cell_value[9]
 	EvData = zip(iBat, vBat, tBat, iCont, vCont, tCont, iMot, vMot, tMot, tempBat, tempBms, tempCont, rpmMot, tSense)
	BatData = zip(iBat, vBat, tBat, cell1, cell2, cell3, cell4, cell5, cell6, cell7, cell8, cell9, cell10)
	#build data frames using pandas
	evFrame=pd.DataFrame(data = EvData, columns = ['iBat', 'vBat', 'tBat', 'iCont', 'vCont', 'tCont', 'iMot', 'vMot', 'tMot', 'tempBat', 'tempBms', 'tempCont', 'rpmMot', 'tSense'])
	batFrame=pd.DataFrame(data = BatData, columns = ['iBat', 'vBat', 'tBat', 'cell1', 'cell2', 'cell3', 'cell4', 'cell5', 'cell6', 'cell7', 'cell8', 'cell9', 'cell10'])
	return evFrame, batFrame
	
def to_db(operation, evFrame, batFrame): #operation = 'fail', 'replace', 'append'
	con = None
	#connect to database
	try:
		con = sql.connect("pack.db")
		cur = con.cursor()
	except sql.Error, e:
		print "Error %s:" %e.args[0]
	#write data frames to database using pandas built in sqlite3 support
	evFrame.to_sql('EV', con, flavor='sqlite', schema=None, if_exists=operation, index=True, index_label=None, chunksize=None, dtype=None)
	batFrame.to_sql('BAT', con, flavor='sqlite', schema=None, if_exists=operation, index=True, index_label=None, chunksize=None, dtype=None)
	return
def new_db():
	dir_t = str(datetime.datetime.now()).rstrip("0")
	dir_t=dir_t.replace("-", "")
	dir_t=dir_t.replace(" ", "-")
	print dir_t
	os.system("cd /home/pi/EVPI")
	try:
		os.system("sudo cp /home/pi/EVPI/scada/pack.db /home/pi/EVPI/db_backup/{0}.db".format(dir_t[2:17]))
	except:
		print "pack.db does not exist"
	evFrame, batFrame=build_frames()
	to_db('replace',evFrame, batFrame)
	return
# ###################################################################################################################################	
#Display Functionality
# ###################################################################################################################################
def update_display(display, evFrame, batFrame):
	display.fill(black)
	for x in range(0, 40):
		pygame.draw.rect(display, white, (x*12,500-0,bat_cell_height*10,11), 1)
	pygame.draw.rect(display, red, pygame.Rect(0, 30, 300, 60), 8)
	text = font.render("Temperatures", True, white)
	display.blit(text,(0, 0))
	text = font.render("Battery", True, white)
	display.blit(text,(10, 40))
	text = font.render("BMS", True, white)
	display.blit(text,(100 , 40))
	text = font.render("Controller", True, white)
	display.blit(text,(200, 40))
	#temperatures
	text = font.render(str(evFrame.tempBat[0]), True, white)
	display.blit(text,(10, 60))
	text = font.render(str(evFrame.tempBms[0]), True, white)
	display.blit(text,(100, 60))
	text = font.render(str(evFrame.tempCont[0]), True, white)
	display.blit(text,(200, 60))
	
	pygame.draw.rect(display, blue, pygame.Rect(310, 30, 100, 60), 8)
	text = font.render("RPM", True, white)
	display.blit(text,(320, 0))
	#speeds
	text = font.render(str(evFrame.rpmMot[0]), True, white)
	display.blit(text,(320, 40))
	
	pygame.draw.rect(display, blue, pygame.Rect(8, 150, 484, 104), 8)
	pygame.draw.rect(display, red, pygame.Rect(0, 142, 500, 120), 8)
	text = font.render("POWER LEVELS", True, white)
	display.blit(text,(150, 105))
	text = font.render(str(evFrame.vBat[0])[:4], True, white)
	display.blit(text,(20, 170))
	text = font.render("V", True, white)
	display.blit(text,(60, 170))
	text = font.render(str(evFrame.iBat[0])[:4], True, white)
	display.blit(text,(20, 200))
	text = font.render("A", True, white)
	display.blit(text,(60, 200))
	text = font.render(str(evFrame.vMot[0])[:4], True, white)
	display.blit(text,(250, 170))
	text = font.render("V", True, white)
	display.blit(text,(290, 170))
	text = font.render(str(evFrame.iMot[0])[:4], True, white)
	display.blit(text,(250, 200))
	text = font.render("A", True, white)
	display.blit(text,(290, 200))
	
	#speeds
	#render pack voltage levels
	for x in range(0, 10): 		# create a column for each cell
		battery_cell(bat_levels[x], cell_value[x], x*30 , 50) #pass the cell you want to render and its value.	
	
	pygame.display.update()
	return

#battery cell receives the voltage level of a single cell and plots a bar graph at the specified location
def battery_cell(level, cell_val, locX, locY):
	color = white
	if level < 5:
		color = red
	elif cell_val>4:
		colour = blue
	else:
		color = green
	for L in range(0, level):
		pygame.draw.rect(display, color, (locX+100,100+500-locY-L*30,bat_cell_height,bat_cell_height), 1)
	
	temp_text = str(cell_val)
	if len(temp_text)>3:
		temp_text = temp_text[:-1] #strip the last character from the string
	text = font.render(temp_text, True, white)
	display.blit(text,(locX // 1, 520-locY - text.get_height() // 1))
	return
# ###################################################################################################################################	
#Serial port functionality
# ###################################################################################################################################

	


# ###################################################################################################################################	
# ###################################################################################################################################	
# 	                                            MAIN LOOP
# ###################################################################################################################################	
# ###################################################################################################################################	

while 1:
	current_time = datetime.datetime.now()
	if current_time-displayed>datetime.timedelta(seconds=1): #log data every 20 seconds in this mode
		evFrame, batFrame=build_frames()
		update_display(display, evFrame, batFrame)
		displayed = datetime.datetime.now()
	
	if wp.digitalRead(new_log)==0:
		print "NEW DATABASE"
		new_db() #backup the database and clear it
	if wp.digitalRead(time_log)==0:
		if current_time-logged>datetime.timedelta(seconds=10): #log data every 20 seconds in this mode
			evFrame, batFrame=build_frames()
			to_db('append',evFrame, batFrame)
			sense_ser.flushInput()
			print "TIME LOG"
			logged=datetime.datetime.now()
			
	elif wp.digitalRead(rpm_log)==0:
		if current_rpm-previous_rpm>=10: #log data every 10 rpm in this mode
			print "RPM LOG"
	try:
		while bms_ser.inWaiting() !=0:
			in_serial = bms_ser.readline()
			if(in_serial == "cell voltages = \r\n"):
				#print "Receiving cell voltages"
				in_serial = bms_ser.readline()# get stack voltages
				
				read_bat(in_serial, 1) #process the battery cell value readings place them in bat_levels variable
			elif(in_serial == "status bits = \r\n"):
				#print "Receiving cell status"
				status_bits = bms_ser.readline()
			elif(in_serial == "Pack Current = \r\n"):
				#print "Receiving cell current"
				pack_current = float(bms_ser.readline()) # get stack current
				stack_current(pack_current, 1)# display current as a bar
	except:
		pass #if bms not plugged in do nothing
	#try:		
	# ###################################################################################################################################
	while sense_ser.inWaiting() !=0:
		in_serial=sense_ser.readline()
		if(in_serial=="temperatures = \r\n"):
			print "TEMPERATURES"
			in_serial = sense_ser.readline() # get temperatures 
			temp = in_serial.split() #split on whitespace
			try:
				tempBat[0]=temp[0]
				tempBms[0]=temp[1]
				tempCont[0]=temp[2]
				print tempBat[0], tempBms[0], tempCont[0]
			except:
				pass #if temperature error skip this recording
			#print temp
		elif(in_serial == "rpm = \r\n"):
			t = unicode(datetime.datetime.now())
			in_serial = sense_ser.readline() # get hall effect speeds 
			rpm = in_serial.split()
			#print rpm
			rpmMot[0]=552.1 #float(rpm)
			tSense[0]=t
		elif(in_serial == "battery voltage = \n"):
			t = unicode(datetime.datetime.now())
			vBat[0]=bat_volts(in_serial, sense_ser)
			tBat[0]=t
		elif(in_serial == "battery current = \n"):
			iBat[0]=bat_amps(in_serial, sense_ser)
		elif(in_serial == "motor voltage = \n"):
			t = unicode(datetime.datetime.now())
			# ###################################################################################################################################
			#TESTING COMMENTS FOOLLLOW
			# ###################################################################################################################################
			vMot[0]=mot_volts(in_serial, sense_ser)#rms_volts(in_serial, sense_ser)
			tMot[0]=t
		elif(in_serial == "motor current = \n"):
			iMot[0]=rms_amps(in_serial, sense_ser)
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

