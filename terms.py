from flask import (jsonify,Blueprint,request)
from runner import db

mod = Blueprint('terms',__name__)

@mod.route('/terms',methods=['GET'])
def get_terms():
    t = db.table('terms').get()
    return jsonify(t.serialize()),200


@mod.route('/terms/add',methods=['POST'])
def set_terms():
    terms = request.get_json()
    db.table('terms').insert(terms)
    return jsonify({'message':'created'}),201

@mod.route('/terms/<int:id>/edit',methods=['PUT'])
def edit_term(id):
    db.table('terms').where('id',id).update(request.get_json())
    return jsonify({'message':'updated'}),202


@mod.route('/terms/<int:id>/delete',methods=['POST'])
def delete_terms(id):
    db.table('terms').where('id',id).delete()
    return jsonify({'message':'deleted'}),200
