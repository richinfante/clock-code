# clock-code

Work-in-progress CircuitPython code for my 7-Segment alarm clock project.

The components that're currently in use in my prototypes, although they can be swapped for all sorts of equivalent parts:
- Raspberry Pi Pico
- Adafruit DS3231 I2C breakout
- 74HC595 8-bit shift register - 6x
- 7 Segment Displays (common cathode, with dot.)
- 470 Ohm resistors (about 60 of them)

I'm intentionally not using an LED driver IC for this project - I'm well aware of parts like the MAX7219CNG which'll do a lot of the heavy lifting for me, but part of the fun of this project is the challenge in using more simple logic components. Also, the PCBs I'm working on designing look _much_ cooler when there's arrays of resistors and shift registers all over them.
 
Overall Goals:
- modular components (use all IC sockets/header sockets for parts for easy replace-ability)
- per-led addressability for custom applications / display (this rules out using 74HC47 ICs for converting BCD->7 Segment)
- adjustable brightness - we'll be PWM-ing the output-enable pin on the 74HC595's to accomplish this
- To keep things simple and not needing high-wattage resistors when everything's at full brightness, each LED will have an individual address line and resistor.
- buzzer IC for wake up alarm-ing
- ability to swap the Pico / DS3232 for other parts by exposing the main clock as a set of pin headers for serial I/O and button / buzzer outputs.
- ability to add modules via i2c - for example, a LoRa radio, wifi adapter, or temperature sensors.
- Time format HHMMSS, flipping every other one to allow for clock separators
- Date format MON DD, using approximations of letters in 7-segment.
- Year format YYYY
- rgb led for indicator / alerts on front panel. Potentially PWM each of the colors as well.
- snooze, dst switch, dial for time / settings.
- custom PCBS so I don't need to individually wire each of the LEDs
- 5V power via DC barrel jack, code customization / power over Micro-USB.
