import board
import busio
import time
import adafruit_ds3231
import digitalio
import pwmio

# Constants
LED_SERIAL_PULSE_TIME = 0.0005
LED_BRIGHTNESS = 0.4
LED_DUTY_CYCLE = int(0xffff * (1 - LED_BRIGHTNESS))

# LED I/O Pins (for inputs to 74HC595)
led_dat = digitalio.DigitalInOut(board.GP2)
led_clk = digitalio.DigitalInOut(board.GP3)
led_disp = digitalio.DigitalInOut(board.GP4)
led_dat.direction = digitalio.Direction.OUTPUT
led_clk.direction = digitalio.Direction.OUTPUT
led_disp.direction = digitalio.Direction.OUTPUT

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
  '0': [1,1,1,1,1,1,0,0],
  '1': [0,1,1,0,0,0,0,0],
  '2': [1,1,0,1,1,0,1,0],
  '3': [1,1,1,1,0,0,1,0],
  '4': [0,1,1,0,0,1,1,0],
  '5': [1,0,1,1,0,1,1,0],
  '6': [1,0,1,1,1,1,1,0],
  '7': [1,1,1,0,0,0,0,0],
  '8': [1,1,1,1,1,1,1,0],
  '9': [1,1,1,0,0,1,1,0],
  'A': [1,1,1,0,1,1,1,0],
  'B': [0,0,1,1,1,1,1,0],
  'C': [1,0,0,1,1,1,0,0],
  'D': [0,1,1,1,1,0,1,0],
  'E': [1,0,0,1,1,1,1,0],
  'F': [1,0,0,0,1,1,1,0],
  'G': [1,1,1,1,0,1,1,0],
  'H': [0,1,1,0,1,1,1,0],
  'I': [0,0,0,0,1,1,0,0],
  'J': [0,1,1,1,0,0,0,0],
  'K': 'H', # alias of "K"
  'L': [0,0,0,1,1,1,0,0],
  'M': 'N', # alias of "N" for now (until we figure out multi-char letters)
  'N': [0,0,1,0,1,0,1,0],
  'O': [1,1,1,1,1,1,0,0],
  'P': [1,1,0,0,1,1,1,0],
  'Q': [1,1,1,1,1,1,0,1],
  'R': [0,0,0,0,1,0,1,0],
  'S': [1.0,1,1,0,1,1,0],
  'T': [0,0,0,1,1,1,1,0],
  'U': [0,0,1,1,1,0,0,0],
  'V': [0,1,1,1,1,1,0,0],
  'W': 'U', # alias of "U" for now (until we figure out multi-char letters)
  'X': 'H', # alias of "H"
  'Y': [0,1,1,1,0,1,1,0],
  'Z': [1,1,0,1,1,0,1,0],
  '-': [0,0,0,0,0,0,1,0],
  '_': [0,0,0,1,0,0,0,0],
  '=': [0,0,0,1,0,0,1,0]
}


# Render a char / 7 segment bitmap
# This assumes that we're only using one 74HC595 IC / a single digit.
# To account for multiple, we'd need to pulse led_disp after a sequence of chars is written.
def serial_output_char(letter):
  # allow using precalculated sequence
  if isinstance(letter, list):
    dat = letter

  # lookup in font table
  elif isinstance(mapping[letter], str):
    dat = mapping[mapping[letter]]
  else:
    dat = mapping[letter]

  # Reverse the order since the first LED is the furthest one (the dot)
  for signal in reversed(dat):
    led_dat.value = signal == 1
    led_clk.value = True

    # reset for next clock
    time.sleep(LED_SERIAL_PULSE_TIME)
    led_clk.value = False
    time.sleep(LED_SERIAL_PULSE_TIME)

  # Pulse the shift register latch to transfer data
  # into the display registers
  time.sleep(LED_SERIAL_PULSE_TIME)
  led_disp.value = True
  time.sleep(LED_SERIAL_PULSE_TIME)
  led_disp.value = False

# Spin loader animation
def show_loader(load_ct=10):
  for i in range(0, load_ct):
    for x in range(0, 6):
      # empty display
      seq = [0,0,0,0,0,0,0,0]
      # toggle the x'th bit (from 0-6, which is the outer ring of the 7 segment)
      seq[x] = 1
      serial_output_char(seq)
      time.sleep(0.05)

# render a loading bar for testing
show_loader()

# iterate over all chars for testing
for char in sorted(mapping.keys()):
  serial_output_char(char)
  time.sleep(0.05)

while True:
  # write last digit of seconds to display
  now = rtc.datetime
  serial_output_char(str(now.tm_sec % 10))
