from PyInstaller.__main__ import run

opts = ['start.py',
        '-D',
        '-c',
        '-y',
        '--icon=./assets/icon.ico']
run(opts)
