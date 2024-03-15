from flask import Flask, jsonify, request
import subprocess
import pymongo
import keyboard
import json
import time
import re
from datetime import datetime, timedelta
import pytz
import time
import requests
from bson import ObjectId
import configparser
import threading


app = Flask(__name__)


@app.route('/')
def hi():
    return "Hello"

@app.route('/process_json_file', methods=['POST'])
def process_json_file():
       
    try:
        
        json_data = request.json
        if json_data:
            
            result = process_json(json_data)
            return jsonify(result)
    
        else:
            
            return jsonify({"error": "No JSON data provided"}), 400
    
    except Exception as e:
        
        # print(result)
        return jsonify({'error': str(e)}), 500


def process_json(json_data):

    # return json_data
    mongo_uri = "mongodb://localhost:27017/"
    
    collection_name="poweroff_api"
    collection_name1="onu_offline_api"
    collection_name2="Data_Error_api"
    collection_name3="Data_time_Error_api"
    
    client = pymongo.MongoClient(mongo_uri)

    db = client["elxer"]
    poweroff_collection=db[collection_name]
    onu_offline_collection=db[collection_name1]
    Error_data=db[collection_name2]
    time_error_collection=db[collection_name3]
    
    all_log=db["logs_api"]
    error_level_0=db["poweroff_api"]
    error_level_00=db["onu_offline_api"]
    error_level_1=db["events_api"]
    error_level_2=db["issues_api"]
    error_level_3=db["incidents_api"]
    error_mis=db["Data_Error_api"]
    error_los=db["Onu_los_came_first_then_poweroff"]
    error_time=db["Data_time_Error_api"]
    
    lock = threading.Lock()
    

    def test(api_url):
        return api_url
    
    
    def convert_timezone(input_time_str, from_timezone, to_timezone):
        
        input_format = "%Y-%m-%d %H:%M:%S"
        input_time = datetime.strptime(input_time_str, input_format)
        from_tz = pytz.timezone(from_timezone)
        to_tz = pytz.timezone(to_timezone)
        converted_time = from_tz.localize(input_time).astimezone(to_tz)
        return converted_time


    def post_data_to_api(api_url, data):        
        # return{"R":"yes"}
        
        try:
            
            # config = configparser.ConfigParser()
            # config.read('config.ini')
            # header = config['Credentials']['headers']
            
            data_for_json = data.copy()
            for key, value in data.items():
                
                if isinstance(value, ObjectId):                    
                    data_for_json[key] = str(value)
                    
            token = "36A9F18467C3EFD17E223FA125876"
            headers = {"Authorization": f"Bearer {token}"}
            # response = requests.post(api_url, json=data_for_json, headers={"Authorization": f"Bearer {header}"})
            response = requests.post(api_url, json=data_for_json, headers=headers)
            response.raise_for_status()  
            print("Data posted successfully. Response:", response.text)
            # return response.text
            
        except requests.exceptions.RequestException as err:
            
            print(f"Error posting data: {err}")

    try:
        
        with lock:

            # return json_data
            
            # config = configparser.ConfigParser()
            # config.read('config.ini')
            # api_url = config['Credentials']['api_url']
            # api_url= "http://10.255.25.66/api"
            api_url= "http://10.255.25.66/api_v2/rest_apis/index.php/api/receivedata"
            
            def onu_pon(data):
            
                value=data
                
                pattern=r"\d\W\W(\d)\W\W(\d{1,2})"
                pattern1=r"\d\W(\d)\W(\d{1,2})"
                pattern2=r"\d\W\W(\d) ONU (\d{1,2})"
                pattern3=r"\d\W(\d) ONU (\d{1,2})"
                pattern4=r"EPON0\W\W(\d)\W(\d{1,2})"

                a=re.findall(pattern,value)
                
                if len(a)!=0:
                    
                    # print(a)
                    pon_id=a[0][0]
                    onu_id=a[0][1]
                    return pon_id,onu_id
                    
                if len(a) == 0:
                    
                    a=re.findall(pattern1,value)
                    
                    if len(a)!=0:
                        
                        # print(a)
                        pon_id=a[0][0]
                        onu_id=a[0][1]
                        return pon_id,onu_id
                        
                    if len(a)==0:
                        
                        a=re.findall(pattern2,value)
                        
                        if len(a)!=0:
                            
                            # print(a)
                            pon_id=a[0][0]
                            onu_id=a[0][1]
                            return pon_id,onu_id
                        
                        if len(a)==0:
                            
                            a=re.findall(pattern3,value)
                            
                            if len(a)!=0:
                            
                                # print(a)
                                pon_id=a[0][0]
                                onu_id=a[0][1]
                                return pon_id,onu_id
                            
                            if len(a)==0:
                                
                                a=re.findall(pattern4,value)
                                
                                if len(a)!=0:
                                    
                                    # print(a)
                                    pon_id=a[0][0]
                                    onu_id=a[0][1]
                                    return pon_id,onu_id
                                
                                else:
                                    pass
                        
                        
            # level = json_data["level"]
            # print("Situation Level:", level)
            

            hostip = json_data.get("hostip", "")
            print("Host Ip Address:", hostip)
            # return hostip
            
            def error_data(data):
                
                error_mis.insert_one(data)        
                # return{"result":"Already in error_mis"}
                
            def error_time_data(data):
                error_time.insert_one(data)

            time1 = str(json_data.get("time", {}))
            input_time = time1.replace("T"," ")
            
            if "." in input_time:
                input_time=input_time.split(".")
                
            elif "+" in input_time:
                input_time=input_time.split("+")
  
            else:
                pass
            
            input_time_str=input_time[0]
            time2=input_time_str
            # from_timezone = "UTC"
            # to_timezone = "Asia/Kolkata"
            # converted_time = convert_timezone(input_time_str, from_timezone, to_timezone)
            # time2 = converted_time.strftime('%Y-%m-%d %H:%M:%S')
            print("Date_Time:", time2)
            time3=time2.split(" ")
            only_time=time3[1]
            print("time:",only_time)
            # return time2
                        

            message = json_data.get("message", "") or json_data.get("msg", "")
            
            pattern = r"offline|Dying Gasp|DYING_GASP|online|ONU Deregister|ONU Register|PON LOS Recovery|PON LOS|LinkDown|LinkUp|deregistered|registered|ONU AUTH Success|ONU MAC Conflict|configuration error"
            event = re.findall(pattern, message)
            issue=message
            if len(event) != 0:
                
                print("event:", event[0])
                # return event[0] 
                
                match event[0]:
                    
                    case "offline" | "Dying Gasp" | "DYING_GASP" | "online" | "ONU Deregister" | "ONU Register" | "deregistered" | "registered" | "ONU AUTH Success" | "ONU MAC Conflict" | "configuration error":
                        
                        pon_onu=onu_pon(message)
                        pon_id=pon_onu[0]
                        onu_id=pon_onu[1]
                        print("pon_id:",pon_id)
                        print("onu_id:",onu_id)
                        
                        curr_date=(datetime.today().date().strftime("%Y-%m-%d"))
                        curr_time=(datetime.today().time().replace(microsecond=0).strftime("%H:%M:%S"))
                        curr_date_time=f'{curr_date} {curr_time}'
                        date_now=datetime.today().date().strftime("%Y-%m-%d")
                        input_date1=time2.split(" ")
                        input_date=input_date1[0]
                        time111 = datetime.strptime(time2, "%Y-%m-%d %H:%M:%S")
                        time222 = datetime.strptime(curr_date_time, "%Y-%m-%d %H:%M:%S")

                        time_difference = time222 - time111
                        time_difference=str(time_difference)
                        print("Time Difference:", time_difference)
                        # return(input_date)
                        
                        if input_date!=date_now:
                            
                            data={"date_time": time2,"host_ip": hostip,"pon_id": pon_id}
                            # print(data)
                            # return(data)
                            data2={"host_ip": hostip,"pon_id": pon_id}
                            found_data=Error_data.find_one(data2)
                            print(found_data)
                            # return(found_data)
                            
                            if found_data is None:
                                error_data(data)

                        check_pattern=r"reason:"
                        check_reason=re.findall(check_pattern,message)
                        
                        if len(check_reason)!=0:
                            
                            reason_pattern=r"(?<=reason:) ([a-zA-Z0-9]+_[a-zA-Z0-9]+|[a-zA-Z0-9]+)"
                            reason_match=re.findall(reason_pattern,message)  
                            reason= reason_match[0].replace("_"," ").strip()
                            print("reason:",reason)
                            
                            match reason:
                                
                                case "POWER OFF":
                                    
                                    data={"host_ip":hostip,"pon_id":pon_id,"onu_number":onu_id}
                                    data0=({"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"reason":reason,"pon_id":pon_id,"onu_number":onu_id})
                                    data1=({"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"reason":reason,"pon_id":pon_id,"onu_number":onu_id})
                                    event="ONU OFFLINE"
                                    message="POWER OFF"
                                    data2=({"date_time":time2,"host_ip":hostip,"event":event,"reason":message,"pon_id":pon_id,"onu_number":onu_id})
                                    data4=({"date_time":time2,"host_ip":hostip,"issue":issue,"event":message,"pon_id":pon_id,"onu_number":onu_id})
                                    poweroff_database=poweroff_collection.find_one(data)
                                    onu_offline_database=onu_offline_collection.find_one(data)
                                    time_error_db=time_error_collection.find_one(data)   
                                    data3=data2.copy()
                                    # print(data2)
                                    
                                    if onu_offline_database != None:
                                        
                                        # post_data_to_api(api_url, data4)
                                        onu_offline_collection.delete_one(data)
                                        error_level_0.insert_one(data)
                                        if only_time!=curr_time :
                                            error_time_data(data1)
                                        all_log.insert_one(data0)
                                        error_level_1.insert_one(data2)                                        
                                        error_los.insert_one(data2)
                                        return data4,{"result":"First gave offline then gave power off but situation handled and data deleted from onu offline collection"} 
                                    
                                    elif poweroff_database is None:
                                        
                                        if only_time!=curr_time :
                                            error_time_data(data1)
                                        all_log.insert_one(data0)    
                                        error_level_0.insert_one(data)
                                        error_level_1.insert_one(data2)
                                        return data3
                                    
                                    if only_time!=curr_time :
                                        error_time_data(data1)  
                                    all_log.insert_one(data0)    
                                    return data3
                                                                    
                                
                                case "LOSI":
                                    
                                    data={"host_ip":hostip,"pon_id":pon_id,"onu_number":onu_id}
                                    data0=({"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"reason":reason,"pon_id":pon_id,"onu_number":onu_id})
                                    data1=({"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"reason":reason,"pon_id":pon_id,"onu_number":onu_id})
                                    event="ONU OFFLINE"
                                    message="LOS"
                                    data2=({"date_time":time2,"host_ip":hostip,"issue":issue,"event":event,"reason":message,"pon_id":pon_id,"onu_number":onu_id})     
                                    poweroff_database=poweroff_collection.find_one(data)
                                    time_error_db=time_error_collection.find_one(data)              
                                    data3=data2.copy()
                                    # print(data2)
                                    
                                    if poweroff_database is None:
                                        
                                        # post_data_to_api(api_url, data2)
                                        error_level_00.insert_one(data)
                                        if only_time!=curr_time :
                                            error_time_data(data1)
                                        all_log.insert_one(data0)
                                        error_level_1.insert_one(data2)
                                        error_level_2.insert_one(data2)
                                        return data3
                                    
                                    else:
                                        if only_time!=curr_time :
                                            error_time_data(data1)
                                        all_log.insert_one(data0)
                                        error_level_1.insert_one(data2)
                                        return {"result":"data in power off database"} 
                                        
                                case default:
                                    pass
                                
                            
                        else:
                            
                            match event[0]:
                                
                                case "Dying Gasp" | "DYING_GASP":
                                    
                                    data={"host_ip":hostip,"pon_id":pon_id,"onu_number":onu_id}
                                    data0=({"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"pon_id":pon_id,"onu_number":onu_id})
                                    data1=({"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"pon_id":pon_id,"onu_number":onu_id})
                                    event="ONU OFFLINE"
                                    message="POWER OFF"
                                    data2=({"date_time":time2,"host_ip":hostip,"event":event,"reason":message,"pon_id":pon_id,"onu_number":onu_id})
                                    data4=({"date_time":time2,"host_ip":hostip,"issue":issue,"event":message,"pon_id":pon_id,"onu_number":onu_id})
                                    poweroff_database=poweroff_collection.find_one(data)
                                    onu_offline_database=onu_offline_collection.find_one(data)
                                    time_error_db=time_error_collection.find_one(data)   
                                    data3=data2.copy()
                                    # print(data2)
                                    
                                    if onu_offline_database != None:
                                        
                                        # post_data_to_api(api_url, data4)
                                        onu_offline_collection.delete_one(data)
                                        error_level_0.insert_one(data)
                                        if only_time!=curr_time:
                                            error_time_data(data1)
                                        all_log.insert_one(data0)
                                        error_level_1.insert_one(data2) 
                                        error_los.insert_one(data2)                                       
                                        return data4,{"result":"First gave offline then gave power off but situation handled and data deleted from onu offline collection"} 
                                    
                                    elif poweroff_database is None:
                                        
                                        if only_time!=curr_time:
                                            error_time_data(data1)
                                        all_log.insert_one(data0)
                                        error_level_0.insert_one(data)
                                        error_level_1.insert_one(data2)
                                        return data3,{"result":"data added to power off database"} 
                                    
                                    if only_time!=curr_time:
                                        error_time_data(data1)
                                    all_log.insert_one(data0)
                                    return {"result":"data already in power off database"} 
                                
                                case "ONU Deregister"|"offline"|"deregistered":
                                    
                                    data={"host_ip":hostip,"pon_id":pon_id,"onu_number":onu_id}
                                    data0={"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"pon_id":pon_id,"onu_number":onu_id}
                                    data1={"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"pon_id":pon_id,"onu_number":onu_id}
                                    event="ONU OFFLINE"
                                    message="LOS"
                                    data2={"date_time":time2,"host_ip":hostip,"issue":issue,"event":event,"reason":message,"pon_id":pon_id,"onu_number":onu_id}                        
                                    poweroff_database=poweroff_collection.find_one(data)
                                    onu_off_database=onu_offline_collection.find_one(data)
                                    time_error_db=time_error_collection.find_one(data)   
                                    data3=data2.copy()
                                    print(data2)
                                                                                        
                                    if poweroff_database is None:
                                        
                                        if onu_off_database is None:
                                                            
                                            # post_data_to_api(api_url, data2)
                                            error_level_00.insert_one(data)
                                            if only_time!=curr_time:
                                                error_time_data(data1)
                                            all_log.insert_one(data0)
                                            error_level_1.insert_one(data2)
                                            error_level_2.insert_one(data2) 
                                            return data3
                                        
                                        else:
                                            
                                            if only_time!=curr_time:
                                                error_time_data(data1)
                                            all_log.insert_one(data0)
                                            return {"result":"data already in onu offline database"} 
                                    
                                    else:
                                        
                                        if only_time!=curr_time:
                                            error_time_data(data1)                                      
                                        all_log.insert_one(data0)
                                        error_level_1.insert_one(data2)
                                        return {"result":"data in power off database"} 
                                
                                case "ONU Register":
                                    
                                    # data0=({"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"pon_id":pon_id,"onu_number":onu_id})
                                    data=({"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"pon_id":pon_id,"onu_number":onu_id})
                                    data1=data.copy()
                                    all_log.insert_one(data)
                                    return data1
                                
                                case "online" | "ONU AUTH Success" | "registered":
                                    
                                    data={"host_ip":hostip,"pon_id":pon_id,"onu_number":onu_id}
                                    data0=({"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"pon_id":pon_id,"onu_number":onu_id})
                                    data1=({"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"pon_id":pon_id,"onu_number":onu_id})
                                    event="ONU ONLINE"
                                    data2=({"date_time":time2,"host_ip":hostip,"issue":issue,"event":event,"pon_id":pon_id,"onu_number":onu_id})
                                    onu_off_database=onu_offline_collection.find_one(data)
                                    poweroff_database=poweroff_collection.find_one(data)
                                    time_error_db=time_error_collection.find_one(data)   
                                    data3=data2.copy()
                                    
                                    if poweroff_database is not None:
                                        
                                        # post_data_to_api(api_url, data2)
                                        if only_time!=curr_time:
                                            error_time_data(data1)
                                        all_log.insert_one(data0)
                                        error_level_1.insert_one(data2)
                                        poweroff_collection.delete_one(data)
                                        return {"result":"data was in power off database but now its removed"} 
                                            
                                    elif onu_off_database is not None:
                                        
                                        # post_data_to_api(api_url, data2)
                                        if only_time!=curr_time:
                                            error_time_data(data1)
                                        all_log.insert_one(data0)
                                        error_level_1.insert_one(data2)
                                        error_level_2.insert_one(data2)
                                        onu_offline_collection.delete_one(data)
                                        return {"result":"data was in ONU Offline database but now its removed"} 
                                    
                                    else:
                                        
                                        if only_time!=curr_time:
                                            error_time_data(data1)
                                        all_log.insert_one(data0)
                                        error_level_1.insert_one(data2)
                                        return data3
                                
                                case "ONU MAC Conflict" | "configuration error":
                                    
                                    issue=message
                                    event="ONU Error"
                                    data={"date_time":time2,"host_ip":hostip,"issue":issue,"event":event,"issue":issue,"pon_id":pon_id,"onu_number":onu_id}
                                    data0={"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event,"issue":issue,"pon_id":pon_id,"onu_number":onu_id}
                                    data2={"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event,"issue":issue,"pon_id":pon_id,"onu_number":onu_id}
                                    data3={"host_ip":hostip,"pon_id":pon_id,"onu_number":onu_id}
                                    time_error_db=time_error_collection.find_one(data3)   
                                    data1=data.copy()
                                    # post_data_to_api(api_url, data)
                                    if only_time!=curr_time:
                                        error_time_data(data2)
                                    all_log.insert_one(data0)
                                    error_level_1.insert_one(data)
                                    return data1  
                                   
                    case 'PON LOS' | 'PON LOS Recovery':
                        
                        # return message
                        pattern=r"\d/(\d)"
                        a=re.findall(pattern,message)
                        pon_id=a[0]
                        print("pon_id:",pon_id)
                        # return pon_id
                        time_error_db=time_error_collection.find_one(data)   
                        
                        match event[0]:
                            case 'PON LOS':
                                
                                data= {"date_time":time2,"host_ip":hostip,"issue":issue,"event":event[0],"pon_id":pon_id}
                                data0= {"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"pon_id":pon_id}
                                data2= {"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"pon_id":pon_id}
                                data1=data.copy()
                                # print(data)     
                                    
                                # post_data_to_api(api_url, data)
                                if only_time!=curr_time:
                                    error_time_data(data2)
                                all_log.insert_one(data0)
                                error_level_1.insert_one(data)
                                error_level_3.insert_one(data)
                                return data1
                            
                            case 'PON LOS Recovery': 
                                
                                data0={"date_time":time2,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"pon_id":pon_id}
                                data1={"date_time":time2,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"pon_id":pon_id}       
                                event="PON LOS RECOVERY"
                                data= {"date_time":time2,"host_ip":hostip,"issue":issue,"event":event,"pon_id":pon_id}  
                                data2=data.copy()
                                # print(data1)
                                # print(data) 
                                    
                                # post_data_to_api(api_url, data)
                                if only_time!=curr_time:
                                    error_time_data(data1)
                                all_log.insert_one(data0)
                                error_level_1.insert_one(data)
                                error_level_3.insert_one(data)
                                return data2
                            
                            case default:
                                return {"result":"Nither PON LOS Nor PON LOS RECOVERY"}   
                        
                    case "LinkDown"|"LinkUp":
                        
                        time_parse_linkupdown=time2.split(".")
                        time_linkupdown=time_parse_linkupdown[0]
                        pattern=r"[a-zA-Z]\d\/(\d)"
                        a=re.findall(pattern,message)
                        pon_id=a[0]
                        print("pon_id:",pon_id)
                        time_error_db=time_error_collection.find_one(data)   
                        
                        match event[0]:
                            
                            case "LinkDown":
                                
                                data0={"date_time":time_linkupdown,"curr_date_time":curr_date_time,"host_ip":hostip,"message":issue,"event":event[0],"pon_id":pon_id}
                                data1={"date_time":time_linkupdown,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"pon_id":pon_id}  
                                event="PON LOS"
                                data= {"date_time":time_linkupdown,"host_ip":hostip,"issue":issue,"event":event,"pon_id":pon_id} 
                                data2=data.copy()
                                # print(data1)
                                # print(data)  
                                        
                                # post_data_to_api(api_url, data)
                                if only_time!=curr_time:
                                    error_time_data(data1)
                                all_log.insert_one(data0)
                                error_level_1.insert_one(data)
                                error_level_3.insert_one(data)
                                return data2
                            
                            case "LinkUp": 
                                
                                data0={"date_time":time_linkupdown,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"message":issue,"event":event[0],"pon_id":pon_id}
                                data1={"date_time":time_linkupdown,"curr_date_time":curr_date_time,"Time Difference":time_difference,"host_ip":hostip,"event":event[0],"pon_id":pon_id}       
                                event="PON LOS RECOVERY"
                                data= {"date_time":time_linkupdown,"host_ip":hostip,"issue":issue,"event":event,"pon_id":pon_id}
                                data2=data.copy() 
                                # print(data1)
                                # print(data)   
                                    
                                # post_data_to_api(api_url, data)
                                if only_time!=curr_time:
                                    error_time_data(data1)
                                all_log.insert_one(data0)
                                error_level_1.insert_one(data)
                                error_level_3.insert_one(data)
                                return data2
                                    
                            case default:
                                return {"result":"Nither linkup Nor linkdown"}
                        
                    case default:
                        return {"result":"Event not that Important"}
                        
            else:
                return {"result":"Event other than Important events"}  
              
        # print("*"*33)
        
    except Exception as err:
        print(err)

# if __name__ == '__main__':
#     app.run(debug=True)