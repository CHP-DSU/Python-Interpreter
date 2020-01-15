import socket
from threading import *
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "172.16.68.107" 
port = 8000
print (host)
print (port)
serversocket.bind((host, port))
sendCommand = ""
confirmation = "Cannot connect to device"

class client(Thread):
	def __init__(self, socket, address):
		Thread.__init__(self)
		self.sock = socket
		self.addr = address
		print("Connection Received From:\t> " + str(self.addr))
		self.start()
	
	
	def bluetoothConnect(self):
		ble = Adafruit_BluefruitLE.get_provider()

		def mainBluetooth():
			global sendCommand
			global confirmation
			# Clear any cached data
			ble.clear_cached_data()

			# Get first available adapter and make sure it is powered on
			adapter = ble.get_default_adapter()
			adapter.power_on()
			print("Using adapter: {0}".format(adapter.name))

			# Disconnect any currently connected devices
			print("Disconnecting any connected UART devices...")
			UART.disconnect_devices()

			# Scan for UART devices
			print("Searching for UART device...")
			try:
				adapter.start_scan()
				device = UART.find_device()
				if device is None:
					raise RuntimeError("Failed to find UART device!")
			finally:
				adapter.stop_scan()

			print("Connecting to device...")
			device.connect()

			try:
				print("Discovering services...")
				UART.discover(device)

				# Create instance to interact with
				uart = UART(device)

				sendCommand = sendCommand.encode()
				uart.write(b"%b" % (sendCommand))
				received = uart.read(timeout_sec=10)
				if received is not None:
					print("Received: {0}".format(received))
					confirmation = "Received: " + received
				else:
					print("Received no data!")
					confirmation = "Received no data!"
			finally:
				device.disconnect()

		# Initialize the BLE system
		ble.initialize()

		# Start the mainloop process
		ble.run_mainloop_with(mainBluetooth)

	def run(self):
		global sendCommand
		global confirmation
		try:
			while 1:
				data = self.sock.recv(1024).decode()
				if data:
					print('Client sent: ' + data)
					data = data.split(" ")
					if data[0].lower() == "set":
						sendCommand = data[0].upper() + " " + data[2]
					elif data[0].lower() == "query":
						sendCommand = "RQT"
					self.sock.send(b'Connection Success')
					try:
						self.bluetoothConnect()
					except:
						print("BROKE")
					self.sock.send(confirmation.encode())
				else:
					self.sock.send(b'No info sent')
		except:# (Exception) as e:
			#print(e)
			self.sock.close()
			print("Connection Closed on Address\t> " + str(self.addr))

serversocket.listen(5)
print ('server started and listening')
while 1:
	clientsocket, address = serversocket.accept()
	client(clientsocket, address)
