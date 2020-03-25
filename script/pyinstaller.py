from PyInstaller.__main__ import run

opts = ['setup.py', '-F', '-w', '--icon=..conf/icon.jpg']
opts = ['start.py', '-D', '-c', '-y']
run(opts)
