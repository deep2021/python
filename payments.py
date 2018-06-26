from orator.orm.collection import Collection
from flask import (Blueprint,request)
from flask_orator import (jsonify)
from runner import db
import datetime
import json
import math as m
mod = Blueprint('payments',__name__)

@mod.route('/payment/<id>/<int:status>', methods=['POST'])
def pay_for_treatments(id,status):
    userid = id,
    pay = status
    summary = request.get_json()['summary']
    sdata =  json.dumps(summary)
    catId = summary[0]['disease']['category_id']
    tdump = json.dumps(summary[0]['treatment'])

    category = db.table('categories').where('id',catId).first()
    nextDate = datetime.datetime.now() + datetime.timedelta(days=category.nextTime)
    print category.nextTime
    print nextDate
    x= db.table('user_orders').insert({
        'user_id':userid,
        'purchased':pay,
        'summary':sdata,
        'nextDate':nextDate
        })
    
    return jsonify({
        'message':'success'
        }),200





@mod.route('/summary/<int:id>',methods=['GET'])
def get_user_summary(id):
    user = db.table('users')\
             .where('users.id',id)\
             .select('users.id as Id','users.email as email','users.name as name','users.weight as Weight')\
             .first().serialize()
    summary = db.table('user_orders')\
            .where('user_id',id).get().map(lambda x:{
                'nextDate':x['nextDate'],
                'purchased':x['purchased'],
                'created_at':x['created_at'],
                'id':x['id'],
                'summary':[{
                    'blood_test':y['blood_test'],
                    'dignosis':y['dignosis'],
                    'treatment':y['treatment'],
                    'disease':y['disease']
                    } 
                    for y in json.loads(x['summary'])]
                })

    attachment = db.table('user_attachments')\
                   .where('user_id',id)\
                   .select('id','attachment')\
                   .get().serialize()

    user['reports']=  [{
            'attachment':b['attachment'],
            'history':a
             }
            for a,b in zip(summary,attachment)
        ]

    return jsonify({
        'summary':user
        })

@mod.route('/recent/<int:id>')
def get_recent_diagnosis(id):
    sql = "SELECT * FROM user_orders WHERE user_id = {} order by id desc limit 1"
    y = db.select(sql.format(id))
    return jsonify(y),200


@mod.route('/payment/edit/<int:id>',methods=['POST'])
def update_payment(id):
    db.table('user_orders').where('id',id).update({'purchased':1})
    return jsonify({
        'message':'success'
        }),200


@mod.route('/check/next/<int:id>')
def check_for_retest(id):
    nextTime = db.table('user_orders').latest().first()
    today = datetime.datetime.now()
    ntt =  nextTime['nextDate']
    delta = today- ntt
    print (delta.days)
    return jsonify({'time':today})


@mod.route('/getPlotData/<int:id>')
def get_plot_data(id):
    summary = db.table('user_orders')\
                .where('user_id',id)\
                .order_by('id','desc')\
                .limit(1)\
                .get()\
                .pluck('summary')\
                .map(lambda u:json.loads(u))\
                .collapse()\
                .pluck('blood_test')\
                .collapse()\
                .unique('name')

    weight = summary.filter(lambda z: z['name']=='weight')
    bloods = summary.filter(lambda z: not z['name']== 'weight')
    labels = bloods.pluck('name')
    values = bloods.pluck('number')
    return jsonify({'plot':{
        'yAxis':weight.serialize(),
        'xAxis':{
            'labels':labels.serialize(),
            'values':values.serialize()
            }
        }})
