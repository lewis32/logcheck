from log_check import LogCheck


def main():
    lc = LogCheck()
    try:
        log = lc.load_log()
        conf = lc.load_policy()
    except Exception as e:
        print("Failed to load log or policy: ", e)
    else:
        result = lc.check_log(log,conf)
        for i in range(len(result)):
            print(i,result[i])

if __name__ == '__main__':
    main()
