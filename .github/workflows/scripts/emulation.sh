#!/bin/bash
cd state_machine
timeout 5s sh run.sh
if $? == "124":
    exit 0
echo "Emulated flight software crashed"
exit 1
