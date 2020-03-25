from core.log_check import LogCheck


def main():
    lc = LogCheck()
    # lc.load_policy()
    data = """{
                "appname": "vidaa-free", "launchsource": "1", "appid": "184",
                 "eventcode": "211010", "version": "3.0", "starttime": "1584944040",
                 "endtime": "0", "appversion": "", "apppackage": "vidaa-free",
                 "deviceid": "861003009000004000000730458b8c7f0935ab94f026120720b3c354",
                 "os": "Linux", "chipplatform": "MTK9602", "zone": "-10",
                 "countrycode": "USA", "capabilitycode": "2019101201",
                 "tvversion": "V0000.01.00S.K0321", "brand": "his",
                 "devicemsg": "HU50A6109FUWV591", "tvmode": "2", "time": "1584944058",
                 "extra": "{\\"a\\":1, \\"b\\":2}"
            },{
                "appname": "vidaa-free", "launchsource": "1", "appid": "184",
                 "eventcode": "200120", "version": "3.0", "starttime": "1584944040",
                 "endtime": "0", "appversion": "", "apppackage": "vidaa-free",
                 "deviceid": "861003009000004000000730458b8c7f0935ab94f026120720b3c354",
                 "os": "Linux", "chipplatform": "MTK9602", "zone": "-10",
                 "countrycode": "USA", "capabilitycode": "2019101201",
                 "tvversion": "V0000.01.00S.K0321", "brand": "his",
                 "devicemsg": "HU50A6109FUWV591", "tvmode": "2", "time": "1584944058"
            }"""
    lc.check_log(data=data)

if __name__ == '__main__':
    main()
