from models.user import User
from utils.observers import UserObserver
from flask import request, jsonify
from webargs.flaskparser import use_args
from webargs import fields
import re
import bcrypt
from flask import Blueprint
from runner import db
from runner import mail
from flask_mail import Message
import random
from handlers.access_grant import makepassword
from flask import current_app
from flask import send_from_directory
import string

User.observe(UserObserver())
app = Blueprint('usermgmt', __name__)


user_args = {
    'name': fields.Str(required=True),
    'username': fields.Str(required=True),
    'password': fields.Str(validate=lambda x: len(x) > 6),
    'dob':  fields.Str(validate=lambda x: len(x) == 10),
    'weight': fields.Float(validate=lambda x: x > 0),
    'email': fields.Str(validate=lambda x: re.match(r"[^@]+@[^@]+\.[^@]+", x) is not None),
    'gender': fields.Str(validate=lambda x: len(x) == 1)

}

login_args = {
    'email': fields.Str(required=True),
    'password':fields.Str(validate=lambda x:len(x) > 6)
}

user_mail_template ="<h3>Hello {}</h3><p>You have succesfully registered login to your account to continue<br> Your one time otp is {}</p>"
reset_template = "<h3>Password has been reset successfully !</h3><br><p>Your new password is {}</p>"

admin_template ="<h3>New user with details registered recently</h3>"
admin_template+="<table border=1>"
admin_template+="<tr>"
admin_template+="<td>email</td><td>{email}</td>"
admin_template+="</tr><tr>"
admin_template+="<td>name</td><td>{name}</td>"
admin_template+="</tr><tr>"
admin_template+="<td>gender</td><td>{gender}</td>"
admin_template+="</tr>"
admin_template+="</table>"



def code_generator():
    return str(random.randint(1000,9999)) 


def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/signup', methods=['POST'])
@use_args(user_args)
def user_signup_link(args):
    role = db.table('roles').where('name', 'user').first()
    user = db.table('users').where('username', args['username']).first() or db.table('users').where('email', args['email']).first() 
    if user is None:
        new_user = User().fill(args)
        new_user.role_id = role.id
        new_user.save()
        code = code_generator();
        db.table('roles_users').insert({
            'role_id': role.id,
            'user_id': new_user.id
        })
        print 'Adding verification'
        db.table('verifications').insert({
            'user_id':new_user.id,
            'code':code
        })

        print "sending mail"
        message = user_mail_template.format(args['name'],code)
        msg =   Message(
                    subject="Welcome",
                    html=message,
                    sender="noreply@medicalratios.net",
                    recipients=[args['email']]
                    )

        adminM = admin_template.format(**args)
        mass =   Message(
                    subject="New Registration",
                    html=message,
                    sender="noreply@medicalratios.net",
                    recipients=["powmalion@gmail.com"]
                    )

        mail.send(msg)
        mail.send(mass)

        return jsonify({"message": new_user.serialize()})
    else:
        return jsonify({'message': 'User exists'})

@app.route('/login', methods=['POST'])
@use_args(login_args)
def login_handler(args):
    email = args['email']
    passw = b"{}".format(args['password'])
    user = db.table('users').where('email', email).first() or db.table("users").where('username', email).first()
    print email
    if user is None:
        return jsonify({'message': 'Username or EmailId not Exists'}), 404
    else:
        if user.active == "0":
            return jsonify({'isActive':user.active})
        elif bcrypt.checkpw(passw,str(user.password)):
                return jsonify({
                    'email':user.email,
                    'token': str(user.token)
                })
        else:
            print(passw)
            print(bcrypt.hashpw(passw, bcrypt.gensalt(15)))
            print(user.password)
            return jsonify({
                    "message": "Invalid Credentials"
                    })



@app.route('/upload/profile/pic/<int:id>', methods=['POST','GET'])
def upload_pic_user(id):
    user = db.table('users').where('id',id).first()
    if request.method == 'POST':
        if user is not None:
            db.table('users').where('id',id).update({
                'profile_pic':request.get_json()['image']
                })

            return jsonify({
                'message':'success'
                })

    elif request.method == 'GET':
        print user
        if user is not None:
            return send_from_directory(current_app.config['UPLOAD_FOLDER'],user.profile_pic)
        else:
            return jsonify({
                'message':'No Data Available'
                })



