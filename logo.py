from flask import (Blueprint, request, current_app)
from flask_orator import jsonify
from models.logo import Logo
mod = Blueprint('logo_change',__name__)

@mod.route('/logo/get')
def get_logo():
	return jsonify(Logo.where('id','1').first())

@mod.route('/logo/save',methods=['POST'])
def change_logo():
	if request.is_json:
		logo = Logo.where('id',1).first()
		if logo is not None:
			logo.update(request.get_json())
			return jsonify(logo), 203
		else:
		     	l = Logo.create(request.get_json())	
			return jsonify(l), 201
