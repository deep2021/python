from flask import (jsonify, Blueprint, request)
from runner import db
mod = Blueprint('appmgmt',__name__)
# user token need to be processed to frtch token

@mod.route('/appmgmt/contact/save',methods=['POST'])
def get_appmgmt():
    contact = request.get_json()['contact']
    db.table('about').where('id','1').update({'contact':contact})
    return jsonify({'message':contact}), 200


@mod.route('/appmgmt/contact',methods=['GET'])
def get_appmgmt_ctx():
    c = db.table('about').where('id','1').first()
    return jsonify({'contact':c.serialize()}), 200


@mod.route('/appmgmt/revoke/<int:pid>/<string:roles>',methods=['POST'])
def indivisual_appmgmt(id):
	return jsonify({'return details':id}), 200


