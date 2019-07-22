if __name__ == "__main__":
    from PyInstaller.__main__ import run
    # opts=['setup.py','-F','-w','--icon=favicon.ico']
    # opts=['setup.py','-F','-w']
    # opts=['setup.py','-D','-w']
    opts=['setup.py','-D']
    run(opts)