from flask import request,jsonify
from models.blood_test import BloodTest
from flask import Blueprint

app = Blueprint('tests',__name__)

@app.route('/tests')
def get_bloodtests():
    return jsonify(
        BloodTest.all().serialize()
    )

@app.route('/test/<int:id>')
def get_single_bloodtest(id):
    return jsonify(
        BloodTest.find(id).serialize()
    )

@app.route('/test/<int:id>/update', methods=['PUT'])
def update_test(id):
    return jsonify(
        BloodTest.find(id).update(request.get_json())
    )

@app.route('/test/create', methods=['POST'])
def create_test():
    for i in request.get_json():
        BloodTest.create(i)

    return jsonify(
        {"message": "ok"}
    )
