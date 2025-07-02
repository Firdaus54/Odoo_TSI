from odoo import http
from odoo.http import request

class WebsiteForm(http.Controller):
    @http.route(['/ispo'], type='http', auth="public", website=True)
    def appointment(self):
        iso_standard = request.env['tsi.iso.standard'].search([('standard','=','ispo')])
        return request.render("v15_tsi.ispo_form",{
                'iso_standard': iso_standard,
                'iso_doctype': 'ispo',

            })

       
    @http.route(['/ispo/submit'], type='http', auth="public", website=True)
    def submit(self, **post):
        std_iso = request.httprequest.form.getlist('iso_standardx')
        partner = request.env['res.partner'].search([('name','=', post.get('company_name'))])

        if not partner:
            partner = request.env['res.partner'].sudo().create({
                    'name': post.get('company_name'),
                    'company_type': 'company'
                    })

        iso_form = request.env['tsi.iso'].sudo().create({
            'doctype'           : 'ispo',
            'company_name'      : post.get('company_name'),
            'office_address'    : post.get('office_address'),
            'invoicing_address' : post.get('invoicing_address'),
            'contact_person'    : post.get('contact_person'),

            'jabatan'           : post.get('jabatan'),
            'telepon'           : post.get('telepon'),
            'fax'               : post.get('fax'),
            'email'             : post.get('email'),
            'website'           : post.get('website'),
            'cellular'          : post.get('cellular'),

            'customer'          : partner.id,

            'scope'             : post.get('scope'),
            'boundaries'        : post.get('boundaries'),
            'cause'             : post.get('cause'),
            'isms_doc'          : post.get('isms_doc'),            

            'certification'     : post.get('certification'),

            'iso_standard_ids'  : [(6, 0, [x for x in std_iso])],

            'legal_lokasi'      : post.get('legal_lokasi'),
            'legal_iup'         : post.get('legal_iup'),
            'legal_spup'        : post.get('legal_spup'),
            'legal_itubp'       : post.get('legal_itubp'),
            'legal_prinsip'     : post.get('legal_prinsip'),
            'legal_menteri'     : post.get('legal_menteri'),
            'legal_bkpm'        : post.get('legal_bkpm'),
            'perolehan_a'       : post.get('perolehan_a'),
            'perolehan_b'       : post.get('perolehan_b'),
            'perolehan_c'       : post.get('perolehan_c'),
            'perolehan_d'       : post.get('perolehan_d'),
            'legal_hgu'         : post.get('legal_hgu'),
            'legal_amdal'       : post.get('legal_amdal'),

        })

        return request.render("v15_tsi.ispo_form_success")
