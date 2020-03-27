from PyInstaller.__main__ import run

# opts = ['setup.py', '-F', '-w', '--icon=favicon.ico']
opts = ['start.py', '-D', '-c', '-y']
run(opts)
