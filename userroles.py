
from models.user import User
from models.role import Role
from flask_orator import jsonify
import jwt
from runner import db
from flask import Blueprint, request
from handlers.access_grant import authentication_required
from webargs.flaskparser import use_args
from webargs import fields


app = Blueprint('userroles',__name__)

key = "bWFkYXJjaG9kIGJlaGVuY2hvZCBnYW5kdSBib3NkaSBrYSBsYW5ndQ=="

@app.route('/user/<int:id>/roles/<int:role>', methods=['POST'])
def role_assignment(id, role):
    role = Role.find(role)
    user = User.find(id).roles
    old_roles = [(lambda y: y.name)(x) for x in user]
    if role.name not in old_roles:
        db.table('roles_users').insert({
            'user_id': id,
            'role_id': role.id
        })

    user_old = User.find(id)
    updated_user = User.find(id).roles
    updated_roles = [(lambda y: y.name)(x) for x in updated_user]

    encoded = {'email': user_old.email,
               'name':  user_old.name,
               'weight': user_old.weight,
               'role': updated_roles}

    data = jwt.encode(encoded, key=key, algorithm='HS256')
    user_old.token = data;
    save = user_old.save()
    if save:
        return jsonify({
            'message': 'Access controls have been updated'
        }), 201
    else:
        return jsonify({
            'message': 'Some Tragedy has happen try again later'
        }), 404

@app.route('/user/<int:id>/roles/<int:role>/revoke', methods=['POST'])
def role_revoke(id, role):
    role = Role.find(role)
    user = User.find(id).roles
    old_roles = [(lambda y: y.name)(x) for x in user]
    if role.name in old_roles:
        db.table('roles_users').where('user_id', id).where('role_id', role).delete()

    user_old = User.find(id)
    updated_user = User.find(id).roles
    updated_roles = [(lambda y: y.name)(x) for x in updated_user]

    encoded = {'email': user_old.email,
               'name': user_old.name,
               'weight': user_old.weight,
               'role': updated_roles}

    data = jwt.encode(encoded, key=key, algorithm='HS256')
    user_old.token = data;
    save = user_old.save()
    if save:
        return jsonify({
            'message': 'Access controls have been updated'
        }), 202
    else:
        return jsonify({
            'message': 'Some Tragedy has happen try again later'
        }), 404

@app.route('/user/all')
def get_user_with_roles():
    users = User.all()
    user_roles = [[str(y.name) for y in x.roles] for x in users]
    user_ids = [x.id for x in users]
    user_names = [x.name for x in users]
    user_emails = [x.email for x in users]
    uinfo = [{"id": x[0], "name":x[1], "email":x[2], "roles": x[3]} for x in zip(user_ids, user_names, user_emails ,user_roles)]

    return jsonify({
        'users': uinfo
    })


@app.route('/user/<string:id>')
@authentication_required
def get_single_user(id):
	user = User.where('email',id).first()

	if user is not None:
		transported = {
			"id":user.id,
			"name":user.name,
			"username":user.username,
			"email":user.email,
			"dob":user.dob,
			"gender":user.gender,
			"weight":user.weight,
            "mobile":user.mobile,
            'roles':user.roles.serialize()
		}
		
		return jsonify({
			"user":transported
		}), 200
	else:
		return jsonify({
			"message":"No Records"
		}), 404


