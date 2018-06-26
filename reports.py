from flask import (jsonify,Blueprint,render_template)
from runner import (db)
import json
import mimerender

mimerender.register_mime('pdf', ('application/pdf',))
mimerender = mimerender.FlaskMimeRender(global_charset='UTF-8')

mod = Blueprint(__name__,'reports',template_folder='templates')


def render_pdf(html):
    from xhtml2pdf import pisa
    from cStringIO import StringIO
    pdf = StringIO()
    pisa.CreatePDF(StringIO(html.encode('utf-8')), pdf)
    resp = pdf.getvalue()
    pdf.close()
    return resp



@mod.route('/reports/users/<int:id>')
@mimerender(default='pdf', pdf=render_pdf, override_input_key='format')
def make_reports_for_user(id):
    user = db.table('users')\
             .where('users.id',id)\
             .select('users.id as Id','users.email as email','users.name as name','users.weight as Weight','users.mobile as contact')\
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

    report =  [{
            'attachment':b['attachment'],
            'history':a
             }
            for a,b in zip(summary,attachment)
        ]

    html =render_template(
        'report.html',
        user=user,
        report=report,
        js0n = json,
        enum = zip
        )


    return { 'html': html } 


