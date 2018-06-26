from models.user import User
from utils.observers import UserObserver
from flask import request, jsonify
from webargs.flaskparser import use_args
from webargs import fields
import re
import bcrypt
from flask import Blueprint
from runner import db
import random
from handlers.access_grant import makepassword,authentication_required
import string
app = Blueprint('adminuserspace', __name__)



user_args = {
    'name': fields.Str(required=True),
    'username': fields.Str(required=True),
    'password': fields.Str(validate=lambda x: len(x) > 6),
    'dob':  fields.Str(validate=lambda x: len(x) == 10),
    'weight': fields.Float(validate=lambda x: x > 0),
    'email': fields.Str(validate=lambda x: re.match(r"[^@]+@[^@]+\.[^@]+", x) is not None),
    'gender': fields.Str(validate=lambda x: len(x) == 1)

}

@authentication_required
@app.route('/admin/make/signup', methods=['post'])
@use_args(user_args)
def make_signup_for_admin(args):
    role = db.table('roles').where('name', 'user').first()
    user = db.table('users').where('username', args['username']).first() or db.table('users').where('email', args['email']).first() 
    if user is None:
        new_user = User().fill(args)
        new_user.role_id = role.id
        new_user.active=1
        new_user.save()
        db.table('roles_users').insert({
            'role_id': role.id,
            'user_id': new_user.id
        })

        return jsonify({"message": new_user.serialize()}),200
    else:
        return jsonify({'message': 'user exists'}),402

