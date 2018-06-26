from models.disease import Disease
from handlers.calculate import calculate, give_treatment, get_user,insert_injury,preview_map,calculate_health,calculate_public,calculate_other
from unidecode import unidecode
from flask_orator import jsonify
from flask import Blueprint,request
from handlers.access_grant import  authentication_required
from runner import db
from itertools import izip_longest
import math as m
import datetime
from flask import render_template
from jinja2 import Environment
from orator.orm.collection import Collection
from handlers.access_grant import checkPrevious 
from utils.check import (appL,R,filterEquation,fixEmAll,separateIds, finalStep)
app = Blueprint('diagnosis', __name__)


@app.route('/dx/preview/<int:id>/<int:uid>', methods=['POST'])
@authentication_required
@checkPrevious
def preview(id,uid):
    req = request.get_json()
    first = request.get_json()[0]
    user = db.table('users').where('id',uid).first()['weight']
    second = first.copy()
    intermediate = {'variable':'w','number':user,'conv':'None','name':'weight'}
    second.update(intermediate)
    req.append(second)
    x= preview_map(uid,req,id)
    image = request.get_json()[0]['image']
    db.select("insert into user_attachments(id,user_id,attachment) values(null,'{}','{}')".format(uid,image))
    calculate_health(uid,x)
    calculate_public(uid,x)
    calculate_other(uid,x)
    return jsonify(
                req
            )


@app.route('/dx/health/<int:id>', methods=['POST'])
@authentication_required
def calc_health(id):
    x= calculate_health(id,request.get_json())
    return jsonify(
      x
    )
    
@app.route('/dx/public/<int:id>', methods=['POST'])
@authentication_required
def public_health(id):
    x= calculate_public(id,request.get_json())
    return jsonify(
      x
    )


@app.route('/dx/other/<int:id>', methods=['POST'])
@authentication_required
def other_health(id):
    x= calculate_other(id,request.get_json())
    return jsonify(
      x
    )


@app.route('/dx/<int:category>/calculate/for/<int:id>', methods=['POST'])
def diagonize(category,id):
    categoryI = db.table('categories').where('id',category).first()
    t2 = categoryI.nextTime
    nextTime = db.table('user_orders').latest().first()
    today = datetime.datetime.now()
    if nextTime :
        ntt =  nextTime['nextDate']
        delta = today- ntt
        check = delta.days
        if check < nextTime:
           """ return jsonify({
                    'message':'You are not Eligible'
                        }),200
           """              
           print nextTime

    disease = Disease.with_('equations').where('category_id',category).get()
    ndfa = Disease.with_('equations', 'bloodtests', 'treatment').where('category_id',category).get();
    alpha= ndfa.map(lambda d:{
     'id':d.id,
     'equations':d.equations.filter(lambda x:appL(x.equation)).map(lambda x:x.serialize())
    }).all()
    indicators = db.select("select indicators.variable , indicators.equation from indicators where indicators.categories_id = {}".format(category))
    c= finalStep(ndfa,list(indicators)) 
    test_data = request.get_json()
    refined_equations = [
        {
            'name': d.id,
            'equations': d.equations.pluck('equation').transform(lambda eq: unidecode(eq)).all(),
            'operator': d.equations.pluck('opr').transform(lambda eq: unidecode(eq)).reject(lambda z: z == 'None').all(),
            'tests':list(indicators)
         }
        for d in disease
    ]


    redif_equations = [
        {
            'name': d["id"],
            'equations': d["equations"].pluck('equation').transform(lambda eq: unidecode(eq)).all(),
            'operator': d["equations"].pluck('opr').transform(lambda eq: unidecode(eq)).reject(lambda z: z == 'None').all(),
            'tests':list(indicators)
         }
        for d in alpha
    ]
    
    
    oax_equations = [
        {
            'name': d["id"],
            'equations': d["equations"].pluck('equation').transform(lambda eq: unidecode(eq)).all(),
            'operator': filter(lambda x: not x == 'None',R(d["equations"].pluck('opr').transform(lambda eq: unidecode(eq)).reject(lambda z: z == 'None').all())),
            'tests':list(indicators)
         }
        for d in alpha
        ]


    g =   Collection(indicators).all()
    print refined_equations
    d = calculate(id,test_data, *c)
    #return jsonify({'err':c}),203
    z =  [give_treatment(id,x,test_data, g) for x in d]
    return jsonify(z),200


