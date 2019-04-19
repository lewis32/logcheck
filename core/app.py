from bottle import run, route,template
from log_check import LogCheck

@route('/',method='GET')
def index():
    return template('main')

if __name__ == '__main__':
    run(debug=True)

