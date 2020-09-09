from flask import Flask
from flask import request, Response, jsonify
from flask_login import LoginManager
import secrets
import datetime
app = Flask(__name__)

login_manager = LoginManager()

Logged_in = False

USERS = {'surya':'SimplePassword'}
ACCESS_KEY = 'QWERTYUIOP'


SESSION_KEY = {}


@app.route('/',methods = ['GET','POST','PUT','DELETE'])
def hello_world():
    print('method',request.method)
    print('headers',request.headers)
    print('args',request.args)
    response = do_action(request.method,{'id':request.args.get('id','1'),
                                         'name':request.args.get('name')})
    if isinstance(response, dict):
        return jsonify(response)
    else:
        return response

@app.errorhandler(401)
@app.route('/access/userpass',methods = ['GET','POST','PUT','DELETE'])
def userpass():
    global Logged_in
    username = password = None
    for k,v in request.args.items():
        if k == 'username':
            username = v
        elif k == 'password':
            password = v

    if not Logged_in:
        if not username or not password:
            return 'Username and/or Password is missing', 401 # missing arguments
        if USERS.get(username) != password:
            return 'Username and/or Password is wrong', 401
        Logged_in = True

    if Logged_in:
        response = do_action(request.method,{'id':request.args.get('id','1'),
                                             'name':request.args.get('name')})
        return jsonify(response)


@app.errorhandler(401)
@app.route('/access/key',methods = ['GET','POST','PUT','DELETE'])
def access_with_key():
    global Logged_in
    username = password = None
    access_key = ''
    for k,v in request.args.items():
        if k == 'access_key':
            access_key = v
    if not access_key or access_key != ACCESS_KEY:
        return 'you are not authorised to perform this action', 401 # missing arguments
    response = do_action(request.method,{'id':request.args.get('id','1'),
                                         'name':request.args.get('name')})
    return jsonify(response)



@app.errorhandler(401)
@app.route('/generate/session',methods = ['GET'])
def generate_session_key():
    for k,v in request.args.items():
        if k == 'username':
            username = v
        elif k == 'password':
            password = v

    if not username or not password:
        return 'Username and/or Password is missing', 401 # missing arguments
    if USERS.get(username) != password:
        return 'Username and/or Password is wrong', 401

    session_key = secrets.token_urlsafe(16)
    end_time = datetime.datetime.now() + datetime.timedelta(minutes=1)
    SESSION_KEY[session_key] = end_time
    return jsonify({'session_key':session_key})


@app.errorhandler(401)
@app.route('/access/session',methods = ['GET','POST','PUT','DELETE'])
def access_with_session_key():
    session_key = ''
    for k,v in request.args.items():
        if k == 'session_key':
            session_key = v
    time = SESSION_KEY.get(session_key)
    if not session_key or (time and time < datetime.datetime.now()):
        return 'Invalid or expired session key', 401

    response = do_action(request.method,{'id':request.args.get('id','1'),
                                         'name':request.args.get('name')})
    return jsonify(response)


@app.route('/headers',methods = ['GET','POST','PUT','DELETE'])
def headers():
    response = request.headers
    print(response)
    print(dir(response))
    return jsonify(list(response.items()))

API_DATA = {'1':{'id':1,'name':'surya'},
            '2':{'id':2,'name':'juhi'},
}

def do_action(method,data):
    id = data.get('id')
    print(method)
    name = None
    for k,v in request.args.items():
        if k == 'name':
            name = v

    if not id:
        return 'invalid id', 401

    if method == 'GET':
        response = API_DATA.get(id)
        if response:
            return response
        else:
            return 'no data', 206
    elif method == 'POST':
        if name:
            API_DATA[id] = {'id':id,'name':name}
        else:
            return 'invalid name for id', 401
        return API_DATA[id]
    elif method == 'PUT':
        name =  data.get('name')
        if name:
            API_DATA[id] = {'id':id,'name':name}
        else:
            return 'invalid name for id', 401
        return API_DATA(id)
    elif method == 'DELETE':
        if API_DATA.get(id):
            response = API_DATA.pop(id)
            return response
        else:
            return 'invalid id', 401
    else:

        return method+'invalid method', 400



login_manager.init_app(app)


app.run(host='127.0.0.1',port=5002)
