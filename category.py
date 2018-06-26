from flask import Blueprint, request
from flask_orator import jsonify
from handlers.access_grant import access_for, authentication_required
from runner import db

mod = Blueprint('category',__name__)


@mod.route('/category/', methods=['GET'])
def category():
    category = db.table('categories').get()
    return jsonify(category), 200

@mod.route('/category/create', methods=['POST'])
def set_categories():
	if request.is_json:
		category = db.table('categories').insert(request.get_json())
		return jsonify(category)
	else:
		return jsonify({"ERR": "You must hAve JSON"})


@mod.route('/category/<int:id>/update', methods=['PUT'])
def update_categories(id):
	if request.is_json:
		return jsonify(db.table('categories').where('id', id).update(request.get_json()))
	else:
		return jsonify({"ERR": "You must hAve JSON"})


@mod.route('/category/<int:id>')
@authentication_required
def single_category(id):
	return jsonify(db.table('categories').where('id', id).first())


@mod.route('/category/<int:id>/diseases')
@authentication_required
def category_with_diseases(id):
	return jsonify(
		db.table('diseases').where('category_id', id).get()
		)

@mod.route('xyz/disease', methods =['GET'])
def test_api():
    sql = "CALL all_diseases_info()";
    return jsonify(db.select(sql)),200

@mod.route('/category/<int:id>/delete',methods=['DELETE'])
@authentication_required
def del_category(id):
    dex = db.select("CALL check_diseases('{}')".format(id))
    dexists= str(dex[0]['exists'])
    if dexists == '1':
        print 'delete all disease----'
        ad = db.table('diseases').where('category_id',id).get().serialize()
        for x in ad:
            print x['id']
            tex = db.select("CALL check_treatment('{}')".format(x['id']))
            texists = str(tex[0]['exists'])
            if texists == '1':
                db.table('treatments').where('disease_id',x['id']).delete()
                print 'delete treatment for {}'.format(x['id'])
            dgx = db.select("CALL check_diagnosis('{}')".format(x['id']))
            dgexists = str(dgx[0]['exists'])
            if dgexists == '1':
                db.table('dignoses').where('disease_id',x['id']).delete()
                print 'delete diagnosis for {}'.format(x['id'])
            eqx  =  db.select("CALL check_equation('{}')".format(x['id']))
            eqxist = str(eqx[0]['exists'])
            if eqxist == '1':
                db.table('equations').where('disease_id',x['id']).delete()
                print 'delete all equations'
            
            db.table('diseases').where('id',x['id']).delete()
            print 'delete disease {}'.format(x['id'])

        print 'delete all disease----'
        dit = db.select("CALL check_indicators('{}')".format(id))
        ditex =  str(dit[0]['exists'])
        if ditex == '1':
            db.table('indicators').where('categories_id',id).delete()
        db.table('categories').where('id',id).delete()
        print 'delete category {}'.format(id)

    else:
        dit = db.select("CALL check_indicators('{}')".format(id))
        ditex =  str(dit[0]['exists'])
        if ditex == '1':
            db.table('indicators').where('categories_id',id).delete()
        db.table('categories').where('id',id).delete()
        print 'delete category {}'.format(id)
        print 'just delete categories'
    return jsonify({"message":dex}),200


