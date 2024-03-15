from flask import Flask, jsonify, request
from datetime import datetime
import re
import pymongo
import requests
from bson import ObjectId
import threading

app = Flask(__name__)


@app.route('/', methods=['POST'])
def hi():
    return "Hello"

@app.route('/parse_data', methods=['POST'])
def parse_data():
       
    try:
        
        data = request.json
        if data:
            
            result = parse_data(data)
            return jsonify(result)
    
        else:
            
            return jsonify({"error": "No JSON data provided"}), 400
    
    except Exception as e:
        
        # print(result)
        return jsonify({'error': str(e)}), 500


def parse_data(data):
    
    mongo_uri = "mongodb://localhost:27017/"
    # collection_name="poweroff_api"
    
    client = pymongo.MongoClient(mongo_uri)

    db = client["elxer"]
    # poweroff_collection=db[collection_name]
    
    all_log=db["nas_logs_api"]
    
    lock = threading.Lock()
    
    def post_data_to_api(api_url, data):        
        # return{"R":"yes"}
        
        try:
            
            data_for_json = data.copy()
            for key, value in data.items():
                
                if isinstance(value, ObjectId):                    
                    data_for_json[key] = str(value)
                    
            token = "36A9F18467C3EFD17E223FA125876"
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(api_url, json=data_for_json, headers=headers)
            response.raise_for_status()  
            print("Data posted successfully. Response:", response.text)
            # return response.text
            
        except requests.exceptions.RequestException as err:
            
            print(f"Error posting data: {err}")
    
    try:
        
        with lock:
        
            api_url= "http://10.255.25.66/api_v2/rest_apis/index.php/api/receivedata"
            
            Time = data.get("Time", "")
            date_time=Time.split(" ")
            date=date_time[0]
            date=datetime.strptime(date, "%b/%d/%Y")
            date=date.strftime("%d/%m/%Y")
            date_time=f"{date} {date_time[1]}"
            print("date_time:",date_time)
            
            message = data.get("Message", "")
            
            mac_id_pattern=r"([a-zA-Z0-9]+(:?:[a-zA-Z0-9]+)+)"
            id_pattern1=r"\w+-(\d+)"
            id_pattern2=r"user (\w+ \d+)"
            id_pattern3=r"user ((\w+)\S+)"
            event_pattern=r"authentication failed|connected|disconnected|connection established"
            
            def parse_id(message):
                
                id=re.findall(id_pattern1,message)
                parsed_id=id
                
                if len(parsed_id)!=0:
                    return parsed_id[0]
                
                else:
                    id=re.findall(id_pattern2,message)
                    parsed_id=id
                    
                    if len(parsed_id)!=0:                        
                        return parsed_id[0]
                    
                    else:                        
                        id=re.findall(id_pattern3,message)
                        parsed_id=id
                        
                        if len(parsed_id)!=0:
                            return parsed_id[0][0]
                        
                        else:
                            return None
            

            id=parse_id(message)
            print("id:",id)
            
            parsed_mac_id=re.findall(mac_id_pattern,message)
            
            if len(parsed_mac_id)!=0:
                
                mac_id=parsed_mac_id[0][0]
                print("mac_id:",mac_id)
                
            else:
                pass 
        
            parsed_event=re.findall(event_pattern,message)
            event=parsed_event[0]
            print("event:",event)
            
            if event=="disconnected" or "authentication failed" or "connected":
                
                data={"date_time":date_time,"id":id,"event":event}
                data1=data.copy()
                
                post_data_to_api(api_url, data)
                all_log.insert_one(data)
                return data1
            
            elif event=="connection established":
                
                data={"date_time":date_time,"mac_id":mac_id,"event":event}
                data1=data.copy()
                
                post_data_to_api(api_url, data)
                all_log.insert_one(data)
                return data1

    except Exception as e:
        print(e)

    
if __name__ == '__main__':
    app.run(debug=True)