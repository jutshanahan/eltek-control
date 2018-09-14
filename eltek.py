import socket, sys, struct, signal, codecs, subprocess, time, threading 
from time import sleep

#/etc/network/interfaces
	#allow-hotplug can0
	#iface can0 can static
	#        bitrate 125000
	#        up ip link set $IFACE txqueuelen 1000

# https://endless-sphere.com/forums/viewtopic.php?f=14&t=71139https://endless-sphere.com/forums/viewtopic.php?f=14&t=71139&sid=6dda9684374755f76d107f6698b01976&start=50


# eltek SN :  163471014351




class RepeatedTimer(object):
	def __init__(self, interval, function, *args, **kwargs):
		self._timer = None
		self.interval = interval
		self.function = function
		self.args = args
		self.kwargs = kwargs
		self.is_running = False
		self.next_call = time.time()
		self.start()

	def _run(self):
		self.is_running = False
		self.start()
		self.function(*self.args, **self.kwargs)

	def start(self):
		if not self.is_running:
			self.next_call += self.interval
			self._timer = threading.Timer(self.next_call - time.time(), self._run)
			self._timer.start()
			self.is_running = True

	def stop(self):
		self._timer.cancel()
		self.is_running = False
		




def signal_handler(signal, frame):
	# print(' you next time.')
	try:
		set_vout_iout(float(input("voltage?  ")),float(input("current?  ")),input("permanent?  "))
	except:
		sock.close()
		sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)


interface = "can0"
try:
	sock.bind((interface,))
except OSError as err:
	sys.stderr.write("Could not detect usb CAN dongle '%s'\n" % interface)
	print("OS error: {0}".format(err))
	sys.exit(0)
	# do something about the error...


fmt = "<IB3x8s"


lastTime=time.time()
startTime=time.time()
lastPrint=0
wtf= 5

run = 0

Ah = 0
Wh = 0

def login():
	cantxid =0x85004808
	if eltekSN != 0:
		# frame=struct.pack(fmt,cantxid,8,b'\x16\x34\x71\x01\x43\x51\x00\x00')	
		frame=struct.pack(fmt,cantxid,8,eltekSN.to_bytes(6,'big',signed="False"))
		sock.send(frame)

def print_info(id,msg):

	if eltekSN != 0:
	
		global lastTime, Ah, Wh
		
		now = time.time()
		dT = now - lastTime
		lastTime = now
			
		
		if (id == 0x85024004) or (id == 0x85024008):
			# print ("msg=",msg)
			tin,iout,vout,vin,tout = struct.unpack('<BhhhB',msg)
			vout = vout/100.0
			vpercell = round(vout/14,3)
			iout = iout/10.0
			iin = round(vout*iout/0.9/vin,1)
			power = int(vout*iout)
			
			Ah += dT/3600.0 * iout
			Wh += dT/3600.0 * power
			
			Ah = round(Ah,3)
			Wh = round(Wh,3)
			
			if id == 0x85024004: mode = "CV"
			if id == 0x85024008: mode = "CC"
			
			# print(tin,'=>',tout,'C','\t',vin,'AC =>',vout,'DC\r', end='\r', flush=True)
			print(('%dC->%dC' % (tin,tout)),'\t',vin,'VAC,',iin,'IAC =>',('%2.2f' % vout),'VDC, ',('(%1.3f V/cell)' % vpercell),('%2.2f' % iout),'A\t',Ah,'Ah',mode,('%4d' % power),'W',Wh,'Wh')
			
			# the status messages are (like described earlier in the thread) :
			# 0x05014010 AA BB CC DD EE FF GG HH where 
			# AA is the intake temperature in Celcius
			# BB is the output current Low Byte
			# CC is the output current High Byte. the current high and low byte combined give the current in deci amps (* 0.1 Amp)
			# DD is the output voltage Low byte
			# EE is the output voltage High Byte. the voltage high and low byte combined give the voltage in centivolts (* 0.01 Volt)
			# FF is the input voltage Low Byte
			# GG is the input voltage High Byte. the input voltage high and low byte combined gives the AC input voltage in volts
			# HH is the output temperature in Celcius
			
			# ex
			# 0x150000f214750023
			# 0x15 0000 f214 7500 23
		
		
		
def set_vout_iout(vout,iout,perm="n",ovp=59.5):

	vout = int(vout * 100.0)
	ovp = int(ovp * 100.0)
	iout = int(iout * 10.0)
	
	if perm == 'y':
		data = struct.pack("<BBBh",0x29,0x15,0x00,vout)
		frame=struct.pack(fmt,0x85029C00,5,data)
		sock.send(frame)
		
		# id 05 01 9C 00, dlc = 5, data = 29 15 00 <FE 10>

	# 01=Rectifier Number 01
	# FE 10 = 43.50 volts, same codage as already explained.
		
		
	
	data = struct.pack("<hhhh",iout,vout,vout,ovp)
	frame=struct.pack(fmt,0x85FF4004,8,data)
	
	
	sock.send(frame)

# String for voltage setting : "send 05 FF 40 04 header and 8 bytes AA BB CC DD EE FF GG HH" 

# Where :
# BBAA (in HEX!) is the maximum current setting
# (I have set it at A2 01 for 41.8 Amps (1820 Watts divided by 43.5 Volt which is the lowest voltage setting) 

# DDCC (in HEX!) is the system voltage measurement
# (no idea what it really does but i have set this the same as th e output voltage setting so 80 16)

# FFEE (in HEX!) is the output voltage in centivolts (0.01V)
# (I have set this at 80 16 for 57.6 Volt which is the highest voltage setting)

# HHGG (in HEX!) is the overvoltage protection setting (I have set this at 3E 17 for 59.5 Volts)

# So the complete string for setting the maximum voltage (57.6V) and maximum current is : 05 FF 40 04 header and 8 bytes A2 01 80 16 80 16 3E 17
		



rt1 = RepeatedTimer(5, login) # it auto-starts, no need of rt.start()
# rt2 = RepeatedTimer(1, print_info) # it auto-starts, no need of rt.start()

choice=0

eltekSN = 0

len(sys.argv)



try:
	while 1:

		try:
			canid,canlen,candata=struct.unpack(fmt,sock.recv(16))
			# canid = canid & 0x7fffffff
			
			if ((canid & 0xFFFF000) == 0x5000000) and eltekSN==0:
			# if canid == 0x85024400:
				eltekSN = (int.from_bytes(candata, 'big') >> 8) & 0xFFFFFFFFFFFF
				print("eltekSN",hex(eltekSN))
				lastTime = time.time()
				
				
				if len(sys.argv) == 3:
					set_vout_iout(float(sys.argv[1]),float(sys.argv[2]),"n")

			
			
			if eltekSN != 0:
				now = time.time()
				if now - lastPrint > 1:
					print_info(canid,candata)
					lastPrint = now
				
			
			 # can0  05024004   [8]  15 00 00 F0 14 76 00 23
			
			# print ("og cd=",ogcandata)

			
			# candata = int.from_bytes(candata, 'big', signed=True)
			# candata = struct.unpack(">L", candata)[0]
			# candata=struct.unpack("<L", candata)[0]
			
			

			# print ("socket.CAN_EFF_FLAG=",socket.CAN_EFF_FLAG)
			# cantxid =0x4808 | socket.CAN_EFF_FLAG
			# if login == True:
			

		except OSError as err:
			print("OS error: {0}".format(err))


finally:
	rt1.stop() # better in a try/finally block to make sure the program ends!
