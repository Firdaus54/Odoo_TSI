# -*- coding: utf-8 -*-
# from odoo import http


# class V15Cis(http.Controller):
#     @http.route('/v15_cis/v15_cis', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/v15_cis/v15_cis/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('v15_cis.listing', {
#             'root': '/v15_cis/v15_cis',
#             'objects': http.request.env['v15_cis.v15_cis'].search([]),
#         })

#     @http.route('/v15_cis/v15_cis/objects/<model("v15_cis.v15_cis"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('v15_cis.object', {
#             'object': obj
#         })
