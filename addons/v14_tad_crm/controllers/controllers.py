# -*- coding: utf-8 -*-
# from odoo import http


# class V14TadCrm(http.Controller):
#     @http.route('/v14_tad_crm/v14_tad_crm/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/v14_tad_crm/v14_tad_crm/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('v14_tad_crm.listing', {
#             'root': '/v14_tad_crm/v14_tad_crm',
#             'objects': http.request.env['v14_tad_crm.v14_tad_crm'].search([]),
#         })

#     @http.route('/v14_tad_crm/v14_tad_crm/objects/<model("v14_tad_crm.v14_tad_crm"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('v14_tad_crm.object', {
#             'object': obj
#         })
