from core.log_check import LogCheck


def main():
    lc = LogCheck()
    data = lc.load_log()
    res = lc.check_log(data)
    print(res)


if __name__ == '__main__':
    main()
