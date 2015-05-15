import pygame, sys, time, serial
from pygame.locals import *

red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
darkBlue = (0,0,128)
white = (255,255,255)
black = (0,0,0)
pink = (255,200,200)

bat_levels = [1]*40
bat_cell_height = 10



def draw_square(square_size,locX,locY, win):
	pygame.draw.rect(win, red, (locX,locY,square_size,square_size), 2)
	pygame.display.update()
	return
	
def battery_cell(level, locX, locY, win):
	if level < 5:
		color = red
	else:
		color = green
	for L in range(0, level):
		pygame.draw.rect(win, color, (locX,500-locY-L*bat_cell_height,bat_cell_height,bat_cell_height), 1)
	return

def init():
	
	try:
		bms_ser = serial.Serial('/dev/ttyACM0', 9600)
		print "BMS present"
	except:
		print "BMS not plugged in"

	try:  
		pygame.init()
		pygame.font.init()
		print "pygame initialized"
	except:
		print "pygame failed to initialize"
	bat_dis = pygame.display.set_mode((500, 500))
	pygame.display.set_caption('Battery Level indicator')

	return bat_dis, bms_ser
	
def read_bat(line, pack):
	f10 = line.split(' ')
	if(pack ==1):
		for x in range(0, 10):
			bat_levels[x] = float(f10[x])
			bat_levels[x] = int(((bat_levels[x]-2.8)/1.1)*10)
	print type(bat_levels)
	print bat_levels
	
	return

def main():	
	display, ser = init()

	while 1:
		while ser.inWaiting() !=0:
			in_serial = ser.readline()
			if(in_serial == "cell voltages = \r\n"):
				print in_serial
				in_serial = ser.readline()
				read_bat(in_serial, 1)
				for x in range(0, len(bat_levels)):
					battery_cell(bat_levels[x], x*12 , 10, display)
				pygame.display.update()
				


		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					print 'stop'
					pygame.quit()
					sys.exit()
				if event.key == pygame.K_r:
					pygame.display.update()
main()
