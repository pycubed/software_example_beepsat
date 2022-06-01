# State Machine

For the state_machine version of the software there are two independent parts: the "frame" where the state_machine implementation resides along with a few other helpful utilities,
and the "plugins" where the actual specific hardware and task dependent parts of the flight software are.

To build the flight software you run `sh build.sh {plugin}` where `{plugin}` is the path to the plugin code (depends on hardware/purpose).

## Dependencies
The build script automatically generates a graph of the state machine. 
This requires that you install the `graphviz` tool.

## Locally running the test version of the software
To build the files run `sh build.sh plugs/advanced` and to run it run `sh run.sh`. 

## Building the actual flight software
build: `sh build.sh frame plugs/test`
run: copy over files to the CIRCUITPY drive (don't automate with rm -rf *, as this has led to corrupting the file system in the past)

## Software Architecture Overview

The folder `frame/` contains the barebones sattelite state machine code, and the `main.py`. 
This code remains unchanged independent of whether you are using pycubedmini, pycubed, or running your own test script.

We also have the folders `plugs/{name}` where each `name` represents a certain "plugin" that you attach to the frame using the build script.
Each `{name}` represents an entirely different set of flight software, be it flight software targetting pycubedmini, pycubed or an emulator.
The state machine structure, tasks, and libraries are all defined in the individual `plugs/{name}` directories.

See [the plugins README](plugs/README.md) for a brief description of each plugin.

In order to see a basic example run `sh build.sh plugs/example` and to run it run `sh run.sh`. 
This example emulates the pycubed library, so that it can be run locally on your computer. 
