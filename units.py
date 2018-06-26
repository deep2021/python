from flask import (Blueprint,request)
from flask_orator import jsonify
from runner import db

mod = Blueprint('units',__name__)

@mod.route('/unit/create',methods=['POST'])
def create_Unit():
	if request.is_json:
		db.table('units').insert(request.get_json())
		return jsonify({
			'message':'created'	
			}),201
	else:
		return jsonify({
				'message':'bad request'		
			}),400	

@mod.route('/unit/',methods=['GET'])
def all_Unit():
	u= db.table('units').get()
	return jsonify(u),200


@mod.route('/unit/<int:id>/update',methods=['PUT'])
def update_Unit(id):
	if request.is_json:
		db.table('units').where('id',id).update(request.get_json())
		return jsonify({
			'message':'updated'	
			}),202
	else:
		return jsonify({
				'message':'bad request'		
			}),400	

@mod.route('/unit/<int:id>/delete',methods=['DELETE'])
def del_unit(id):
	if request.is_json:
		db.table('units').where('id',id).delete()
		return jsonify({
			'message':'deleted'	
			}),204


