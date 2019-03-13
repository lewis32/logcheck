from log_check import LogCheck

def test():
    lc = LogCheck()
    log = lc.loadLog()

    print(log[0])
    print(log[1])
    # policy = lc.loadPolicy()
    # lc.checkLog(log,policy)

if __name__ == '__main__':
    test()