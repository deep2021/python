from flask import (Blueprint, request, current_app)
from flask_orator import jsonify
from models.question import Questions as Question
from runner import db

mod = Blueprint('question',__name__)

@mod.route('/question/create', methods=['POST'])
def create_queston():
	if request.is_json:
		db.table('questions').insert(request.get_json())	
		return jsonify({'message':'created'}), 200
	else:
		return jsonify({}), 404




@mod.route('/question/user/<int:id>', methods=['POST'])
def my_questions(id):
	if request.is_json:
		data = Question.where('user_id',id).get()
		return jsonify(data)
	else:
		return jsonify({}), 404



@mod.route('/question/<int:id>/update', methods=['PUT'])
def update_question(id):
	if request.is_json:
		data = db.table('questions').where('id', id).update(request.get_json())
		return jsonify({'status':data}), 200
	else:
		return jsonify({}), 404




@mod.route('/question/all', methods=['GET'])
def all_question():
	if request.is_json:
		data =	db.table('questions')\
			  .select('questions.question as question','questions.answer as answer','questions.status as status','users.name as name', 'questions.id as id')\
			  .join('users','questions.user_id','=','users.id')\
			  .get()

		return jsonify(data)
	else:
		return jsonify({}), 404


@mod.route('/question/test', methods=['POST'])
def test_question():
	if request.is_json:
		data = request.get_json()
		return jsonify(data)
	else:
		return jsonify({}), 404



