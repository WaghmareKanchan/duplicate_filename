from flask import Flask, render_template, request, redirect, send_file 
from pymongo import MongoClient
from werkzeug.utils import secure_filename 
from bson import ObjectId
import os 
import uuid 
import datetime  

app = Flask(__name__, template_folder='template')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient('mongodb://localhost:27017/')
collection = client['logic']['logic']

@app.route('/', methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        file = request.files['file']
        
        if file and file.filename:
            original_name = secure_filename(file.filename)
            base, ext = os.path.splitext(original_name)
            
            count = collection.count_documents({'original_filename': original_name})
            
            if count == 0:
                save_name = original_name 
            else:
                save_name = f"{base}({count + 1}){ext}"
                
            unique_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                f"{uuid.uuid4()}_{save_name}"
            )
            
            file.save(unique_path)
            
            print(f"[UPLOAD] originals='{original_name}' saved_as='{save_name}' path='{unique_path}'")
            
            collection.insert_one({
                'ID'    : id,
                'name'  : name,
                'original_filename' : original_name,
                'save_filename'     : save_name,
                'file_location'     : unique_path,
                'uploaded_at'       : datetime.datetime.utcnow()
            })
            
            return redirect('/data')
        
    return render_template('index.html')

@app.route('/data')
def data():
    logic = list(collection.find().sort('uploaded_at', -1))
    for row in logic:
        row['_id'] = str(row['_id'])
    return render_template('download.html',logic=logic)

@app.route('/download/<record_id>')
def download_file(record_id):
    
    return()

if __name__ == '__main__':
    app.run(port=5000, debug=True)