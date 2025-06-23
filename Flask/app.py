from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required,decode_token
import mysql.connector
 
app = Flask(__name__)

# JWT configuration
app.config["JWT_SECRET_KEY"] = "your_secret_key"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 5 * 60 * 60
jwt = JWTManager(app)  
@jwt.unauthorized_loader
def custom_missing_token_response(error):
    return jsonify({"error": "Token is missing"}), 403
 
@jwt.invalid_token_loader
def custom_invalid_token_response(error):
    return jsonify({"error": "Token is invalid or expired"}), 401

 
# connect to my database 
# db_config = {
#     "host": "localhost",
#     "user": "root",
#     "password": "manager",
#     "database": "medicaltrack",
# }

#  connect to host database
db_config={
   "host":"10.233.240.199",
   "user":"Kirti",
   "password":"admin",
   "database":"meditrack",
}


#  connect to cohost
# db_config = {
#     "host":"10.233.240.199",
#     "user":"Admin",
#     "password":"admin",
#     "database":"meditrack",
# }


 
#  API 1  from host database
@app.route("/signin", methods=["POST"])
def login():
    try:
        data = request.json
        email = data["email"]
        password = data["password"]
 
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        print(connection) 
        query = "SELECT * FROM users WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
 
        if user:
            access_token = create_access_token(identity=email)
 
            return jsonify({"message": "Login successful", "token": access_token}), 200
        else:
            return jsonify({"message": "Invalid email or password"}), 401
 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


 
# API 2
@app.route("/auth/validate", methods=["GET"])
def validate_token():
    try:
       token = request.headers.get('Authorization',None)
       if not token:
            return jsonify({"error": "forbidden"}), 403
       token= token.split(" ")[1]
       
       decoded_payload = decode_token(token) 
       return jsonify({"valid": True, "user": decoded_payload}), 200
 
    except Exception as e:
        return f"Error: {e}" ,400

        
    


# API 3
@app.route('/patients/register',methods=["Post"])    
@jwt_required()
def Register_Patient():
    try:
        data = request.json
        first_name =data["first_name"]
        last_name = data["last_name"]
        date_of_birth = data["date_of_birth"]
        gender = data["gender"]
        contact_number= data["contact_number"]
        email = data["email"]
        region_id= data["region_id"]

        if not first_name or not last_name or not date_of_birth or not gender or not contact_number or not email or not region_id:
            return jsonify({"error": "All fields are required"}), 400
       
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)  

        
        query = """insert into patients(first_name,last_name,date_of_birth,gender,contact_number,email,region_id) 
        values(%s, %s, %s, %s, %s, %s, %s) """
        cursor.execute(query, (first_name,last_name,date_of_birth,gender,contact_number,email,region_id))

        connection.commit()
         
        patient_id = cursor.lastrowid
        # Return success response
        return jsonify({"message": "Patient registered successfully" ,"patient_id":patient_id}), 201

    except Exception as e:
        return f"Error: {e}", 403
   
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()    



# API 4
@app.route('/drugs/register',methods=['Post'])
@jwt_required()
def Register_Drug ():
    try:
        data = request.json 
        drug_name = data["drug_name"]
        manufacturer = data["manufacturer"]
        drug_type = data["drug_type"]
        dosage = data["dosage"]
        side_effects = data["side_effects"]

     

        if not drug_name or not manufacturer or not drug_type or not dosage or not side_effects:
            return jsonify({"error": "All fields are required"}), 400
       
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)  
      
        query = """insert into drugs(drug_name,manufacturer,drug_type,dosage,side_effects)
                values(%s, %s, %s, %s, %s) 
                """
        cursor.execute(query, (drug_name,manufacturer,drug_type,dosage,side_effects))

        connection.commit()
         
        drug_id = cursor.lastrowid
        # Return success response
        return jsonify({"message": "drugs registered successfully" ,"drug_id":drug_id}), 201

    except mysql.connector.Error as e:
        return f"Error: {e}", 403
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()  


# API 5
@app.route('/prescriptions/<int:patient_id>/issue',methods=['Post'])
@jwt_required()
def Issue_Prescription(patient_id):
    try:
        data = request.json
        doctor_name= data["doctor_name"]

        if not doctor_name:
            return jsonify({"message":"doctor name  is required"}),400
        
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query ="select patient_id from patients where patient_id = %s"
        cursor.execute(query,(patient_id,))
        patient = cursor.fetchone()
    
        
        if not patient:
            return jsonify({"message":"patients is not present with this id"}),400
        
        cursor.execute("""insert into prescriptions(patient_id,doctor_name,prescription_date)
                       values(%s,%s,now())""",(patient_id, doctor_name))
        
        connection.commit()

        prescription_id =  cursor.lastrowid

        return jsonify({"message": "Prescription issued successfully" ,"prescription_id":prescription_id}), 201
    
    except mysql.connector.Error as e:
        return f"Error: {e}", 403
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close() 


