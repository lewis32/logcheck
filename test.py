import os, sys
 
print('__file__:', __file__)
print('realpath of __file__:', os.path.realpath(__file__))
print('sys.executable:', sys.executable)
print('realpath of sys.executable:', os.path.realpath(sys.executable))
print('sys.argv[0]:', sys.argv[0])
print('realpath of sys.argv[0]:', os.path.realpath(sys.argv[0]))
print('sys.path[0]:', sys.path[0])
print('realpath of sys.path[0]:', os.path.realpath(sys.path[0]))