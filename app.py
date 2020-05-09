from flask import Flask, json, Response , request
from werkzeug.utils import secure_filename
from os import path, getcwd
import time 
from db import Database
from face import Face

app=Flask(__name__)

app.config['file_allow']=['image/png','image/jpeg']
app.config['storage']=path.join(getcwd(),'storage')
app.db= Database()
app.face = Face(app)

def success_handle(output,status=200,mimetype='application/json'):
    return Response(output,status=status,mimetype=mimetype)

def error_handle(error_message,status=500,mimetype='application/json'):
    return Response(json.dumps({"error": {"message":error_message}}),status=status,mimetype=mimetype)

def get_user_by_id(user_id):
    user={}
    results=app.db.select('SELECT users.id, users.name, users.created, faces.id, faces.user_id,faces.filename, faces.created FROM users LEFT JOIN faces ON faces.user_id=? WHERE users.id=?',[user_id,user_id])

    index=0
    for row in results: 
        print("entry is", row)
        face={
            "id":row[3],
            "user_id":row[4],
            "filename": row[5],
            "created":row[6],
        }
        if index==0:
            user={
                "id":row[0],
                "name":row[1],
                "created": row[2],
                "faces": [],
            }
        if face["id"] is not None:
            user["faces"].append(face)
        index=index+1
    if 'id' in user:
        return user
    else:
        return None

def delete_user_by_id(user_id):
    app.db.delete('DELETE FROM users WHERE users.id=?',[user_id])

    app.db.delete('DELETE FROM faces WHERE faces.user_id=?',[user_id])
# router for home testing 
@app.route('/',methods=['GET'])
def homepage():
    print('Welcome to homepage. ')
    output=json.dumps({"api":'1.0'})

    return success_handle(output)

# router for feeding with data 
@app.route('/api/train', methods=['POST'])
def train():
    output=json.dumps({"success":True})
    #if file is not recieved in request 
    if 'file' not in request.files:
        print('Face image is required')
        return error_handle('Face Image is Required.')
    else:
        print("File Request",request.files)

        file=request.files['file']
        
        if file.mimetype not in app.config['file_allow']:
                print("File extension is not allowed")
                return error_handle("File extension not allowed as only *.jpeg or *.png allowed")
        else:
            #get name in form data 
            name=request.form['name']
            print("Person in the image",name)
            #saving the file in local storage
            print("File is allowed and will be saved in ", app.config['storage'])
            filename=secure_filename(file.filename)
            trained_storage=path.join(app.config['storage'],'trained')
            file.save(path.join(trained_storage,filename))
            print("new file name is",filename)

            #save to database.db
            created=int(time.time())
            user_id=app.db.insert('INSERT INTO users(name,created) values(?,?)',(name,created))

            if user_id:
                print("USER SAVED",name,user_id)

                face_id =app.db.insert("INSERT INTO faces(user_id,filename,created) values(?,?,?)", (user_id,filename,created))
                if(face_id):
                    print("Face has been saved")

                    face_data={
                        "id":face_id,
                        "filename": filename,
                        "created":created
                    }

                    return_output= json.dumps({
                        "id":user_id,
                        "name":name,
                        "face": [face_data]
                    })
                    return success_handle(return_output)
                else:
                    print("Something is wrong")
                    return error_handle("SOMETHING WENT WRONG")
            else:    
                print("SOMETHING IS WRONG")
                return error_handle("SOMETHING WENT WRONG")

        print("Request contains image")
    return success_handle(output)

# router for fetching the user or deleting the user 
@app.route('/api/users/<int:user_id>',methods=['GET','DELETE'])
def user_profile(user_id):
    if request.method=='GET':
        user=get_user_by_id(user_id)
        if user:
            return success_handle(json.dumps(user),200)
        else:
            return error_handle("USER NOT FOUND",404)
    if request.method=='DELETE':
        delete_user_by_id(user_id)
        return success_handle(json.dumps({"deleted":True}))


# router for recognizing the face 
@app.route('/api/recognize',methods=['POST'])
def recognize():

    if 'file' not in request.files:
        return error_handle("Image is required")
    else:
        file=request.files["file"]

        # file extension validation 
        if file.mimetype not in app.config["file_allow"]:
            return error_handle("FILE EXTENSION IS NOT ALLOWED")
        else:
            filename=secure_filename(file.filename)
            unknown_storage=path.join(app.config['storage'],'unknown')
            file.save(path.join(unknown_storage,filename))

            user_id = app.face.recognize(filename)
            if user_id:
                user=get_user_by_id(user_id)
                message={"message": "We found {0} matched with your face image".format(user["name"]),"user" :user}
                return success_handle(json.dumps(message))
            else:
                return error_handle("Sorry no person with this face found in our data")
    
    return success_handle(json.dumps({"filename to compare is ": filename }))



app.run(host= '0.0.0.0')