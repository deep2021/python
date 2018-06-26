from flask import (jsonify,Blueprint)
from runner import (db,mail)
from flask_mail import Message
import json
mod = Blueprint('contacts',__name__)
from flask import request
@mod.route('/send/message', methods = ['POST'])
def make_contact():
    message = request.get_json()
    dump = json.dumps(message)
    db.table('allmessages').insert({
        'body':dump
        })
    return jsonify ({'message':'sent'}),200


@mod.route('/retrieve/messages')
def retrive_messages():
    messages = db.table('allmessages').get()\
                 .pluck('body').map(lambda x: json.loads(x))\
                 .serialize()

    return jsonify(
            {'messages':messages}
            )

