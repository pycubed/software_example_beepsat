# State Machine

## Software Architecture Overview

The folder `frame/` contains the `main.py` (entry point for our software) and a custom state machine implementation.
This code is minimal enough that no changes should be required regardless of if you are targeting pycubedmini, pycubed, or emulating hardware.

The `drivers` folder contains libaries allowing one to interface with the target hardware.
We currently have the example emulator, pycubedmini driver and pycubedmini emulation. 
We plan to support pycubed in the future.

The `applications` folder contains the programs that utilize the drivers to achieve the specific mission objective. Such as detumbling, beacon transmisions, logging, power management, etc...

## Development

VSCode is strongly recomended so that the IDE properly resolves imports.

## Dependencies
In order to run emulated software `python3` is required.

The build script automatically generates a graph of the state machine. 
Becuase of this `graphviz` and `ImageMagick` are required.


## Building Flight Software

To build the flight software you run `sh build.sh {driver} {application}`.
The {driver} is the part of the software that interfaces with the hardware (or emulates it).
The {application} is what the software attempts to achieve the mission objective (by utilizing the driver to communicate with the hardware).
This allows us to easily test and develop flight software localy by emulating the hardware.

## Simple Example

Build and Run: `sh build.sh drivers/example applications/example && sh run.sh`. 

This example emulates the pycubed library, so it can be run locally on your computer (asuming python3 is installed). 

For an explanation of the example code see [this](./example.md).

## Emulating The Flight Software
Build and Run: `sh build.sh drivers/emulation/ applications/flight/ && sh run.sh` 

## Running The Flight Software
build: `sh build.sh drivers/pycubedmini/ applications/flight/`

run: copy over files to the CIRCUITPY drive (don't automate with rm -rf *, as this has led to corrupting the file system in the past)
