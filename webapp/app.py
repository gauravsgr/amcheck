from flask import Flask
from flask import Response
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/data') 
def content():
    try:
        with open("/tmp/data.txt", 'r') as f:
            return Response(f.read(), mimetype='text/plain')
    except FileNotFoundError:
        return "'Round price log' not created yet. Possibly because per round threshold isn't met with any seller to log."
            
if __name__ == '__main__':
    #app.run()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

