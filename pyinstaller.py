from PyInstaller.__main__ import run

# opts = ['setup.py', '-F', '-w', '--icon=./assets/icon.ico']
# opts = ['start.py', '-D', '-c', '-y']
opts = ['start.py', '-D', '-c', '-y', '--icon=./assets/icon.ico']
run(opts)
