# Beep-Sat Advanced-2

🚧 under development 🚧

Need at least CP7.2, can download from ["Absolute Newest" section here](https://circuitpython.org/board/pycubed_v05/). use libs and tasks from this directory to ensure functionality

Advanced-2 introduces:
1. deep sleep functionality via `alarm` module. Enables things like wake-from-radio (aka "hot start") and improved low battery behavior
2. default cubesat "config" concept with on-chip or SD card loading. still deciding if I like this config approach. could change
3. multi-message OTA command mode. this allows you to chain OTA commands together by setting a flag
   <details>
   <summary>example "ground station" code for multi-msg demo</summary>
   <p>
   
   ```python
   import board
   import busio
   import digitalio
   import pycubed_rfm9x
   import time

   commands = {
       # command name : command code
       'no-op':b'\x8eb',       # does nothing
       'hreset':b'\xd4\x9f',   # hard reset
       ######## cmds with args ########
       'shutdown':b'\x12\x06', # shutdown sat
       'query':b'8\x93',       # eval
       'exec_cmd':b'\x96\xa2', # exec
   }


   CS = digitalio.DigitalInOut(board.RFM9X_CS)
   RESET = digitalio.DigitalInOut(board.RFM9X_RST)

   spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

   # Initialize RFM radio
   rfm9x = pycubed_rfm9x.RFM9x(spi=spi, cs=CS, reset=RESET, frequency=433.0, code_rate=8,baudrate=1320000)
   rfm9x.enable_crc=True
   rfm9x.ack_retries = 2
   rfm9x.ack_wait = 5
   rfm9x.node = 0xAB # this radio's radiohead ID
   rfm9x.destination = 0xFA # target sat's radiohead ID

   # initialize cmd variable with default pass-code
   cmd =  b'p\xba\xb8C'

   # next specify cmd by editing the string below
   CHOOSE_CMD = 'query'
   print('\nWill send command after hearing beacon:',CHOOSE_CMD)

   # then we add the cmd code for our chosen cmd string
   cmd += commands[CHOOSE_CMD]

   # finally we add any arguments (if necessary)
   # P.S. we're doing it this way to illustrate each piece that goes into the cmd packet
   if CHOOSE_CMD == 'shutdown':
       cmd += b'\x0b\xfdI\xec' # shutdown confirmation code
   elif CHOOSE_CMD == 'query':
       cmd += b'cubesat.c_boot' # our query argument. try your own!
   elif CHOOSE_CMD == 'exec_cmd':
       cmd += b'a=1\nprint(a)'


   # comment out if not demoing multi msg
   response=rfm9x.receive(timeout=1000,with_header=True)
   if response is not None:
       print('Beacon Packet:',response)
       rfm9x.flags=8
       rfm9x.send_with_ack(b'p\xba\xb8C'+b'8\x93'+b'cubesat.c_gs_resp')
       response=rfm9x.receive(timeout=10)
       print(response)
       time.sleep(1)
       rfm9x.flags=8
       rfm9x.send_with_ack(b'p\xba\xb8C'+b'8\x93'+b'cubesat.c_gs_resp')
       response=rfm9x.receive(timeout=10)
       print(response)
       rfm9x.flags=0
       time.sleep(1)
       rfm9x.send_with_ack(b'p\xba\xb8C'+b'8\x93'+b'cubesat.c_gs_resp')
       response=rfm9x.receive(timeout=10)
       print(response)
   print('done')

   # regular operation
   while True:
       response=rfm9x.receive(timeout=10,with_header=True)
       if response is not None:
           print('Beacon Packet:',response)
           ack = rfm9x.send_with_ack(cmd)
           if ack is not None:
               if ack: print('ACK RSSI:',rfm9x.last_rssi-137)
           # only listen for a response if we're expecting one
           if CHOOSE_CMD in ('shutdown','query','exec_cmd'):
               response=rfm9x.receive(timeout=10)
               if response is not None:
                   print('Response:',response)

   ```

   </p>
   </details>

## Changelog