@app.route('/test/<int:id>/user/<int:uid>',methods=['POST'])
def getConn(id, uid):
    c =Disease.find(id)
    d = Disease.find(id).treatment
    y = Disease.find(id).equations
    z = Disease.find(id).bloodtests
    test_data = request.get_json()
    refined = {
		"user":get_user(uid),
        "name":c.id,
        "equations":y.pluck('equation').transform(lambda eq: unidecode(eq)).all(),
        "operator":y.pluck('opr').transform(lambda eq: unidecode(eq)).reject(lambda z: z == 'None').all(),
        "tests":z.pluck('variable').all(),
		"sample":z.pluck('name').all()

    }

    #d = calculate(uid,test_data, refined)
    #z =  [give_treatment(uid,x) for x in d if x]
    print refined
    return jsonify(z),200


@app.route('/dx/map/<int:id>/local',methods=['POST'])
def map_to_inputs(id):
    user_data = request.get_json()
    original_data = db.table('categories').join('indicators','categories.id','=','indicators.categories_id').select('indicators.variable as variable').where('categories.id',id).get()
    default_params = ["{}".format(x) for x in [0]*12];
    default_values = [x['variable'] for x in original_data]
    merge = [{'variable':v,'number':k} for k,v in zip(default_params,default_values)]
    return jsonify(merge),200


@authentication_required
@app.route('/dx/user/<int:id>/treatment',methods=['GET'])
def user_treatments(id):
    sql = "SELECT d.name,d.description as priscription, d.created_at as date FROM users u, user_di_tr b, treatments d WHERE u.id = b.user_id AND d.id = b.treatment_id AND u.id = {}"\
            .format(id);
    treatment= db.select(sql)
    print treatment
    return jsonify(treatment
            ),200


@authentication_required
@app.route('/dx/user/<int:id>/dignoses',methods=['GET'])
def user_dignoses(id):
    sql = "SELECT d.name,d.image,d.created_at as date FROM users u, user_diagnoses b, dignoses d WHERE u.id = b.user_id AND d.id = b.diagnosis_id AND u.id = {}".format(id);
    treatment= db.select(sql)
    print treatment
    return jsonify(treatment
            ),200


@authentication_required
@app.route('/dx/user/<int:id>/diseases',methods=['GET'])
def user_diseases(id):
    sql= "SELECT d.name,d.created_at as date FROM users u, user_diseases b, diseases d WHERE u.id = b.user_id AND d.id = b.disease_id AND u.id = {}".format(id);
    treatment= db.select(sql)
    print treatment
    return jsonify(treatment
            ),200


@authentication_required
@app.route('/dx/user/<int:id>/health',methods=['GET'])
def user_dases(id):
    sql= "SELECT b.health, b.created_at as date FROM users u,user_histories b where u.id = b.user_id AND u.id = {}".format(id);
    treatment= db.select(sql)
    print treatment
    return jsonify(treatment
            ),200


@authentication_required
@app.route('/dx/user/<int:id>/public',methods=['GET'])
def user_public_bc(id):
    sql= "SELECT b.health, b.created_at as date FROM users u,user_public_health b where u.id = b.user_id AND u.id = {}".format(id);
    treatment= db.select(sql)
    print treatment
    return jsonify(treatment
            ),200



@authentication_required
@app.route('/dx/user/<int:id>/other',methods=['GET'])
def user_other_mc(id):
    sql= "SELECT b.health, b.created_at as date FROM users u,user_other_health b where u.id = b.user_id AND u.id = {}".format(id);
    treatment= db.select(sql)
    print treatment
    return jsonify(treatment
            ),200


  

@app.route('/dx/previewT/<int:id>/<int:uid>', methods=['POST'])
@checkPrevious
def previewT(id,uid):
    return jsonify({
        'message':'You are done'
        }) 
