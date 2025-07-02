# -*- coding: utf-8 -*-
from odoo import http, _, exceptions
from odoo.http import request
import json
import  werkzeug.wrappers
import base64
import io
from PIL import Image
from base64 import b64encode, b64decode
import xmlrpc, xmlrpc.client
import logging
_logger = logging.getLogger(__name__)
   

class CultureAssessment(http.Controller):
    @http.route('/get_id', csrf=False, type='json', auth='public', methods=['POST'], cors='*')   
    def get_id(self,**params):
        login = params.get('login')
        id = http.request.env['res.users'].sudo().search([('login', '=', login)])  
        if not id:
            return http.Response(json.dumps({'error': 'Email not found'}), status=404, headers={'Content-Type': 'application/json'})
        else:
            return {
                'result': 'success',
                'id': id.id,
                'name': id.name,
            }
    
    @http.route('/get_id', csrf=False, type='json', auth='public', methods=['OPTIONS'], cors="*")
    def options_id(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
        )
    
    @http.route('/get_user_forgot/<int:user_id>',crsf=False,cors='*', type='http', auth='public', methods=['GET'])
    def get_user_forgot(self,user_id, **kwargs):
        user = request.env['res.users'].sudo().search([('id','=',user_id)])
        user_data = []
        for user in user:
            user_data.append({
                'email': user.login,
                'name': user.name,
            })

        return request.make_response(json.dumps(user_data), headers={'Content-Type': 'application/json'})
    
    @http.route('/get_user_forgot/<int:user_id>', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_user_forgot(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )

    @http.route('/web/change_password/<int:user_id>', csrf=False, type='json', auth='public', methods=['POST'], cors='*')   
    def change_password(self,user_id,**params):
        new_password = params.get('new_password')

        user = http.request.env['res.users'].sudo().search([('id', '=', user_id)])
        if not user:
            return {
                'error': 'User not found'
            }
        else:
            user.write({'password': new_password})
            return {
                'result': 'success',
            }

    @http.route('/web/change_password/<int:user_id>', csrf=False, type='json', auth='public', methods=['OPTIONS'], cors="*")
    def options_change_password(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
        )

    @http.route(['/api/feedback_app'], csrf=False, type='json', auth='public', methods=['POST'], cors='*')        
    def api_feedback_app(self,**params):
        emoji = params.get('emoji')
        feedback_app = params.get('feedback')

        vals = {
            'emoji': emoji,
            'feedback': feedback_app,
        }
        
        post = http.request.env['assesment.conf'].sudo().create(vals)
        header = request.httprequest.headers
        data = {
            'message': 'success',
        }
        return data

    @http.route('/api/feedback_app', csrf=False, type='json', auth='public', methods=['OPTIONS'], cors="*")
    def options_api_feedback_app(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
        )

    @http.route(['/api/post'], csrf=False, type='json', auth='public', methods=['POST'], cors='*')        
    def api_post(self, **params):
        employee = params.get("employee")
        event = params.get("event")
        modul = params.get("modul")
        penilai = params.get("penilai")
        entitas = params.get("entitas")

        assessment_line = []
        for line in params.get('assessment_line'):
            assessment_line.append((0, 0, {
                'core_values_id': line.get('core_values_id'),
                'name': line.get('name'),
                'star_rating_id': line.get('star_rating_id'),  
                'feedback': line.get('feedback'),
                'total_score': line.get('total_score'),
                'state': "submit",
                'is_done':True,
                'employee_id': employee,
            }))
        vals = {
            'employee_id': employee,
            'event_id': event,
            'modul_culture_id': modul,
            'assessment_line': assessment_line,
            'penilai_id': penilai,
            'entitas_id': entitas,
            'state': "submit"
        }
        
        post = http.request.env['assessment.tools'].sudo().create(vals)

        header = request.httprequest.headers
        data = {
            'message': 'success',
            'employee_id': employee,
            'event_id': event,
            'modul_culture_id': modul
        }
        return data
    
    @http.route('/api/post/', csrf=False, type='json', auth='public', methods=['OPTIONS'], cors="*")
    def options_api_post(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
        )

    @http.route('/get_form',crsf=False,cors='*', type='http', auth='public', methods=['GET'])
    def get_form(self, **kwargs):
        # form = request.env['assessment.tools'].sudo().search([])
        # form_data = []
        # for form in form:
        #     form_data.append({
        #         'name': form.employee_id.name,
        #         'id': form.employee_id.id,
        #         'nrp': form.nrp,
        #         'entitas': form.entitas_id.name,
        #         'entitas_id': form.entitas_id.id,
        #         'event': form.event_id.name,
        #         'event_id': form.event_id.id,
        #         'modul': form.modul_culture_id.name,
        #         'modul_id': form.modul_culture_id.id,
        #     })

        employee=request.env['hr.employee'].sudo().search([])
        employee_data=[]
        for employee in employee:
            employee_data.append({
                'name': employee.name,
                'id': employee.id,
                'nrp': employee.nrp,
                'entitas': employee.entitas_id.name,
                'entitas_id': employee.entitas_id.id
            })

        event=request.env['event.assessment'].sudo().search([])  
        event_data=[]
        for event in event:
            event_data.append({
                'name': event.name,
                'id': event.id,
            }) 
        module=request.env['culture.module'].sudo().search([])  
        module_data=[]
        for module in module:
            module_data.append({
                'name': module.name,
                'id': module.id,
            }) 

            data = {
                # 'form':form_data,
                'employee': employee_data,
                'event': event_data,
                'module': module_data
            }

        return request.make_response(json.dumps(data), headers={'Content-Type': 'application/json'})
    
    @http.route('/get_form', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_get_form(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )

    @http.route('/session/authenticate',csrf=False, type='json', auth="none",methods=['POST'], cors='*')
    def authenticate(self, db, login, password, base_location=None):
        user = request.env['res.users'].sudo().search([('login', '=', login), ('password', '=', password)], limit=1)
        id = user.id
        employee = request.env['hr.employee'].sudo().search([('user_id','=',id)])

        if user:
            request.session.authenticate(db, login, password)
            return {
                'result': 'success',
                'session_info': request.env['ir.http'].session_info(),
                'user_id': user.id,
                'employee_id': employee.id,
                'user_name': user.name,
            }
        else:
            user = request.env['res.users'].sudo().search([('login', '=', login)], limit=1)
            if user:
                return {
                    'result': 'error password',
                    'error_message': 'Invalid password',
                }
            else:
                return {
                    'result': 'error not found',
                    'error_message': 'Email tidak terdaftar.',
                }

    @http.route('/session/authenticate', csrf=False, type='json', auth='none', methods=['OPTIONS'], cors="*")
    def options_post_authenticate(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            # status=200,
            content_type='application/json',
            response={},
            headers=headers
            )    
        
    @http.route('/get_data_user/<int:user_id>', crsf=False, cors='*', type='http', auth='public', methods=['GET'])
    def get_data_user(self, user_id, **kwargs):
        _logger.info(f"Received request for user_id: {user_id}")

        # Mendapatkan data employee
        employees = request.env['hr.employee'].sudo().search([('user_id', '=', user_id)])
        employee_data = []
        for employee in employees:
            # Mendapatkan data foto profil dari res.users
            user = request.env['res.users'].sudo().search([('id', '=', employee.user_id.id)])
            image_binary = user.image_1920 if user.image_1920 else None

            employee_data.append({
                'name': employee.name,
                'nrp': employee.nrp,
                'position': employee.position,
                'work_email': employee.work_email,
                'location': employee.work_location,
                'work_phone': employee.work_phone,
                'entitas': employee.entitas_id.name,
                'profile_image_binary': image_binary.decode('utf-8') if image_binary else None
            })

        # Mendapatkan data rating berdasarkan user_id dan state
        rating = request.env['assessment.tools'].sudo().search([
            ('employee_id.user_id', '=', user_id),
            ('state', '=', 'submit')
        ])

        total_score_rating = sum(assessment_tool.average_score for assessment_tool in rating)
        average_score_rating = total_score_rating / len(rating) if rating else 0

        response_data = {'employee_data': employee_data,
                        'average_score': average_score_rating}

        return request.make_response(json.dumps(response_data), headers={'Content-Type': 'application/json'})

    @http.route('/get_data_user/<int:user_id>', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_get_data_user(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )
    
    @http.route('/update_profile_image/<int:user_id>', csrf=False, cors='*', type='http', auth='public', methods=['POST'])
    def update_profile_image(self, user_id, **post):
        _logger.info(f"Received request to update profile image for user_id: {user_id}")

        try:
            user = request.env['res.users'].sudo().search([('id', '=', user_id)])
            if not user:
                response = json.dumps({'error': 'User not found'})
                return werkzeug.wrappers.Response(response, status=404, content_type='application/json')

            if 'profile_image' in post and post['profile_image'].filename:
                profile_image_data = post['profile_image'].read()
                user.write({'image_1920': base64.b64encode(profile_image_data)})

                response = json.dumps({'success': 'Profile image updated successfully'})
                return werkzeug.wrappers.Response(response, status=200, content_type='application/json')
            else:
                response = json.dumps({'error': 'Profile image not provided'})
                return werkzeug.wrappers.Response(response, status=400, content_type='application/json')
        except Exception as e:
            _logger.error(f"Error processing profile image update: {e}")
            response = json.dumps({'error': 'Internal server error'})
            return werkzeug.wrappers.Response(response, status=500, content_type='application/json')

    @http.route('/update_profile_image/<int:user_id>', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_update_profile_image(self, id=None,**kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST',
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
        )
    
    @http.route('/get_assessment/<int:user_id>',crsf=False,cors='*', type='http', auth='public', methods=['GET'])
    def get_assessment(self,user_id, **kwargs):
        assessment = request.env['assessment.tools'].sudo().search([('penilai_id.user_id', '=', user_id)])
        assessment_data = []
        for assessment in assessment:
            assessment_data.append({
                'assessment': assessment.employee_id.name,
                'name': assessment.name,
                'nrp': assessment.nrp,
                'score': assessment.average_score,  
            })

        return request.make_response(json.dumps(assessment_data), headers={'Content-Type': 'application/json'})

    @http.route('/get_assessment/<int:user_id>', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_get_assessment(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )
    
    @http.route('/get_assessor/<int:user_id>',crsf=False,cors='*', type='http', auth='public', methods=['GET'])
    def get_assessor(self,user_id, **kwargs):
        assessor = request.env['assessment.line'].sudo().search([('employee_id.user_id', '=', user_id),('state','=','submit')])
        assessor_data = []
        for assessor in assessor:
            assessor_data.append({
                'date':assessor.date.strftime("%Y/%m/%d"),
                'score': assessor.total_score,  
                'value': assessor.core_values_id.name,
                'feedback': assessor.feedback
            })

        return request.make_response(json.dumps(assessor_data), headers={'Content-Type': 'application/json'})

    @http.route('/get_assessor/<int:user_id>', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_get_assessor(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )
    
    @http.route('/feedback/<int:user_id>',crsf=False,cors='*', type='http', auth='public', methods=['GET'])
    def get_feedback(self,user_id, **kwargs):
        feedback = request.env['assessment.line'].sudo().search([('employee_id.user_id', '=', user_id),('state','=','submit'),('feedback', '!=', False)])
        feedback_data = []
        for feedback in feedback:
            feedback_data.append({
                'culture': feedback.core_values_id.name,
                'date': feedback.date.strftime("%Y/%m/%d"),
                'score': feedback.total_score,
                'feedback': feedback.feedback
            })

        return request.make_response(json.dumps(feedback_data), headers={'Content-Type': 'application/json'})

    @http.route('/feedback/<int:user_id>', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_get_feedback(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )

    @http.route('/get_personal/<int:user_id>',crsf=False,cors='*', type='http', auth='public', methods=['GET'])
    def get_personal_score(self, user_id, **kwargs):
        Pe = request.env['assessment.line'].sudo().search([
            ('employee_id.user_id', '=', user_id),
            ('state', '=', 'submit'),
            ('core_values_id', '=', 2)  
        ])

        total_score_Pe = sum(assessment_line.total_score for assessment_line in Pe)
        average_score_Pe = total_score_Pe / len(Pe) if Pe else 0

        Du = request.env['assessment.line'].sudo().search([
            ('employee_id.user_id', '=', user_id),
            ('state', '=', 'submit'),
            ('core_values_id', '=', 3)  
        ])

        total_score_Du = sum(assessment_line.total_score for assessment_line in Du)
        average_score_Du = total_score_Du / len(Du) if Du else 0

        li = request.env['assessment.line'].sudo().search([
            ('employee_id.user_id', '=', user_id),
            ('state', '=', 'submit'),
            ('core_values_id', '=', 4)  
        ])

        total_score_li = sum(assessment_line.total_score for assessment_line in li)
        average_score_li = total_score_li / len(li) if li else 0

        In = request.env['assessment.line'].sudo().search([
            ('employee_id.user_id', '=', user_id),
            ('state', '=', 'submit'),
            ('core_values_id', '=', 5)  
        ])

        total_score_In = sum(assessment_line.total_score for assessment_line in In)
        average_score_In = total_score_In / len(In) if In else 0

        Sa = request.env['assessment.line'].sudo().search([
            ('employee_id.user_id', '=', user_id),
            ('state', '=', 'submit'),
            ('core_values_id', '=', 6)  
        ])

        total_score_Sa = sum(assessment_line.total_score for assessment_line in Sa)
        average_score_Sa = total_score_Sa / len(Sa) if Sa else 0

        Ni = request.env['assessment.line'].sudo().search([
            ('employee_id.user_id', '=', user_id),
            ('state', '=', 'submit'),
            ('core_values_id', '=', 7)  
        ])

        total_score_Ni = sum(assessment_line.total_score for assessment_line in Ni)
        average_score_Ni = total_score_Ni / len(Ni) if Ni else 0

        response_data = {'average_score_Pe': average_score_Pe,
                         'average_score_Du': average_score_Du,
                         'average_score_li': average_score_li,
                         'average_score_In': average_score_In,
                         'average_score_Sa': average_score_Sa,
                         'average_score_Ni': average_score_Ni}

        return request.make_response(json.dumps(response_data), headers={'Content-Type': 'application/json'})
        
    @http.route('/get_personal/<int:user_id>', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_get_personal(self, id=None, **kw):

        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )
    
    @http.route('/get_assessment_def', crsf=False, cors='*', type='http', auth='public', methods=['GET'])
    def get_assessment_def(self, **kwargs):
        assessment1 = request.env['core.values.line'].sudo().search([('id', '=', 2)])
        assessment_data1 = []
        for x in assessment1:
         assessment_data1.append({
            'core': x.name,
            'description': x.description
         })

        assessment2 = request.env['core.values.line'].sudo().search([('id', '=', 3)])
        assessment_data2 = []
        for x in assessment2:
         assessment_data2.append({
            'core': x.name,
            'description': x.description
         })

        assessment3 = request.env['core.values.line'].sudo().search([('id', '=', 4)])
        assessment_data3 = []
        for x in assessment3:
         assessment_data3.append({
            'core': x.name,
            'description': x.description
         })

        assessment4 = request.env['core.values.line'].sudo().search([('id', '=', 5)])
        assessment_data4 = []
        for x in assessment4:
         assessment_data4.append({
            'core': x.name,
            'description': x.description
         })

        assessment5 = request.env['core.values.line'].sudo().search([('id', '=', 6)])
        assessment_data5 = []
        for x in assessment5:
         assessment_data5.append({
            'core': x.name,
            'description': x.description
         })

        assessment6 = request.env['core.values.line'].sudo().search([('id', '=', 7)])
        assessment_data6 = []
        for x in assessment6:
         assessment_data6.append({
            'core': x.name,
            'description': x.description
         })

        questsatu = request.env['star.rating.line'].sudo().search([('id', '=', 1)])
        ass_data1 = questsatu.mapped('star_rating_line.description')

        questdua = request.env['star.rating.line'].sudo().search([('id', '=', 2)])
        ass_data2 = questdua.mapped('star_rating_line.description')

        questtiga = request.env['star.rating.line'].sudo().search([('id', '=', 3)])
        ass_data3 = questtiga.mapped('star_rating_line.description')

        questempat = request.env['star.rating.line'].sudo().search([('id', '=', 4)])
        ass_data4 = questempat.mapped('star_rating_line.description')

        questlima = request.env['star.rating.line'].sudo().search([('id', '=', 5)])
        ass_data5 = questlima.mapped('star_rating_line.description')

        questenam = request.env['star.rating.line'].sudo().search([('id', '=', 6)])
        ass_data6 = questenam.mapped('star_rating_line.description')

        return request.make_response(json.dumps({
            'assessment_data1': assessment_data1,
            'assessment_data2': assessment_data2,
            'assessment_data3': assessment_data3,
            'assessment_data4': assessment_data4,
            'assessment_data5': assessment_data5,
            'assessment_data6': assessment_data6,
            'ass_data1': ass_data1,
            'ass_data2': ass_data2,
            'ass_data3': ass_data3,
            'ass_data4': ass_data4,
            'ass_data5': ass_data5,
            'ass_data6': ass_data6
        }), headers={'Content-Type': 'application/json'})
    
    @http.route('/get_assessment_def', csrf=False, type='http', auth='public', methods=['OPTIONS'], cors="*")
    def options_assessment_def(self, id=None, **kw):
        headers = {
            'Access-Control-Allow-Headers': 'apikey,Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST'
        }
        return werkzeug.wrappers.Response(
            status=200,
            content_type='application/json',
            response={},
            headers=headers
            )
