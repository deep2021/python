from flask import request
from flask_orator import jsonify
from flask import Blueprint
from handlers.access_grant import  authentication_required,access_for
from runner import db
import json
app = Blueprint('disease',__name__)

@app.route('/disease/', methods=['GET'])
@authentication_required
def disease():
    sql = "SELECT * , (select categories.name from categories where categories.id = diseases.category_id) as category FROM diseases"
    alt = db.select(sql)
    disease =  db.table('diseases').get()
    return jsonify(alt)

@app.route('/disease/create', methods=['POST'])
def index():
    if request.is_json:
        disease = db.table('diseases').insert(request.get_json())
        return jsonify(disease),201
    else:
        return jsonify({"ERR": "You must hAve JSON"})

@app.route('/disease/<int:id>/update', methods=['PUT'])
def update_disease(id):
    if request.is_json:
        disease =  db.table('diseases').where('id',id).update(request.get_json())
        return jsonify(disease)
    else:
        return jsonify({"ERR": "You must hAve JSON"})

@app.route('/disease/<int:id>')
@authentication_required
def single(id):
    return jsonify(db.table('diseases').where('id',id).first())

@app.route('/disease/<int:id>/treatment')
@authentication_required
def disease_treatment(id):
    d = db.table('diseases').where('id',id).first()
    return jsonify(
    	d
	)

@app.route('/disease/<int:id>/tests')
def disease_tests(id):
    d = db.table('blood_tests').select('name','variable').where('disease_id',id).get()
    return jsonify(
		d.serialize()
	)



@app.route('/category/<int:id>/tests')
def categories_indicators(id):
    d = db.table('indicators').select('id','name','variable','description','default_unit').where('categories_id',id).get()
    return jsonify(
		d.serialize()
	)


@app.route('/category/tests',methods=['POST'])
def create_indicators():
    c= request.get_json()['category']
    print c
    indicator = request.get_json()['indicators']
    sql = u"CALL creatCategory('{name}','{about}','{image}','{nextTime}')".format(**c)
    cat = db.select(sql)
    dex= [ x for x in cat][0]['ID']
    ilist= ["CALL createIndicator('{}','{name}','{variable}','{description}')".format(dex,**x) for x in indicator]
    for x in ilist:
        db.select(x)
    return jsonify({'message':'created'}),200

@app.route('/category/<int:id>/tests',methods=['PUT'])
def edit_indicator(id):
    category = db.table('categories').where('id',id).update(request.get_json()['category'])
    indicator = request.get_json()['indicators']
    ilist= ["CALL edit_indicator('{id}','{name}','{variable}','{description}')".format(**x) for x in indicator]
    for x in ilist:
        db.select(x)
    return jsonify({'message':'updated'}),200

@app.route('/tests/<int:id>/remove',methods=['POST'])
def remove_indicators(id):
    d = db.table('indicators').where('id',id).delete()
    return jsonify({'message':'deleted'}),200



@app.route('/user/<int:id>/summary')
def user_summary(id):
   user =  db.select("select user_diseases.disease_id as id, user_diseases.created_at as date from user_diseases where user_id = {}".format(id))
   ind = db.select("select test, indicator from user_blood_indicators where user_id={}".format(id))
   diseases = [
           { "id":x['id'],
             "disease":[
                 {
                     "category":y['category_id'],
                     "disease":y,
                     "bloodReport":db.select("select test,indicator from user_blood_indicators where user_id={} and catID = {}".format(id,y['category_id']))
                     }
                   for y in db.select("select name, description, icon, category_id from diseases where id= {} limit 1".format(x['id']))
                 ],
             "date":x['date'],
             "treatment":db.select("select treatments.name , treatments.price, treatments.description from treatments where treatments.disease_id= {} limit 1".format(x['id'])),
             "diagnoses":db.select("select name, summary, pricetag,image from dignoses where disease_id={} limit 1".format(x['id']))
               } for x in user]
   return jsonify(diseases)


@app.route('/about/get')
def about_app():
    return jsonify(db.select("select text,contact from about limit 1")[0])



@app.route('/about/update', methods=['POST'])
def about_update():
    db.table('about').where('id', 1).update({
        'text':request.get_json()['about']
    })
    return jsonify({    
        "message":"ok"
        })

@app.route('/disease/<int:id>/delete', methods=['DELETE'])
def del_disease(id):
    
    tex = db.select("CALL check_treatment('{}')".format(id))
    texists = str(tex[0]['exists'])
    if texists == '1':
        db.table('treatments').where('disease_id', id).delete()
        print 'delete treatment for {}'.format(id)
    dgx = db.select("CALL check_diagnosis('{}')".format(id))
    dgexists = str(dgx[0]['exists'])
    if dgexists == '1':
        db.table('dignoses').where('disease_id', id).delete()
        print 'delete diagnosis for {}'.format(id)
    eqx = db.select("CALL check_equation('{}')".format(id))
    eqxist = str(eqx[0]['exists'])
    if eqxist == '1':
        db.table('equations').where('disease_id', id).delete()
        print 'delete all equations'
    
    db.table('diseases').where('id', id).delete()
    print 'delete disease {}'.format(id)
    return jsonify({
        "message":'deleted'
        }),200




