from log_check import LogCheck


def main():
    lc = LogCheck()
    result = lc.check_log()
    for i in result:
        print(i)

if __name__ == '__main__':
    main()
