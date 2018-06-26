
from flask import (jsonify, Blueprint)
from runner import db
from flask import request
from orator.orm.collection import Collection

mod = Blueprint('user_permission',__name__)
# user token need to be processed to frtch token

@mod.route('/permissions/for/<int:id>',methods=['POST'])
def save_permissions(id):
    perm = request.get_json()
    db.table('user_permission').insert(request.get_json())
    return jsonify({'message':'permissions created'})


@mod.route('/permissions/for/<int:id>',methods=['PUT'])
def update_permissions(id):
    perm = request.get_json()
    db.table('user_permission').where('user_id',id).update(request.get_json())
    return jsonify({'message':'user_Permissions updated'}), 200



@mod.route('/permissions/for/<int:id>',methods=['GET'])
def list_permissions(id):
    fg = db.select('describe user_permission')
    pm = ["'{}'".format(x['Field']) for x in fg]
    up = db.table('user_permission').where('user_id',id).first()
    print up
    return jsonify({'permission':up})

@mod.route('/permissions/list',methods=['GET'])
def get_permissions():
    fg = db.select('describe user_permission')
    pm = [{'name':x['Field'],'value':'0'} for x in fg]
    #val = ['0']*22

    #li = dict(zip(pm,val))
    return jsonify({'list':pm}), 200


@mod.route('/permissions/for/<int:id>',methods=['DELETE'])
def delete_permissions(id):
    up = db.table('user_permission').where('user_id',id).delete()
    return jsonify({'message':'permission deleted'})
