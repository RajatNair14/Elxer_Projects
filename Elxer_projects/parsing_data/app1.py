from flask import Flask
import subprocess
app = Flask(__name__)

@app.route('/')
def hello():
    # Run the external executable (app.exe)
    result = subprocess.run([r'E:\Elxer Projects\dist\app.exe'], stdout=subprocess.PIPE)
    return f"Hello, result from external executable: {result}"

@app.route('/process_json_file', methods=['POST'])
def process_json_file():
    
    result = subprocess.run([r'E:\Elxer Projects\dist\app.exe'], stdout=subprocess.PIPE)
    # output = result.stdout.decode('utf-8')
    return result
    

# if __name__ == '__main__':
#     app.run(debug=True)
