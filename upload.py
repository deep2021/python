from werkzeug.utils import secure_filename
from models.category import Category
from flask import request, Response
from flask import jsonify, Blueprint
from flask import send_from_directory
from runner import db
import os
from flask import current_app
ALLOWED_EXTENS = set(['jpeg','jpg','png','docx','pdf','mp4'])

def allow_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENS


mod = Blueprint('upload',__name__)

@mod.route('/upload', methods=['POST'])
def upload_files():
        if request.method == 'POST':
            if 'file' not in request.files:
                return jsonify({
                    'error':'File part not present'
                    }),404
            
            else:
                 file = request.files['file']
                 if file and  allow_files(file.filename):        
                     filename = secure_filename(file.filename)
                     file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                     print send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
                     return jsonify({
                        'file':'/upload/{}'.format(filename)
                        }), 200
                 else:
                     return jsonify({
                         'message':'No File Exists'
                         }), 200



@mod.route('/upload/<fname>')
def getmyfiles(fname):
        return send_from_directory(current_app.config['UPLOAD_FOLDER'],fname)


@mod.route('/uploads/videos',methods=['POST','GET'])
def myvids():
    if request.method == 'POST':
        db.table('videos').insert(request.get_json())
        return jsonify({'message':'upload success'}),200
    elif request.method == 'GET':
        videos = db.table('videos').get()
        return jsonify({'videos':videos.serialize()}),200


@mod.route('/uploads/videos/<int:id>',methods=['POST','PUT'])
def myvidsdel(id):
    if request.method == 'POST':
        db.table('videos').where('id',id).delete()
        return jsonify({'message':'removed successully'}),200
    elif request.method == 'PUT':
        videos = db.table('videos').where('id',id).update(request.get_json())
        return jsonify({'message':'updated'}),200

@mod.route('/get/pops')
def my_pops():
    popups = db.table('popup').get()
    return jsonify({'popup':popups.serialize()})


@mod.route('/push/pops/<int:id>',methods=['POST','GET'])
def save_pop(id):
    if request.method == 'POST':
        it = db.table('popup').where('pageId',id).update(request.get_json())
        if it:
            return jsonify({
            'message':'Popup updated'
         }),200
        else:
            return jsonify({'message':'no changed were done'}),200
    elif request.method == 'GET':
        pop = db.table('popup').where('pageId',id).first()
        return jsonify({
        'popup':pop
        })
        
    else:
        return jsonify({'message':'Operation not supported'})
