from flask import (jsonify, Blueprint)
from runner import db
mod = Blueprint('history',__name__)
# user token need to be processed to frtch token

@mod.route('/history')
def get_history():
	x= db.table('injuries').join('users','injuries.user_id','=','users.id').select('users.name as username ','injuries.name as name','status').get()
	print x.serialize()
	return jsonify(x.serialize()), 200


@mod.route('/history/<int:id>')
def indivisual_history(id):
	x= db.table('injuries').where('user_id',id)\
		.join('users','injuries.user_id','=','users.id')\
		.join('treatments','injuries.treatment_id','=','treatments.id')\
		.join('diseases','injuries.disease_id','=','diseases.id')\
		.select('users.name as name',
			'treatments.price as price',
			'diseases.name as disease',
			'treatments.description as prescription',
			'injuries.status as status',
			'injuries.tsummary as summary')\
		.get().serialize()

	return jsonify(x), 200