# API 6
@app.route('/consumption/<int:patient_id>',methods=['Post'])
@jwt_required()
def Record_Drug_Consumption(patient_id):
    try:
        data = request.json
        drug_id = data["drug_id"]
        dosage = data["dosage"]

        if not drug_id or not dosage:
          return jsonify({"message":"all feilds are required "}) ,400
    
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = "select patient_id from patients where patient_id = %s"
        cursor.execute(query,(patient_id,))
        patient = cursor.fetchone()

        if not patient:
           return jsonify({"message":"patients is not present with this id"}), 400
    
        cursor.execute("insert into consumption_logs(drug_id,dosage,consumption_time)values(%s,%s,now())",(drug_id,dosage))

        connection.commit()

        consumption_id =  cursor.lastrowid

        return jsonify({"message":"Drug consumption logged successfully","consumption_id": consumption_id}),200
    
    except Exception as e:
         return f"Error: {e}", 403
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


#  APT 7
@app.route('/follows-up/<int:follow_up_id>/status',methods=['Put'])
@jwt_required()
def Update_Follow_Up_Status(follow_up_id):
    try:
       data = request.json
       status = data["status"]

       if not status:
           return jsonify({"merssage":"upadted status is required"}), 400
    
       connection = mysql.connector.connect(**db_config)
       cursor = connection.cursor(dictionary=True)

       query = "update follow_ups set status = %s where follow_up_id = %s"
       cursor.execute(query,(status,follow_up_id,))
    #    details  = cursor.fetchone()
       connection.commit()

       return jsonify({ "message": "Follow_up status updated", "status":"completed"}),201
    
    except Exception as e:
        return f"Error:{e}",403
    
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            

#  API 9
@app.route('/drugs/<int:drug_id>/side-effects',methods=["get"])  
@jwt_required()
def Get_Drug_Side_Effects(drug_id):
    try:

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query= "select side_effect_description,occurrence_rate from drug_side_effects where drug_id = %s"
        cursor.execute(query,(drug_id,))
        result = cursor.fetchone()
    
        if not result :
            return jsonify({"message":" not matching details"}),400
     
        return jsonify({"drug_id":drug_id,"side_effects":result}),200
    
    except Exception as e:
        return f"Error:{e}",400
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()



# API 10
@app.route('/regions/<int:region_id>/consumption',methods=['Get'])
@jwt_required()
def Get_Consumption_Pattern_for_Region(region_id):
    try:

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query ="""select drug_id,drug_consumption_pattern as pattern_details
              from analytics where region_id = %s
              """
        cursor.execute(query,(region_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"message":" not matching details"}),400
        
        return jsonify({"region_id":region_id,"consumption_patterns":result}),200
    except Exception as e:
        return f"Error:{e}",400
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


 # API 11 
