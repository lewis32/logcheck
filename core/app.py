from bottle import run, route, template, Bottle
from log_check import LogCheck

app = Bottle()

@route('/',method='GET')
def index():
    return template('main')

@route('result',method='Post')
def result():
    lc = LogCheck()


if __name__ == '__main__':
    run(debug=True, reloader=True)
