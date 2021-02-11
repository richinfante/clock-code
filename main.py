import board
import busio
import time
import adafruit_ds3231
import digitalio
import pwmio

# LED I/O Pins
led_dat = digitalio.DigitalInOut(board.GP2)
led_clk = digitalio.DigitalInOut(board.GP3)
led_disp = digitalio.DigitalInOut(board.GP4)
led_dat.direction = digitalio.Direction.OUTPUT
led_clk.direction = digitalio.Direction.OUTPUT
led_disp.direction = digitalio.Direction.OUTPUT

# display brightness
# 0xFFFF is off, 0x0 is full brightness.
disp_pwm = pwmio.PWMOut(board.GP16, frequency=5000, duty_cycle=0xcfff)

# Board LED - turn on
led = digitalio.DigitalInOut(board.GP25)
led.direction = digitalio.Direction.OUTPUT
led.value = True

# RTC I/O
i2c = busio.I2C(board.GP1, board.GP0)
rtc = adafruit_ds3231.DS3231(i2c)

# Clock Signal
LED_CS_EPOCH = 0.0005

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
  'K': 'H',
  'L': [0,0,0,1,1,1,0,0],
  'M': 'N',
  'N': [0,0,1,0,1,0,1,0],
  'O': [1,1,1,1,1,1,0,0],
  'P': [1,1,0,0,1,1,1,0],
  'Q': [1,1,1,1,1,1,0,1],
  'R': [0,0,0,0,1,0,1,0],
  'S': [1.0,1,1,0,1,1,0],
  'T': [0,0,0,1,1,1,1,0],
  'U': [0,0,1,1,1,0,0,0],
  'V': [0,1,1,1,1,1,0,0],
  'W': 'U',
  'X': 'H',
  'Y': [0,1,1,1,0,1,1,0],
  'Z': [1,1,0,1,1,0,1,0],
  '-': [0,0,0,0,0,0,1,0],
  '_': [0,0,0,1,0,0,0,0],
  '=': [0,0,0,1,0,0,1,0]
}

def bitbang_sequence(letter):
  if isinstance(mapping[letter], str):
    dat = mapping[mapping[letter]]
  else:
    dat = mapping[letter]

  for signal in reversed(dat):
    # print(signal)
    led_dat.value = signal == 1
    led_clk.value = True

    # reset for next clock
    time.sleep(LED_CS_EPOCH)
    led_clk.value = False
    time.sleep(LED_CS_EPOCH)

  time.sleep(LED_CS_EPOCH)
  led_disp.value = True
  time.sleep(LED_CS_EPOCH)
  led_disp.value = False

# iterate over all chars for testing
for char in sorted(mapping.keys()):
  print(char)
  bitbang_sequence(char)
  time.sleep(0.1)

while True:
  # write last digit of seconds to display
  now = rtc.datetime
  bitbang_sequence(str(now.tm_sec % 10))