@app.route('/patients/<int:patient_id>/consumption-history')
@jwt_required()
def Get_Patient_Consumption_History(patient_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = "select drug_id,dosage,consumption_time from consumption_logs where patient_id = %s"
        cursor.execute(query,(patient_id,))
        result = cursor.fetchone()
        if not result:
           return jsonify({"message":"matching detials are found"}), 400
       
        return jsonify({"patient_id":patient_id,"consumption_history":result}),200
    except Exception as e:
        return f"Error:{e}",400
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
     

# API 12
@app.route('/regions/<int:region_id>/drug_consumption',methods=["Get"])
@jwt_required()
def Track_Regional_Drug_Consumption(region_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query ="select drug_id,consumption_count from region_consumption where region_id=%s"
        cursor.execute(query,(region_id,))
        result = cursor.fetchone()

        if not result:
            return ({"message":"not matching details "}),400
        
        return jsonify({"region_id":"region_id","drug_consumption":result}),200
    
    except Exception as e:
        return f"Error:{e}",400
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
# API 13
@app.route('/patients/<int:patient_id>/follow-ups',methods=['Get'])
@jwt_required()
def Track_Patient_Follow_Ups(patient_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = "select follow_up_date,status from follow_ups where patient_id = %s"
        cursor.execute(query,(patient_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"message":"not matching data found"}),400
        
        return jsonify({"patient_id":patient_id,"follow_ups":result}),200
    
    
    except Exception as e:
        return f"Error:{e}",400
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    


# API 14 
@app.route('/prescriptions/<int:prescription_id>',methods=['Get'])
@jwt_required()
def Get_Prescription_Details(prescription_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = "select prescription_id,doctor_name,prescription_date as date from prescriptions where prescription_id=%s"
        cursor.execute(query,(prescription_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"message":"not matching data found or invalid id "}),400
        
        return (result),200
    except Exception as e:
        return f"Error:{e}",400
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()




#  API 17
@app.route('/analytics/<int:region_id>/<int:drug_id>',methods=['Get'])
@jwt_required()
def Get_Analytics_Report(region_id,drug_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        query = """ select region_id,drug_id,drug_consumption_pattern from analytics 
            where drug_id = %s and region_id= %s;
            """
        
        cursor.execute(query,(region_id,drug_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"Error"  : "No data found to delete "}),400


        return result,200
        # return jsonify({"result":result}),200
        
    except Exception as e:
        return f"Error:{e}",400
    
    finally:
         if connection.is_connected():
            cursor.close()
            connection.close()


   
                     

# API 15 
@app.route('/patients/<int:patient_id>',methods=['delete'])
@jwt_required()
def Delete_Patient_Record(patient_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("select patient_id from patients where patient_id  = %s", (patient_id,))
        check  = cursor.fetchone()

        if not check:
            return jsonify({"Error"  : "No data found to delete "})  

        query = "delete from patients where patient_id=%s"
        cursor.execute(query,(patient_id,))
        connection.commit()

        return jsonify({"message": "Patient record deleted successfully" }),200

         
    except Exception as e:
        return f"Error:{e}",400 
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


@app.route('/drugs/<int:drug_id>',methods=['delete'])            
@jwt_required()
def Delete_Drug_Record(drug_id):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("select drug_id from drugs where drug_id=%s",(drug_id,))
        check = cursor.fetchone()

        if not check:
            return jsonify({"Error"  : "No data found to delete "}),400


        cursor.execute("delete from drugs where drug_id= %s",(drug_id,))
        connection.commit()

        return jsonify({"message": "drug record deleted successfully" }),200

         
    except Exception as e:
        return f"Error:{e}",400 
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
        
  
    
 #    Testing api
# @app.route('/users/serach',methods =['Post'])
# @jwt_required()
# def users():
#     try:
#         data = request.json
#         id =data['id']
#         if not id :
#             return jsonify({"message":" id is required "}), 401
        
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor(dictionary=True)

#         query = "select * from patients where patient_id= %s"
#         cursor.execute(query,(id,))
#         result = cursor.fetchall()

#         connection.commit()

#         if not result:
#             return jsonify({"message":" not matching results"}),401
        
#         return jsonify({"message":"succesfull","result":result}),200
    
#     except Exception as e:
#         return f"Error:{e}", 403
    
    
    # finally:
    #     if connection.is_connected():
    #         cursor.close()
    #         connection.close()


#  testing api 
# @app.route('/users', methods=['GET'])
# @jwt_required()  
# def get_users():
#     try:
       
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor(dictionary=True)  
 
#         cursor.execute("SELECT * FROM regions")
#         result = cursor.fetchall()
 
 
#         return jsonify(result)
#     except mysql.connector.Error as e:
#         return f"Error: {e}", 500
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()



# @app.route('/all/<string:tablename>',methods=['get'])
# @jwt_required()
# def kirti(tablename):
#     try:
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor(dictionary=True)

#         cursor.execute("select * from %s",(tablename,))
#         result = cursor.fetchall()   

#         if not result:
#             return jsonify({"message":"invalid table name"}),400
        
#         return result,200
    
#     except Exception as e:
#         return f"Error: {e} " , 500
#     finally:
#         if connection.is_connected:
#             cursor.close()
#             connection.close()
    

# @app.route('/patients/<int:patient_id>',methods=["Get"])
# @jwt_required()
# def patients(patient_id):
#     try:
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor(dictionary=True)

#         cursor.execute('select * from patients where patient_id = %s',(patient_id,))
#         result = cursor.fetchone()

#         if not result:
#             return jsonify({"message":"id not exists"}),400
        
#         return result,200
#     except Exception as e:
#         return f"Error:{e}",500
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()
            

# @app.route('/doctors/code',methods=['Post'])    
# @jwt_required()
# def patients():
#     try:
#         data = request.json
#         first_name = data["first_name"]
#         last_name = data["last_name"]
#         specialization = data["specialization"]
#         contact_number =data["contact_number"]

#         if  not first_name or not last_name or not specialization or not contact_number:
#            return jsonify({"message":"all fiels are requried"}), 400
    
#         connection = mysql.connector.connect(**db_config)
#         cursor = connection.cursor(dictionary=True)

         
#         cursor.execute("""insert into doctors(first_name,last_name,specialization,contact_number)
#                        values(%s,%s,%s,%s)""",(first_name,last_name,specialization,contact_number,))

        
#         connection.commit()
#         doctor_id = cursor.lastrowid

        
    
#         return jsonify({"message":"succesfuly entered","doctor_id":doctor_id}),200
#     except Exception as e:
#         return f"Error:{e}",500
#     finally:
#         if connection.is_connected():
#             cursor.close()
#             connection.close()

               
 
if __name__ == "__main__":
    app.run(debug=True, port = 2999)

 
