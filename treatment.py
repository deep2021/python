from flask import request
from flask_orator import jsonify
from flask import Blueprint
from runner import db

app = Blueprint('treatment',__name__)

@app.route('/treatment/create', methods=['POST'])
def create_treatment():
    if request.is_json:
        treatment = db.table('treatments').insert(request.get_json())
        return jsonify(treatment)
    else:
        return jsonify('Invalid syntax')

@app.route('/treatment/<int:id>/update', methods=['PUT'])
def update_treatment(id):
    treatment = db.table('treatments').where('id',id).update(request.get_json())
    return jsonify(treatment)

@app.route('/treatments')
def all_treatments():
    treatment = db.table('treatments')\
                .join('diseases','diseases.id','=','treatments.disease_id')\
                .select('treatments.name as name','treatments.description as description','treatments.price as price','treatments.id as id','diseases.name as disease','treatments.duration as duration')\
                .get()
    return jsonify(treatment)

@app.route('/treatment/<int:id>')
def single_treatment(id):
    treatment= db.table('treatments').where('id', id).first()
    return jsonify(treatment)

@app.route('/treatment/<int:id>/delete', methods=['DELETE'])
def delete_treatment(id):
    treatment = db.table('treatments').where('id', id).delete()
    return jsonify(treatment)











