from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class WebsiteForm(http.Controller):
    @http.route(['/appointment'], type='http', auth="public", website=True)
    def appointment(self):
        iso_standard    = request.env['tsi.iso.standard'].search([('standard','=','iso')])
        return request.render("v15_tsi.online_appointment_form",{
                'iso_standard': iso_standard,
                'iso_doctype': 'iso',
            })
       
    @http.route(['/appointment/submit'], type='http', auth="public", website=True)
    def submit(self, **post):

        std_iso = request.httprequest.form.getlist('iso_standardx')
        partner = request.env['res.partner'].search([('name','=', post.get('company_name'))])

        if not partner:
            partner = request.env['res.partner'].sudo().create({
                    'name': post.get('company_name'),
                    'company_type': 'company'
                    })

        # j = 0
        # service_list = []
        # while j < (int(post['number'])):
        #     item = "iso_standardx["+str(j)+"][i]"
        #     service_list.append(int(post[item]))
        #     j += 1

        iso_form = request.env['tsi.iso'].sudo().create({
            'doctype'           : 'iso',
            
            'company_name'      : post.get('company_name'),
            'office_address'    : post.get('office_address'),
            'invoicing_address' : post.get('invoicing_address'),
            'contact_person'    : post.get('contact_person'),

            'jabatan'   : post.get('jabatan'),
            'telepon'   : post.get('telepon'),
            'fax'       : post.get('fax'),
            'email'     : post.get('email'),
            'website'   : post.get('website'),
            'cellular'  : post.get('cellular'),

            'customer'  : partner.id,

            'scope'         : post.get('scope'),
            'boundaries'    : post.get('boundaries'),
            'cause'         : post.get('cause'),
            'isms_doc'      : post.get('isms_doc'),

            'head_office'       : post.get('head_office'),
            'site_office'       : post.get('site_office'),
            'off_location'      : post.get('off_location'),
            'part_time'         : post.get('part_time'),
            'subcon'            : post.get('subcon'),
            'unskilled'         : post.get('unskilled'),
            'seasonal'          : post.get('seasonal'),
            'total_emp'         : post.get('total_emp'),
            'shift_number'      : post.get('shift_number'),
            'number_site'       : post.get('number_site'),
            'outsource_proc'    : post.get('outsource_proc'),

            'last_audit'        : post.get('last_audit'),
            'last_review'       : post.get('last_review'),

            'certification'     : post.get('certification'),

            'iso_standard_ids'  : [(6, 0, [x for x in std_iso])]

        })

        return request.render("v15_tsi.online_appointment_form_success")

    @http.route(['/tsi_iso_form'], type='http', auth="public", website=True)
    def create_iso_form(self):
        return request.render("v15_tsi.tsi_iso_form")

    @http.route(['/tsi_ispo_form'], type='http', auth="public", website=True)
    def create_ispo_form(self):
        return request.render("v15_tsi.tsi_ispo_form")
