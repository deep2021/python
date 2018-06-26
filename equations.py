from models.equation import Equation
from flask import (request, jsonify)
from flask import Blueprint
from runner import db
from orator.orm.collection import Collection
app = Blueprint('equations', __name__)


@app.route('/equations')
def get_them_all():
    d = db.select("select diseases.id as Id, diseases.name as name from diseases")
    e = [{"Id":x.Id
        ,"name":x.name,
        "equations":db.select("select * from equations where disease_id={}".format(x.Id)),
        "diagnosis":db.select("select * from dignoses where disease_id ={} limit 1".format(x.Id)),
        "treatment":db.select("select * from treatments where disease_id={} limit 1".format(x.Id))}
        for x in d]

    print e
    return jsonify(e),200


@app.route('/equation/<int:id>')
def get_single_equation(id):
    return jsonify(
        Equation.find(id).serialize()
    )


@app.route('/equation/create', methods=['POST'])
def create_equation():
    sql = ["CALL createEquation('{equation}','{opr}','{disease_id}')".format(**c) for c in request.get_json()]
    [db.select(x) for x in sql]
    return jsonify({'message':'created'}),200


@app.route('/equation/<int:id>', methods=['PUT'])
def update_equation(id):
    return jsonify(
        db.table('equations').where('id',id).update(request.get_json())
    )

@app.route('/equation/update', methods=['PUT'])
def updatie_equation():
    t = request.get_json()["treatment"]
    e = request.get_json()["equations"]
    d = request.get_json()["diagnosis"]
    db.select("START TRANSACTION")
    for x in t:
       db.table("treatments").where('id',x['id']).update(x)
    for x in e:
       db.table("equations").where('id',x['id']).update(x)

    for x in d:
       db.table("dignoses").where('id',x['id']).update(x)

    db.select("COMMIT")
    return jsonify(
            request.get_json()
    )


@app.route('/equation/<int:id>', methods=['DELETE'])
def drop_equation(id):
    return jsonify(
        Equation.find(id).delete()
    )
