import socket, sys, struct, signal, codecs, subprocess, time


# https://endless-sphere.com/forums/viewtopic.php?f=14&t=71139


def signal_handler(signal, frame):
	print(' you next time.')
	sock.close()
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)


#print(help(sock))
interface = "can0"
try:
	sock.bind((interface,))
except OSError as err:
	sys.stderr.write("Could not detect usb CAN dongle '%s'\n" % interface)
	print("OS error: {0}".format(err))
	sys.exit(0)
	# do something about the error...


fmt = "<IB3x8s"
#can_pkt = struct.pack(fmt, 0x741, len(b"hello"), b"hello")
#sock.send(can_pkt)

# print (sock)

#id=0x570		# CAN ID 0x570 =  PODDBG00_10Hz messages, which has cell voltages/temperatures
#mask=0xffff
#sock.setsockopt(socket.SOL_CAN_RAW, socket.CAN_RAW_FILTER, struct.pack("II", id, mask)) 


# turn off power and wake line to the pod
#can_pkt=struct.pack(fmt,0x777,1,b'\x00')
#sock.send(can_pkt)

lastTime=time.time()
startTime=time.time()

def login():
	cantxid =0x85004808
	can_pkt=struct.pack(fmt,cantxid,8,b'\x16\x34\x71\x01\x43\x51\x00\x00')	
	sock.send(can_pkt)

def mon_status(id,msg):
	
	if (id == 0x85024004) or (id == 0x85024008):
		# print ("msg=",msg)
		tin,iout,vout,vin,tout = struct.unpack('<BhhhB',msg)
		vout = vout/100.0
		iout = iout/10.0
		
		# print(tin,'=>',tout,'C','\t',vin,'AC =>',vout,'DC\r', end='\r', flush=True)
		print(tin,'=>',tout,'C','\t',vin,'AC =>',vout,'VDC, ',iout,'ADC\t',vout*iout,'W')
		
		# ovH = (msg >> 8*3) & 0xFF
		# ovL = (msg >> 8*4) & 0xFF
		# print (ovH<<8+ovL,"V")
		
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
		
	if id == 0x805024400:
		print("id")
		
		
def set_vout_iout(vout=50.0,iout=5.0,ovp=59.5):

	vout = int(vout * 100.0)
	ovp = int(ovp * 100.0)
	iout = int(iout * 10.0)
	msg = struct.pack("<hhhh",iout,vout,vout,ovp)
	print ("msg=",msg,len(msg))
	can_pkt=struct.pack(fmt,0x85FF4004,8,msg)
	# can_pkt=struct.pack(fmt,cantxid,8,b'\x16\x34\x71\x01\x43\x51\x00\x00')	
	sock.send(can_pkt)

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
		
print_status = False

while 1:

	login()
	
	print ("1. log in")
	print ("2. monitor status")
	print ("3. set voltage/current")
	
	choice = int(input("?  "))
	
	if choice == 1:
		# login = True
		pass
		
	if choice == 2:
		print_status = True
		
	if choice == 3:
			
		set_vout_iout(float(input("voltage?  ")),float(input("current?  ")))
		


	try:
		canid,canlen,candata=struct.unpack(fmt,sock.recv(16))
		# canid = canid & 0x7fffffff
		canid = canid
		
		
		if print_status == True:
			mon_status(canid,candata)
		
		 # can0  05024004   [8]  15 00 00 F0 14 76 00 23
		
		# print ("og cd=",ogcandata)
		
		# candata = int.from_bytes(candata, 'big', signed=True)
		candata = int.from_bytes(candata, 'big')
		# candata = struct.unpack(">L", candata)[0]
		# candata=struct.unpack("<L", candata)[0]
		
		# candata = candata.hex()
		

		# print ("socket.CAN_EFF_FLAG=",socket.CAN_EFF_FLAG)
		# cantxid =0x4808 | socket.CAN_EFF_FLAG
		# if login == True:
		

	except OSError as err:
		print("OS error: {0}".format(err))
