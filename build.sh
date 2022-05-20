echo $1
echo $2

rm -rf build
cp -r $2 build
cp $1/main.py build/
cp $1/state_machine.py build/