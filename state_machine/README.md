# State Machine

## Software Architecture Overview

The folder `frame/` contains the barebones sattelite state machine code, and the `main.py`. 
This code remains independent of whether you are targeting pycubedmini, pycubed, or emulating hardware.

The `drivers` folder contains libaries allowing one to interface with the target hardware.
We currently have the example, pycubedmini and pycubedmini emulation. 
We plan to support pycubed in the future.

The `applications` folder contains the programs that utilize the drivers. 
For example: the actual flight software and the example software.

## Dependencies
The build script automatically generates a graph of the state machine. 
This requires that you install the `graphviz` tool.

## Building Flight Software

To build the flight software you run `sh build.sh {driver} {application}`.
The {driver} is the part of the software that interfaces with the hardware (or emulates it).
The {application} is what the software attempts to achieve the mission objective (by utilizing the driver to communicate with the hardware).
This allows us to easily test and develop flight software localy by emulating the hardware.

## Simple Example

Build & Run: `sh build.sh drivers/example applications/example && sh run.sh`. 
This example emulates the pycubed library, so that it can be run locally on your computer. 

For an explanation of the example code see [this](./example.md)

## Emulating the flight software
To build the files run `sh build.sh drivers/emulation/ applications/flight/` and to run it run `sh run.sh`. 

## Running the flight software
build: `sh build.sh drivers/pycubedmini/ applications/flight/`
run: copy over files to the CIRCUITPY drive (don't automate with rm -rf *, as this has led to corrupting the file system in the past)
