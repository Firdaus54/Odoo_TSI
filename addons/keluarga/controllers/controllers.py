# -*- coding: utf-8 -*-
# from odoo import http


# class Keluarga(http.Controller):
#     @http.route('/keluarga/keluarga/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/keluarga/keluarga/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('keluarga.listing', {
#             'root': '/keluarga/keluarga',
#             'objects': http.request.env['keluarga.keluarga'].search([]),
#         })

#     @http.route('/keluarga/keluarga/objects/<model("keluarga.keluarga"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('keluarga.object', {
#             'object': obj
#         })
