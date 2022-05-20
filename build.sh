rm -rf build
cp -r $2 build
cp $1/main.py build/
cp $1/state_machine.py build/
cp -r $1/tasko build/
cp $1/statemachine.yaml build/