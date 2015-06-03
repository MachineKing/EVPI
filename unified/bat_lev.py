import pygame, sys, time, serial, datetime
from pygame.locals import *
import stack_db as db

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)

bat_levels = [1]*40
cell_value = [2.0]*40
bat_cell_height = 10
bat_pack_height = 1


stackA = "stack_one"
stackB = "stack_two"
stackC = "stack_three"
stackD = "stack_four"

	
try:
	bms_ser = serial.Serial('/dev/ttyACM0', 9600)
	print "BMS present"
except:
	print "BMS not plugged in"

try:  
	pygame.init()
	pygame.font.init()
	display = pygame.display.set_mode((500, 500))
	pygame.display.set_caption('Battery Level indicator')
	print "pygame initialized"
except:
	print "pygame failed miserably"
	
	
font = pygame.font.SysFont("arial", 9)



def draw_square(square_size,locX,locY):
	pygame.draw.rect(display, red, (locX,locY,square_size,square_size), 2)
	pygame.display.update()
	return

def setup_frames():
	for x in range(0, 40):
		pygame.draw.rect(display, white, (x*12,500-0,bat_cell_height*10,11), 1)
	return
	
def stack_current(current, stack):
	pygame.draw.rect(display, white, (0,152,32,104), 1)	
	for L in range(0, int(current*10)):
		pygame.draw.rect(display, blue, (1,250-int(L*bat_pack_height),30,1), 1)		

	
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

def main():	
	status_bits = 0
	while 1:
		display.fill(black)
		while bms_ser.inWaiting() !=0:
			in_serial = bms_ser.readline()
			if(in_serial == "cell voltages = \r\n"):
				in_serial = bms_ser.readline()# get stack voltages
				
				read_bat(in_serial, 1)
				for x in range(0, len(bat_levels)): 		# create a column for each cell
					battery_cell(bat_levels[x], cell_value[x], x*12 , 20) #pass the cell you want to render and its value.
				pygame.display.update()
			elif(in_serial == "status bits = \r\n"):
				status_bits = bms_ser.readline()
				
				pygame.display.update()
			elif(in_serial == "Pack Current = \r\n"):
				pack_current = float(bms_ser.readline()) # get stack current
				
				stack_current(pack_current, 1)# display current as a bar
				pygame.display.update()
			     
				db.pack_state(stackA, cell_value, pack_current, status_bits, datetime.datetime.now())# write cell voltages, stack current, and status to database
				
				
				
		

		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					print 'stop'
					pygame.quit()
					sys.exit()
				if event.key == pygame.K_r:
					pygame.display.update()
main()
