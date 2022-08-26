#!/bin/bash
cd state_machine
timeout 5s sh run.sh
if [ $? == "124" ]; then
    echo "$1 did not crash"
    exit 0
fi
echo "$1 crashed"
exit 1
