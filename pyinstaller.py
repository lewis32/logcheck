from PyInstaller.__main__ import run

# opts = ['setup.py', '-F', '-w', '--icon=favicon.ico']
# opts = ['start.py', '-D', '-c', '-y']
opts = ['start.py', '-D', '-c', '-y', '--icon=./conf/icon.ico']
run(opts)
