from flask import (Blueprint,jsonify,request)
from runner import db
import json
from orator.orm.collection import Collection
from utils.check import(appL,E,Y,checkFunc,cleanFunc,splitFunc)

mod = Blueprint('user_reports',__name__)

userlist = lambda x:db.table('user_diseases')\
                      .join('users','user_diseases.user_id','=','users.id')\
                      .join('diseases','diseases.id','=','user_diseases.disease_id')\
                      .where('diseases.id',x)\
                      .select('users.name as fullname','diseases.category_id as CategoryId','users.id as UserId','user_diseases.bloodtest as bt','diseases.created_at as timestamp')\
                      .get()



userReport = lambda x,y:db.table('user_diseases')\
                      .join('users','user_diseases.user_id','=','users.id')\
                      .join('diseases','diseases.id','=','user_diseases.disease_id')\
                      .where('diseases.id',x)\
                      .where('users.id',y)\
                      .select('users.name as fullname','diseases.category_id as CategoryId','users.id as UserId','user_diseases.bloodtest as bt')\
                      .get()\
                      .unique('fullname')



userReport = lambda x:json.loads(
                                    db.table('user_orders').where('user_id','{}'.format(x))\
                                                            .latest()\
                                                            .first()['summary'])[0]['blood_test']



def identify_colors(equation,variable,number):
    eq = eval(equation,{variable:number})
    data = {
        'number':number,
        'equation':equation,
        'result':eq
    }
    (min, max) = map(lambda x: x.strip(), equation.split('and'))
    if eval(min,{variable:number}):
        if eval(max,{variable:number}):
            return '#008000'
        else:
            return '#F00'
            
    else:
        return '#004e80'



@mod.route('/users/reports/base',methods=['GET','POST'])
def get_user_base_diseases():
    dummy = 'x1 or x2 or x3 or x5 or x6 or x7 or x8 or x9 or x10 or x11 or x12 or w > 0'
    if request.method == 'POST':
        if request.get_json()['next'] == 'users':
            nully = userlist(request.get_json()['DiseaseNo'])
            if nully:
                xqw =  nully.transform(lambda x: {
                    'userId':x['UserId'],
                    'labels':Collection(json.loads(x['bt'])).transform(lambda x: {'name':x['name'],'value':x['number']}).all(),
                    'values':Collection(json.loads(x['bt'])).pluck('number').all(),
                    'color':Collection(json.loads(x['bt'])).map(lambda x:identify_colors(x['equation'],x['variable'],x['number'])).all(),
                    'name':x['fullname'],
                    'timestamp':x['timestamp']
                })
                return jsonify({
                        's':xqw.serialize()
                        })
        elif request.get_json()['next'] == 'reports':
            category = request.get_json()['CatNo']
            users = request.get_json()['userId']
            print userReportNew(category,92).all()
            return jsonify({
                'reports': Collection(allReports).collapse().all()
                })

        return jsonify({
            'message':'not found'
            })
    else:
        diseases = db.table('diseases').select('id','name').get().serialize()
        return jsonify({
            'next':'users',
            'field':'DiseaseNo',

            'diseases':diseases
            })


@mod.route('/indicators/equation', methods = ['POST','GET'])
def make_indicator_equation():
    if request.method == 'GET':
        indicators = db.table('indicators').get()
        return jsonify({
            'indicators':indicators.serialize()
            })
    elif request.method == 'POST':
        payload = request.get_json()
        indicatorId = request.args.get('flag')
        if db.table('indicators').where('id', indicatorId).update(request.get_json()):
            return jsonify({
                'message':'modified'
                })
        else:
            return jsonify({
                'message':'updation failed may be wrong indicator'
                })


@mod .route('/indicator/test', methods=['GET'])
def make_indicator_test():
    test = db.table('indicators').get().transform(
                lambda x: identify_colors(x['equation'],x['variable'],205)           
            )\
    .all()

    return jsonify({
        'results':test
        })



   

@mod.route('/user/single/report/<int:id>/<int:disease>',methods=['GET'])
def make_single_user_report(id,disease):
    user = db.table('users').where('id',id).first()
    if user is not None:
        reports = db.table('user_diseases').where('user_id',id).where('disease_id',disease).get()
        if reports is not None:
            report = {
            'user':user.name,
            'reports':reports.map(lambda y: {
                                    'date':y['created_at'],
                                    'report':{
                                        'labels':Collection(json.loads(y['bloodtest'])).pluck('name').all(),
                                        'values':Collection(json.loads(y['bloodtest'])).pluck('number').all(),
                                        'colors':Collection(json.loads(y['bloodtest']))\
                                                                 .transform(lambda x:identify_colors(x['equation'],x['variable'],x["number"])).all()
                                        }
                                    }).all()
            }
            return jsonify({
                'reports':report
            })
        else:
            return jsonify({
                'message':'No Reports Available for User'
            })
    else:
        return jsonify({
            'message':'user doesnt exists'
        })

@mod.route('/users/make/defaults/unit/<id>',methods=['POST'])
def make_default_units(id):
    query = "insert into user_defaults_units(id,user_id,unit)values(null,{},'{unit}') on duplicate key update unit='{unit}'".format(id,**request.get_json())
    db.select(query)
    return jsonify({
    'message':'saved'
    }),200

@mod.route('/users/get/defaults/unit/<id>',methods=['GET'])
def get_default_units(id):
    unit =  db.table('user_defaults_units').where('user_id',id).first()

    if unit is not None:
        return jsonify({
                    'defaults':unit
         }),200
    else:
        return jsonify({'message':'units not set for you'})



@mod.route('/equate/test')
def check_equation_test():
    kc = db.table('equations').get().filter(lambda x:appL(x.equation)).all()
    return jsonify({'t':kc})
