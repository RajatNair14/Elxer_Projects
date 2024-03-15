from flask import Flask, render_template
from flask_socketio import SocketIO, send, join_room, leave_room,emit
import random
import threading
import mysql.connector
import asyncio
import websockets


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")


ROOMS = set()
database = mysql.connector.connect(
  host="localhost",
  user="root",
  password="12345"
)


database_cursor = database.cursor()
database_cursor.execute("create database if not exists Ludo")
database_cursor.execute("use Ludo")
database_cursor.execute("CREATE TABLE IF NOT EXISTS game_data(port int ,player1 varchar(40),player2 varchar(40),player3 varchar(40),player4 varchar(40))")


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    send('Hello from the server on connection!', broadcast=True)
    

import random
def generate_port():
    port = random.randint(1024, 5000)
    print(port,"****port")
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
            que="select player1 from game_data where port=%s"
            while True:
                port_number = generate_port()
                database_cursor.execute(que,[port_number])
                res=database_cursor.fetchone()
                if res is None:
                    join_room(port_number)
                    USER_ID.append(port_number)
                    break  

            port_number=USER_ID[0]
            USER_ID.append(user_id)
            print(USER_ID, "user id")
            print("port number ** first if", len(USER_ID), " ", port_number)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  #     chat_server_thread = threading.Thread(target=port_number)
 
        else:
            
            port_number = USER_ID[0]
            USER_ID.append(user_id)
            join_room(port_number)
            if len(USER_ID)==3:
                print(USER_ID)
                
                print("broadcast")
                print(USER_ID)
                user_id1=USER_ID[1:]
                for id in user_id1:
                    message = {
                    'msg': "Hello to all players in this room! Let's play Ludo!",
                    'user_info_list': id,
                    'room': port_number,
                    'status': True
                    }
                    
                players_dict = {f"player{i+1}": str(user_id) for i, user_id in enumerate(user_id1)}
                data = {**{"port": port_number, "status": True}, **players_dict}
                print(data)
                socketio.emit('message',data,room=port_number, broadcast=True)
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
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)