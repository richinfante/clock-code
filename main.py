import board
import busio
import time
import adafruit_ds3231
import digitalio
import pwmio

# Constants
LED_SERIAL_PULSE_TIME = 0.0005
LED_BRIGHTNESS = 0.2
LED_DUTY_CYCLE = int(0xffff * (1 - LED_BRIGHTNESS))

# LED I/O Pins (for inputs to 74HC595)
led_dat = digitalio.DigitalInOut(board.GP2)
led_clk = digitalio.DigitalInOut(board.GP3)
led_disp = digitalio.DigitalInOut(board.GP4)
led_dat.direction = digitalio.Direction.OUTPUT
led_clk.direction = digitalio.Direction.OUTPUT
led_disp.direction = digitalio.Direction.OUTPUT

# led_on = digitalio.DigitalInOut(board.GP16)
# led_on = digitalio.Direction.OUTPUT
# led_on.value = False
twelve_hr = True

# rotary switch (not yet supported on picos)
# import rotaryio
# encoder = rotaryio.IncrementalEncoder(board.GP18, board.GP19)

# Display brightness
# 0xFFFF is off, 0x0000 is full brightness, this's wired to the 74HC595's Output-Enable pin,
# which is active low. The high end of the PWM pulses actually *disable* the display
disp_pwm = pwmio.PWMOut(board.GP16, frequency=5000, duty_cycle=LED_DUTY_CYCLE)

# Board LED - turn on
led = digitalio.DigitalInOut(board.GP25)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# RTC I/O
i2c = busio.I2C(board.GP1, board.GP0)
rtc = adafruit_ds3231.DS3231(i2c)

# FONT
mapping = {
       #A,B,C,D,E,F,G#
  ' ': [0,0,0,0,0,0,0],
  '0': [1,1,1,1,1,1,0],
  '1': [0,1,1,0,0,0,0],
  '2': [1,1,0,1,1,0,1],
  '3': [1,1,1,1,0,0,1],
  '4': [0,1,1,0,0,1,1],
  '5': [1,0,1,1,0,1,1],
  '6': [1,0,1,1,1,1,1],
  '7': [1,1,1,0,0,0,0],
  '8': [1,1,1,1,1,1,1],
  '9': [1,1,1,0,0,1,1],
  'A': [1,1,1,0,1,1,1],
  'B': [0,0,1,1,1,1,1],
  'C': [1,0,0,1,1,1,0],
  'D': [0,1,1,1,1,0,1],
  'E': [1,0,0,1,1,1,1],
  'F': [1,0,0,0,1,1,1],
  'G': [1,1,1,1,0,1,1],
  'H': [0,1,1,0,1,1,1],
  'I': [0,0,0,0,1,1,0],
  'J': [0,1,1,1,0,0,0],
  'K': 'H', # alias of "K"
  'L': [0,0,0,1,1,1,0],
  'M': 'N', # alias of "N" for now (until we figure out multi-char letters)
  'N': [0,0,1,0,1,0,1],
  'O': [1,1,1,1,1,1,0],
  'P': [1,1,0,0,1,1,1],
  'Q': [1,1,1,1,1,1,0],
  'R': [0,0,0,0,1,0,1],
  'S': [1.0,1,1,0,1,1],
  'T': [0,0,0,1,1,1,1],
  'U': [0,0,1,1,1,0,0],
  'V': [0,1,1,1,1,1,0],
  'W': 'U', # alias of "U" for now (until we figure out multi-char letters)
  'X': 'H', # alias of "H"
  'Y': [0,1,1,1,0,1,1],
  'Z': [1,1,0,1,1,0,1],
  '-': [0,0,0,0,0,0,1],
  '_': [0,0,0,1,0,0,0],
  '=': [0,0,0,1,0,0,1]
}

# Render a char / 7 segment bitmap
# This assumes that we're only using one 74HC595 IC / a single digit.
# To account for multiple, we'd need to pulse led_disp after a sequence of chars is written.
def serial_output_char(letter, dot=False):
  # allow using precalculated sequence
  if isinstance(letter, list):
    dat = letter

  # lookup in font table
  elif isinstance(mapping[letter], str):
    dat = mapping[mapping[letter]]
  else:
    dat = mapping[letter]

  dat = list(dat)
  if dot:
    dat.append(1)
  else:
    dat.append(0)

  # Reverse the order since the first LED is the furthest one (the dot)
  for signal in reversed(dat):
    led_dat.value = signal == 1
    led_clk.value = True

    # reset for next clock
    time.sleep(LED_SERIAL_PULSE_TIME)
    led_clk.value = False
    time.sleep(LED_SERIAL_PULSE_TIME)

def serial_output_str(string, dotmap=None):
  if isinstance(string, str):
    for (i, char) in enumerate(string):
      if dotmap and len(dotmap) > i:
        serial_output_char(char, dot=dotmap[i])
      else:
        serial_output_char(char)
  else:
    serial_output_char(string)

  # Pulse the shift register latch to transfer data
  # into the display registers
  time.sleep(LED_SERIAL_PULSE_TIME)
  led_disp.value = True
  time.sleep(LED_SERIAL_PULSE_TIME)
  led_disp.value = False

# # # Spin loader animation
# def show_loader(load_ct=4):
#   for i in range(0, load_ct):
#     for x in range(0, 6):
#       # empty display
#       seq = [0,0,0,0,0,0,0,0]
#       # toggle the x'th bit (from 0-6, which is the outer ring of the 7 segment)
#       seq[x] = 1
#       serial_output_str([
#         seq,
#         seq,
#         seq,
#         seq,
#         seq,
#         seq
#       ])
#       time.sleep(0.05)

# # render a loading bar for testing
# show_loader()

# # iterate over all chars for testing
# for char in sorted(mapping.keys()):
#   serial_output_char(char)
#   time.sleep(0.05)

months = [
  'JAN ',
  'FEB ',
  'MAR ',
  'APR ',
  'MAY ',
  'JUN ',
  'JUL ',
  'AUG ',
  'SEP ',
  'OCT ',
  'NOV ',
  'DEC '
]

while True:
  # write last digit of seconds to display
  now = rtc.datetime
  hrs = now.tm_hour
  min = now.tm_min
  sec = now.tm_sec

  if twelve_hr:
    hrs = hrs % 12

  if hrs < 10:
    hrs = ' %s' % hrs
  
  if min < 10:
    min = '0%s' % min
    
  if isinstance(sec, int) and sec < 10:
    sec = '0%s' % sec
    
  output = "%s%s%s" % (hrs, min, sec)
  serial_output_str(output, [0,1,1,1,1,0])

  time.sleep(2)
  serial_output_str("%s%s" % (months[now.tm_mon-1], now.tm_mday))

  time.sleep(2)
  serial_output_str("  %s" % (now.tm_year))
  time.sleep(2)
