# State Machine

For the state_machine version of the software there are two independent parts: the "frame" where the state_machine implementation resides along with a few other helpful utilities,
and the "plugins" where the actual specific hardware and task dependent parts of the flight software are.

To build the flight software you run `sh build.sh {driver} {application}`.
The {driver} is the part of the software that interfaces with the hardware (or emulates it).
The {application} is what the software actually does (by utilizing the driver to communicate with the hardware).
This allows us to easily test and develop flight software localy by emulating the hardware.

# Simple Example

Build & Run: ``sh build.sh drivers/example applications/example && sh run.sh`. 
This example emulates the pycubed library, so that it can be run locally on your computer. 

For a simple example see [the example](./example.md)

## Dependencies
The build script automatically generates a graph of the state machine. 
This requires that you install the `graphviz` tool.

## Locally running the emulation version of the software
To build the files run `sh build.sh drivers/emulation/ applications/flight/` and to run it run `sh run.sh`. 

## Building the actual flight software
build: `sh build.sh drivers/pycubedmini/ applications/flight/`
run: copy over files to the CIRCUITPY drive (don't automate with rm -rf *, as this has led to corrupting the file system in the past)

## Software Architecture Overview

The folder `frame/` contains the barebones sattelite state machine code, and the `main.py`. 
This code remains unchanged independent of whether you are using pycubedmini, pycubed, or emulating hardware.

The `drivers` folder contains libaries allowing one to interface with some particular hardware.
We currently have the example, pycubedmini and pycubedmini emulation. 
We plan to support pycubed in the future.

The `applications` folder contains the programs that utilize drivers. 
For example: the actual flight software and the example software.