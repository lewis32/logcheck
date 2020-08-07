import os


def main():
    str_ = "kEsYMR%2Bb1jpcm8SqRwGOqXXGmfB0H%2FsRh0zRxOO4%2Fx6zfzNSXg9WCH2TRSn7jEcAj55gEATNGLuHKhH1FOQ4sUAva7dHZ6BqvpB281tDHhJPN0VK8kbZlBf3%2FXPxdByf6uooiRs4R6J33j%2F98Z%2F%2BUsbyX7jCH%2BAdpWa5WksIea8BDiuRApS8JXz3DkHMeCkQOOaW6Ek2roCTEvEkWykrgto19EOfx5BV1TypbrcVQoMKRkPTx1iluDb%2Fa6WrbSTzfYV6oVM8O9JGU4kQURtcf%2B2wOmm6dyO8l8Hm%2FYmH7j3FRu5jsMTMCY3pnlshYlo7pQtVVtc7lMn5FQEAgXMUdxHAXxvt0DtpqLXh1EZWcWgl7V1XO4ewKgqo3sfqZ6Ex2oOrQ%2FGHlox6VajdshVunvVfOatzEfjE2ayhui374Z71G5r8ATrsWHZN7bo1%2ByBW%2FkDw%2BP81q69Iqc%2B%2Bvyg%2BqMAX1ChntltMsRmIU7wzWHLTpa2JLC1yol9jTexoU%2BmD"
    ret = os.system("java -jar ..\\lib\\logdec-cmd-for-json.jar %s" % str_)
    print(ret)


if __name__ == '__main__':
    main()
