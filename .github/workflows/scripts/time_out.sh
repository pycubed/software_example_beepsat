#!/bin/bash

# Script that runs an already compiled instance of the flight software, 
# and then returns exit code 0, or 1 depending on if the flight software
# ran successfully for 5 seconds.

cd state_machine
timeout 5s sh run.sh
if [ $? == "124" ]; then
    echo "$1 did not crash"
    exit 0
fi
echo "$1 crashed"
exit 1
