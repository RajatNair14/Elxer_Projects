from flask import Flask, request
import requests
import mysql.connector
import re

database = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345")
database_cursor = database.cursor()
database_cursor.execute("create database if not exists erp")
database_cursor.execute("use erp")
database_cursor.execute("CREATE TABLE IF NOT EXISTS user_data(name varchar(40),phone_number varchar(12) UNIQUE NOT NULL,email varchar(60) UNIQUE NOT NULL,password varchar(30))")

app = Flask(__name__)

@app.route('/', methods=['POST'])
def hi():
    return "Welcome to School ERP"


@app.route('/login', methods=['POST'])
def login():
    data=request.json
    email=data.get("email")
    print("email:",email)
    password=data.get("password")
    phone_number=data.get("contact")
    print("phone_number:",phone_number)
    
    def check(passw):
        
        pwd=passw
        print(password)
        if password==None:
            return "Password feild cannot be empty"
        
        elif pwd==password:
            return "Verified User"
        
        elif pwd!=password:
            return "Incorrect Password"
        
        else:
            return "User Not Found"
    
    if database.is_connected():
        try:
            if phone_number==None and len(email)>0:
                cursor=database.cursor()
                query = f"SELECT password FROM user_data WHERE email = '{email}'"
                cursor.execute(query)
                
                rows = cursor.fetchall()
                passw=rows[0][0]
                result=check(passw)
                return result
                
            elif email==None and len(str(phone_number))>0:
                print("NO")
                cursor=database.cursor()
                query = f"SELECT password FROM user_data WHERE phone_number = '{phone_number}'"
                cursor.execute(query)
                
                rows = cursor.fetchall()
                passw=rows[0][0]
                print(passw)
                result=check(passw)
                return result
            
            
        except Exception as e:
            print("e")
            err=str(e)
            print(err)
            if "'NoneType'" in err:
                return "Id feild cannot be empty"
            
            elif "list index out of range" in err:
                return "Incorrect User ID"
            
            else:
                return err
        


@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    print("forgot_password")
    return "forgot_password"


@app.route('/register', methods=['POST'])
def register():
    data=request.json
    name=data.get("name")
    phone_number=data.get("contact")
    email=data.get("email")
    password=data.get("password")
    
    def name_check(input_name):
        name = input_name
        # print("name_check",name)
        if name.isalnum()==False and " " not in name:
                for char in name:
                    if char.isalnum()==False :
                        print(name)
                        return("Special Charectors are not allowed in Name")
                        
                else:                    
                    return(name)

        elif name.isalnum()==False and " " in name:
            for char in name:
                if char.isdigit()==True:
                    return("Digits are not allowed in Name")
                
                
                elif char.isalnum()==False :
                        return("Special Charectors are not allowed in Name")
                         
            else:
                return(name)
        
        elif name.isalnum()==True:
            for char in name:
                # print(char)
                if char.isdigit()==True:
                    return("Digits are not allowed in Name")
                    
            else:
                return(name)
    
    def phone_check(input_phone):
        phone=input_phone
        if phone.isdigit()==True and len(phone)==10:
            return phone
        elif len(phone)<10 and phone.isdigit()==True:
            return "Phone number must contain 10 digits"
        elif phone.isalnum()==True and len(phone)<10:
            return "Phone Number cannot contain Charectors"
        else:
            return "Invalid Number"
        
    def mail_check(input_mail):
        try:
            email=input_mail
            a=0
            regex=r"((.)+[a-zA-Z0-9@.`~_!@#$%^&*-=+:;'<>,/\|{}]+)+@([a-zA-Z]+)+(?:\.([a-zA-Z]+))$"
            result=re.findall(regex,email)
            print(result)
            name_id=result[0][0]
            if name_id.isalnum()==True or "_" in name_id or "_" in name_id:
                if result[0][3]=="com" or result[0][3]=="in":
                    return email
                else:
                    return "Last should be in or com"
            else:
                return "invalid user name in email"
        except Exception as e:
            return "Invalid Input Check your Email Address"

    
    if database.is_connected():
        try: 
            name_checked=name_check(name)
            # print(name_checked)
            phone_checked=phone_check(phone_number)
            email=email.lower()  
            email_checked=mail_check(email)
            if name_checked=="Special Charectors are not allowed in Name":
                return {"error":"Special Charectors are not allowed in Name"}
            elif name_checked=="Digits are not allowed in Name":
                return {"error":"Digits are not allowed in Name"}
            elif phone_checked=="Phone number must contain 10 digits":
                return {"error":"Phone number must contain 10 digits"}
            elif phone_checked=="Phone Number cannot contain Charectors":
                return {"error":"Phone Number cannot contain Charectors"}
            elif phone_checked=="Invalid Number":
                return {"error":"Invalid Number"}
            elif email_checked=="invalid user name in email":
                return {"error":"invalid user name in email"}
            elif email_checked=="Last should be in or com":
                return {"error":"Last should be in or com"}
            elif email_checked=="Invalid Input Check your Email Address":
                return {"error":"Invalid Input Check your Email Address"}

            else:
                cursor=database.cursor()
                query = "INSERT INTO user_data (name, phone_number, email,password) VALUES (%s, %s, %s, %s)"
                values = (name_checked, phone_checked, email_checked,password)
                cursor.execute(query, values)
                database.commit()
                
                db={"Name":name_checked, "Contact":phone_checked,"Email": email_checked}
                return db
        
        except Exception as e:
            
            excp=str(e).split(" ")
            print(excp[-1])
            if excp[-1]=="'user_data.phone_number'":
                return {"error":"Contact already exists"}
            elif excp[-1]=="'user_data.email'":
                return {"error":"Email already exists"}
            else:
                return {"error":e}
            
    
if __name__ == '__main__':
    app.run(debug=True)