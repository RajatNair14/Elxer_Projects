from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from flask_cors import CORS
from engineio.async_drivers import gevent
import random
import threading
import mysql.connector
import broadcast_message
import asyncio
import websockets


application = Flask(__name__)

CORS(application, resources={r"/*": {"origins": "http://localhost:3000"}})
socketio = SocketIO(application, cors_allowed_origins="*",async_mode='gevent')

host = 'localhost'
user = 'root'
password = '12345'
database = mysql.connector.connect(
    host=host,
    user=user,
    password=password)
database_cursor = database.cursor()
database_cursor.execute("create database if not exists Ludo")
database_cursor.execute("use Ludo")
database_cursor.execute("CREATE TABLE IF NOT EXISTS game_data(port int ,player1 varchar(40),player2 varchar(40),player3 varchar(40),player4 varchar(40))")
database_cursor.execute("CREATE TABLE IF NOT EXISTS user(name varchar(40),mobile_number int ,email varchar(60))")
database_cursor.execute("CREATE TABLE IF NOT EXISTS data(Name varchar(40),Mobile int ,Age int,Email varchar(40))")

ROOMS = set()

@application.route('/addtodb', methods=['POST'])
def addtodb():
    
    data = request.json
    name = data.get('name')
    mobile = data.get('mobile')
    age=data.get('age')
    email = data.get('email')
    
    que="INSERT INTO data (Name,Mobile,Age,Email) VALUES (%s, %s, %s,%s)"
    values = (name, mobile,age, email)
    database_cursor.execute(que, values)
    database.commit()
    return {'Name':name,'Mobile':mobile,'Age':age,'Email':email}

@application.route('/generate_otp', methods=['POST'])
def generate_otp():
    mobile_number = request.json.get('mobile_number')
    fetched_data = []

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        if connection.is_connected():
            print(f"Connected to MySQL server")
            cursor = connection.cursor()

            query = f"SELECT * FROM user WHERE mobile_number = '{mobile_number}'"
            cursor.execute(query)

            rows = cursor.fetchall()

            for row in rows:
                fetched_data.append(row)

    except mysql.connector.Error as e:
        print(f"Error: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("Connection closed")

    print(fetched_data)
    return jsonify({'message': 'Data fetched successfully', 'Data': fetched_data}), 200

lock = threading.Lock()
@application.route('/register', methods=['POST'])
def register_user():
    with lock:
        data = request.json
        name = data.get('name')
        mobile_number = data.get('mobile_number')
        email = data.get('email')
        print(name, mobile_number, email)

        fetched_data = []

        try:
            if database.is_connected():
                print(f"Connected to MySQL server")

                print("name ", name, "email ", "mobile ", mobile_number)
                query = "INSERT INTO user (name, mobile_number, email) VALUES (%s, %s, %s)"
                values = (name, mobile_number, email)
                database_cursor.execute(query, values)

                query = f"SELECT * FROM user WHERE mobile_number = '{mobile_number}'"
                database_cursor.execute(query)

                rows = database_cursor.fetchall()

                for row in rows:
                    fetched_data.append(row)

                database.commit()

                print("User registered successfully")

        except mysql.connector.Error as e:
            print(f"Error: {e}")

        finally:
            if 'connection' in locals() and database.is_connected():
                database.close()
                print("Connection closed")

        if not mobile_number or not name or not email:
            return jsonify({'error': 'Mobile number, name, and email are required'}), 400

        return jsonify({'message': 'Data fetched successfully', 'Data': fetched_data}), 201


    
@application.route('/')
def index():
    return render_template('index.html')
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    send('Hello from the server on connection!', broadcast=True)

import random

def generate_port():
    port = random.randint(1024, 65535)
    print(port, "****port")
    return port

USER_ID = []
lock = threading.Lock()

@socketio.on('join_room')
def handle_join_room(data):
    
    global USER_ID
    user_id = int(data.get('user_id'))
    print(user_id, "** userIds hai")
    with lock:
        if len(USER_ID) == 0:
            que = "select player1 from game_data where port=%s"
            while True:
                port_number = generate_port()
                database_cursor.execute(que, [port_number])
                res = database_cursor.fetchone()
                if res is None:
                    join_room(port_number)
                    USER_ID.append(port_number)
                    break

            port_number = USER_ID[0]
            USER_ID.append(user_id)
            print(USER_ID, "user id")
            print("port number ** first if", len(USER_ID), " ", port_number)

        else:
            port_number = USER_ID[0]
            USER_ID.append(user_id)
            join_room(port_number)
            if len(USER_ID) == 3:
                print(USER_ID)
                print("broadcast")
                print(USER_ID)
                user_id1 = USER_ID[1:]
                messages = []
                for id in user_id1:
                    message = {
                        'msg': "Hello to all players in this room! Let's play Ludo!",
                        'user_info_list': id,
                        'room': port_number,
                        'status': True
                    }
                    messages.append(message)

                players_dict = {f"player{i + 1}": str(user_id) for i, user_id in enumerate(user_id1)}
                data = {**{"port": port_number, "status": True}, **players_dict}
                print(data)
                socketio.emit('message', messages, room=port_number, broadcast=True)
                USER_ID = []

@socketio.on('leave_room')
def handle_leave_room(data):
      
    user_id = data.get('user_id')
    port_game = data.get("port")

    room = f'room_{user_id}'
    leave_room(room)
    ROOMS.remove(room)
    que2 = "delete from game_data where port=%s"
    database_cursor.execute(que2, [port_game])
    print(f'Client left room: {room}')
    emit('message', f'Goodbye! You left : {room}', room=room)

@socketio.on('message')
def handle_message(data):
    print(f"Received message: {data}")

    room = data.get('room')
    generated_number = data.get("generatedNumber")

    print(f"Generated number: {generated_number}")
    print(f"Room: {room}")
    print(f'Message from client in room {room}: {data}')

    print(f"Broadcasting message to all players in room {room}")
    emit('message', data, room=room)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(application, host='0.0.0.0', port=8000, debug=True)