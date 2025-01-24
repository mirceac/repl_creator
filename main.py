from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World'

from datetime import datetime

@app.route('/time')
def get_time():
    return {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Not found'}, 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
