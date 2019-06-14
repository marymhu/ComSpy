import serial
import time
import datetime
import os
import configparser

# Port Configuration
BAUDRATE = 115200
BYTESIZE = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOPBITS = serial.STOPBITS_ONE
HEADER = [0x1, 0xFF, 0x2]
# Initialisation of the serial port
# - timeout = 1.0 forces the method of 'port' to stop if nothing is read during 1 seconds
# - write_timeout = 1.0 forces the method write to stop if nothing is written during 1 seconds


class ComSpy:
   def __init__(self, logger="log", log_path = ""):
      cur_path = os.path.dirname(os.path.abspath(__file__))
      config = configparser.ConfigParser()
      config.read(os.path.join(cur_path, 'config.ini'))
      port1_value = config['SERIAL']['PORT1']
      port2_value = config['SERIAL']['PORT2']
      read_timeout =  float(config['SERIAL']['READ_TIMEOUT'])
      write_timeout =  float(config['SERIAL']['WRITE_TIMEOUT'])
      inter_byte_timeout =  float(config['SERIAL']['INTER_BYTE_TIMEOUT'])
      self.name1 = config['SERIAL']['NAME1']
      self.name2 = config['SERIAL']['NAME2']
      self.new_msg_timeout = float(config['SERIAL']['NEW_MSG_TIMEOUT'])

      self.port1 = serial.Serial(port              = port1_value,
                                baudrate           = BAUDRATE,
                                bytesize           = BYTESIZE,
                                parity             = PARITY,
                                stopbits           = STOPBITS,
                                timeout            = read_timeout,
                                xonxoff            = False,
                                rtscts             = False,
                                dsrdtr             = False,
                                write_timeout      = write_timeout,
                                inter_byte_timeout = inter_byte_timeout)

      self.port2 = serial.Serial(port              = port2_value,
                                baudrate           = BAUDRATE,
                                bytesize           = BYTESIZE,
                                parity             = PARITY,
                                stopbits           = STOPBITS,
                                timeout            = read_timeout,
                                xonxoff            = False,
                                rtscts             = False,
                                dsrdtr             = False,
                                write_timeout      = write_timeout,
                                inter_byte_timeout = inter_byte_timeout)

      self.log_name = os.path.join(log_path, logger.lower() + ".txt")
      self.log_file = open(self.log_name, 'w', 1)
      self.buffer_1 = []
      self.buffer_2 = []

   def log (self, event, msg = ""):
      """
      Add entry to log with input/output messages
      """
      item = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S.%f")[:-3]
      item += ' - '+ event
      if msg:
         item += ': ' + str(msg)
      item += '\n'
      self.log_file.write(item)
      if self.log_name == "log.txt":
         print(item)


   def forwarding_bytes(self, from_port, to_port):
      nb_bytes_received = from_port.inWaiting()
      data_received = []
      if nb_bytes_received > 0:
         nb_bytes_received = from_port.inWaiting()
         data_received = from_port.read(nb_bytes_received)
         to_port.write(data_received)
      return data_received, nb_bytes_received


   def bufferize(self, msg_buffer, received_bytes):
      msg_buffer += received_bytes
      # Remove noise
      if msg_buffer[:3] != HEADER:
         msg_buffer = []
      return msg_buffer


if __name__ == '__main__':
   protocol = ComSpy()
   buffer_from_1 = []
   buffer_from_2 = []
   nb_bytes_from_1 = 0
   nb_bytes_from_2 = 0
   bytes_received_from_1 = []
   bytes_received_from_2 = []
   t_1 = 0.0
   t_2 = 0.0

   print("Messages exchanged will be logged in file " + protocol.log_name + ". Type Ctrl-C to stop.")
   while True:
      try:
         # Forwarding all bytes from one interface to the other
         bytes_received_from_1, nb_bytes_from_1 = protocol.forwarding_bytes(protocol.port1, protocol.port2)
         bytes_received_from_2, nb_bytes_from_2 = protocol.forwarding_bytes(protocol.port2, protocol.port1)

         # Gathering received bytes from both interfaces (must start with HEADER)
         if nb_bytes_from_1 > 0:
            protocol.buffer_1 = protocol.bufferize(protocol.buffer_1, bytes_received_from_1)
            t_1 = time.time()

         if nb_bytes_from_2 > 0:
            protocol.buffer_2 = protocol.bufferize(protocol.buffer_2, bytes_received_from_2)
            t_2 = time.time()


         # After a timeout, message is considered received and logged
         if time.time() - t_1 > protocol.new_msg_timeout and protocol.buffer_1:
            message_ready = " ".join(hex(b) for b in protocol.buffer_1)
            protocol.log(protocol.name1 + " -> " + protocol.name2, message_ready)
            protocol.buffer_1 = []

         if time.time() - t_2 > protocol.new_msg_timeout and protocol.buffer_2 :
            message_ready = " ".join(hex(b) for b in protocol.buffer_2)
            protocol.log(protocol.name2 + " -> " + protocol.name1, message_ready)
            protocol.buffer_2 = []

      except KeyboardInterrupt:
         print ("Closing log file")
         protocol.log_file.close()
         exit(0)







