
from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import threading


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

try:
    # Replace these values with your actual MySQL connection details
    host = 'localhost'
    user = 'root'
    password = 'Ankit@2003'
    database = 'Ludo'

    @app.route('/generate_otp', methods=['POST'])
    def generate_otp():
        # Receive mobile_number from the request
        mobile_number = request.json.get('mobile_number')
        # List to store fetched data
        fetched_data = []

        try:
            # Establish a connection
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )

            if connection.is_connected():
                print(f"Connected to MySQL server")
                cursor = connection.cursor()

                # Execute a SELECT query with a WHERE clause to filter by mobile_number
                query = f"SELECT * FROM user WHERE mobile_number = '{mobile_number}'"
                cursor.execute(query)

                # Fetch all the rows
                rows = cursor.fetchall()

                # Display the fetched data
                for row in rows:
                    fetched_data.append(row)

        except mysql.connector.Error as e:
            print(f"Error: {e}")

        finally:
            # Close the connection when done
            if 'connection' in locals() and connection.is_connected():
                connection.close()
                print("Connection closed")
                
        print(fetched_data)

        return jsonify({'message': 'Data fetched successfully','Data' : fetched_data}), 200


    lock = threading.Lock()
    @app.route('/register', methods=['POST'])

    def register_user():
        with lock:
            data = request.json
            name = data.get('name')
            mobile_number = data.get('mobile_number')
            email = data.get('email')
            print(name,mobile_number, email)

            # Establish a connection
            connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if connection.is_connected():
                print(f"Connected to MySQL server")
                cursor = connection.cursor()

                # Insert user data into the 'user' table
                print("name ", name, "email ", "mobile ", mobile_number)
                query = "INSERT INTO user (name, mobile_number, email) VALUES (%s, %s, %s)"
                values = (name, mobile_number, email)
                cursor.execute(query, values)
                
                query = f"SELECT * FROM user WHERE mobile_number = '{mobile_number}'"
                cursor.execute(query)
                
                # List to store fetched data
                fetched_data = []
                
                # Fetch all the rows
                rows = cursor.fetchall()

                # Display the fetched data
                for row in rows:
                    fetched_data.append(row)

                # Commit the transaction
                connection.commit()

                print("User registered successfully")

            if not mobile_number or not name or not email:
                return jsonify({'error': 'Mobile number, name, and email are required'}), 400

            return jsonify({'message': 'Data fetched successfully','Data' : fetched_data}), 201
except Exception as e:
    print(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)