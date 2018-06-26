from flask import Blueprint
from flask_orator import jsonify
from models.dignose import  Dignosis
from flask import request
mod = Blueprint('diagnostix', __name__)
from runner import db

@mod.route('/diagnose/', methods = ['GET'])
def all():
    if request.method == 'GET':
        d = db.table('dignoses')\
                .join('diseases','dignoses.disease_id','=','diseases.id')\
                .select('dignoses.id as id','dignoses.name as name','dignoses.pricetag as pricetag','dignoses.summary as summary','dignoses.image as image','diseases.name as disease','dignoses.created_at as created_at')\
                .get()
        return jsonify({
            'diagnosis': d.serialize()
            }), 200
    else:
        return jsonify({
            'message':'Invalid Syantax'
            }), 200




@mod.route('/diagnose/create', methods = ['POST'])
def create_diagnostix():
    if request.is_json:
        d =  db.table('dignoses').insert(request.get_json())
        return jsonify({
            'message':'created successfully'
            }), 201
    else:
        return jsonify({
            'message':'Invalid Syantax'
            }), 200

@mod.route('/diagnose/<int:id>', methods = ['PUT'])
def edit_diagnostix(id):
    if request.is_json:
        d =  db.table('dignoses').where('id',id).update(request.get_json())
       
        return jsonify({
            'message': "ok"
            }), 203
    else:
        return jsonify({
            'message':'Invalid Syantax'
            }), 200

@mod.route('/diagnose/<int:id>/delete', methods = ['DELETE'])
def del_diagnostixi(id):
    if request.is_json:
        d =  db.table('dignoses').where('id',id).delete()
        return jsonify({
            'message': "ok"
            }), 204
    else:
        return jsonify({
            'message':'Invalid Syantax'
            }), 200


