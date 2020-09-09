from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/')
def hello_world():
    print(request.method)
    return 'Hello, Happy!'


app.run()
