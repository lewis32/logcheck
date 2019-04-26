from bottle import run, route, template, request
from log_check import LogCheck

upload_path = './tmp'

@route('/index', method='GET')
def index():
    return template('main')

@route('/index', method='POST')
def upload():
    upload_file = request.files.get('logfile')
    upload_file.save(upload_path, override='True')
    # return u"上传成功,文件名为：%s，文件类型为：%s"% (upload_file.filename,upload_file.content_type)
    print('ok')
    return template('main')

@route('/result', method='GET')
def get_result():
    lc = LogCheck()
    result = lc.check_log()
    return template('result', result=result)

if __name__ == '__main__':
    run(host='0.0.0.0', port='8080', debug=True)
