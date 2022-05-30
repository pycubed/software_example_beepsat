rm -rf build
cp -r $1 build
cp frame/main.py build/
cp frame/state_machine.py build/
cp -r frame/lib build/
cp -r frame/tasko build/