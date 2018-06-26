from flask import(Blueprint, request)
from flask_orator import jsonify
from models.healthybar import Healthybar
from runner import db

mod = Blueprint('healthybar', __name__)

@mod.route('/health/equation/save', methods=['POST'])
def create_health_param():
	if request.is_json:
		d = db.table('healthybars').where('id', id).insert(request.get_json())
		return jsonify(d)
	else:
		return jsonify({'message':'Invalid Syntax'}),400
		
		
@mod.route('/public/equation/save', methods=['POST'])
def create_public_param():
	if request.is_json:
		d = db.table('public_health').where('id', id).insert(request.get_json())
		return jsonify(d)
	else:
		return jsonify({'message':'Invalid Syntax'}),400


@mod.route('/other/equation/save', methods=['POST'])
def create_other_param():
	if request.is_json:
		d = db.table('other_health').where('id', id).insert(request.get_json())
		return jsonify(d)
	else:
		return jsonify({'message':'Invalid Syntax'}),400


@mod.route('/health/equation/<int:id>/update', methods=['PUT'])
def uptae_health_param(id):
	if request.is_json:
		bar = db.table('healthybars').where('id', id).update(request.get_json())
		return jsonify({'message':'updated'}),200
	else:
		return jsonify({'message':'Invalid Syntax'}),400
		

@mod.route('/public/equation/<int:id>/update', methods=['PUT'])
def uptae_public_param(id):
	if request.is_json:
		bar = db.table('public_health').where('id', id).update(request.get_json())
		return jsonify({'message':'updated'}),200
	else:
		return jsonify({'message':'Invalid Syntax'}),400
		

@mod.route('/other/equation/<int:id>/update', methods=['PUT'])
def uptae_other_param(id):
	if request.is_json:
		bar = db.table('other_health').where('id', id).update(request.get_json())
		return jsonify({'message':'updated'}),200
	else:
		return jsonify({'message':'Invalid Syntax'}),400


@mod.route('/health/equation/all')
def get_health_param():
		return jsonify(db.table('healthybars').get()),200


@mod.route('/public/equation/all')
def get_public_param():
		return jsonify(db.table('public_health').get()),200


@mod.route('/other/equation/all')
def get_other_param():
		return jsonify(db.table('other_health').get()),200


@mod.route('/health/equation/<int:id>', methods=['POST'])
def drop_health_param(id):
	d = db.table('healthybars').where('id', id).delete()
	return jsonify({'message':'dropped'}), 204


@mod.route('/public/equation/<int:id>', methods=['POST'])
def drop_public_param(id):
	d = db.table('public_health').where('id', id).delete()
	return jsonify({'message':'dropped'}), 204


@mod.route('/other/equation/<int:id>', methods=['POST'])
def drop_other_param(id):
	d = db.table('other_health').where('id', id).delete()
	return jsonify({'message':'dropped'}), 204


