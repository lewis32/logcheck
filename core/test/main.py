import os
import sys
import time
sys.path.append(os.path.abspath(os.path.dirname(os.getcwd())))
sys.path.append(os.path.abspath(os.path.dirname(os.getcwd()))+'\\package')
from log_check import LogCheck

lc = LogCheck()
lc.checkLog()
