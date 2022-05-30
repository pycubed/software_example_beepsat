# BeepSat (pycubedmini version)

Currently we have 3 versions of software, basic, advanced and state_machine.
Basic and advanced are drop in replacements for the upstream versions.
While state_machine restructures the advanced flight software to work with a state_machine.
For the state_machine version of the software there are two independent parts, the "frame" where the state_machine implementation resides along with a few other helpful utilities.
And the "plugins" where the actual specific hardware dependent parts of the flight software are.

To build the flight software you run `sh build.sh {plugin}` where `{plugin}` is the part of the code that depends on hardware/purpose.

## Locally running the test version of the software
To build the files run `sh build.sh frame plugs/test` and to run it run `sh run.sh`. 

## Building the actual flight software
build: `sh build.sh frame plugs/test`
run: copy over files to the CIRCUITPY drive (don't automate with rm -rf *, as this has led to corrupting the file system in the past)


# Beep-Sat Demo (Modified for PyCubed-Mini / Work In Progress)

## License (same as upstream)
<a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-sa/4.0/88x31.png" /></a><br />
- Hardware in this repository is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-sa/4.0/">Creative Commons Attribution-ShareAlike 4.0 International License</a>.
- Software/firmware in this repository is licensed under MIT unless otherwise indicated.
