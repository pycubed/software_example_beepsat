# Beep-Sat Demo

This is an educational "flight software" example for a simple beeping-satellite mission.

There are countless ways to implement a mission's software stack. This particular example demonstrates the usage of a lightweight async library performing routine satellite functions utilizing PyCubed hardware capabilities.

complexity: `basic`

features:

- discovers and initializes onboard hardware
- operates a simple asynchronous state machine that performs routine spacecraft tasks until receiving an over-the-air shutdown command
- prints descriptive messages during operation to the USB serial terminal
- default tasks:
  1. blink an LED twice per second
  2. monitor state-of-health info such as battery voltage
     - enter low power mode if necessary
  3. cache on-board IMU data once per second
  4. transmit a beacon packet (LoRa modulated) once per 60 seconds
     - listen for a response for 10 seconds after each beacon
- each task definition is contained within a single `.py` file inside the [/mainboard/beepsat_tasks/](/mainboard/beepsat_tasks/) directory
  - allowing you to easily add, remove, or share of tasks
- each task inside `beepsat_tasks` is automatically loaded and scheduled/performed according to their respective `frequency`, and `priority` attributes

# Usage

Copy the contents of [mainboard](/mainboard/) to your `PYCUBED` drive and observe the output in a serial terminal.
