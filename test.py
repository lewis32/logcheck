from core.log_check import LogCheck
import json


def main():
    lc = LogCheck()
    data = lc.load_log()
    print(data)
    res = lc.check_log(data)
    print(res)

if __name__ == '__main__':
    main()