@app.errorhandler(422)
def error_handler_422(err):
    exc = err
    print(exc.message)
    return jsonify({
        'errors': "Invalid Request"
    }), 422


@app.route('/user/<string:email>/activate',methods=['POST'])
def activate_user(email):
    user = db.table('users').where('email',email).first()
    if user is not None:
        verfication = db.table('verifications').where('user_id',user.id).first()
        if verfication is not None:
            if verfication.code == request.get_json()['code']:
                db.select('START TRANSACTION')
                db.select('update users set active= "1" where users.id= {}'.format(user.id))
                db.select('COMMIT')
                return jsonify({'token':user.token})
            else:
                return jsonify({'message':'wrong verification code'})
        else:
            return jsonify({'message':'Something wrong happens'})
    else:
        return jsonify({'message':'No user exists'})


@app.route('/user/<string:email>/reset_password',methods=['POST'])
def update_password(email):
    user = db.table('users').where('email', email).first()
    old = request.get_json()['old']
    new = request.get_json()['new']
    if user is not None:
        if bcrypt.checkpw( b"{}".format(old),str(user.password)):
            check = makepassword(new,user.id)
            if check == True:
                return jsonify({
                    'message':'password changed succesfully'
                })
            else:
                return jsonify({
                    'message':'Some Error Occured'
                })
        else:
            return jsonify({
                'message':' Old password not matchs'
            })
    else:
        return jsonify({'Wrong email Id'})





@app.route('/user/<int:id>/update', methods=['PUT'])
def update_user(id):
	user = db.table('users').where('id',id).update(request.get_json())
	if user is not None:
		return jsonify({
			'message':'updated'
			}), 202
	else:
		return jsonify({}), 404	


@app.route('/user/mail',methods=['GET'])
def mailer():
    admin_message = admin_template.format(**{'email':'Johndoe@gmail.com','name':'John Doe','gender':'Male'})
    msg =   Message(
                    subject="New Registration",
                    html=admin_message,
                    sender="noreply@medicalratios.net",
                    recipients=["powmalion@gmail.com"]
                    )
    mail.send(msg)
    return 'TEST SUCCESS'



@app.route('/user/<int:id>/delete', methods=['DELETE'])
def del_user(id):
    db.select("delete from roles_users where user_id={}".format(id))
    db.select("delete from users where id={}".format(id))
    return jsonify({
        'message':'deleted'
        }), 202


@app.route('/out/<int:id>',methods=['POST'])
def make_offline(id):
    db.select("CALL trigger_offline({})".format(id))
    return jsonify({
        'message':'ok'
        }),200

@app.route('/in/<int:id>', methods= ['POST'])
def make_online(id):
    db.select("CALL trigger_online('{}')".format(id))
    return jsonify({
        'message':'ok'
        }),200


@app.route('chat/status/<int:user>/<int:status>')
def make_custom_des(user,status):
    db.select("SET @user='{}'".format(user))
    db.select("INSERT into online_users(id,)")

@app.route('/status/online',methods=['POST'])
def check_status():
    x = db.table('online_users').left_join('users', 'users.id' ,'=','user_id').select('email','username','name','users.id as Id', 'online_users.online as online').get().serialize()
    return jsonify({
        'online':x
        }),200


@app.route('/user/forgotten/<string:email>',methods=['POST'])
def forgotten_password(email):
    user = db.table('users').where('email',email).first()
    if user is not None:
        new = id_generator()
        changed = makepassword(new,user.id)
        if changed:
            message = reset_template.format(new)
            msg = Message(
                    subject="password reset info",
                    html=message,
                    sender="noreply@medicalratios.net",
                    recipients=[user.email]
                    )
            mail.send(msg)


        return jsonify({'message':'your password has been reset successfully ...check your email'})
    else:
        return jsonify({'message':'wrong user name'})
