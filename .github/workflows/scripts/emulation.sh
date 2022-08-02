#!/bin/bash
cd state_machine
timeout 5s sh run.sh
if [ $? == "124" ]; then
    echo "Emulated flight software did not crash"
    exit 0
fi
echo "Emulated flight software crashed"
exit 1
