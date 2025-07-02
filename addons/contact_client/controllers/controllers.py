# -*- coding: utf-8 -*-
# from odoo import http


# class ContactClient(http.Controller):
#     @http.route('/contact_client/contact_client', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contact_client/contact_client/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contact_client.listing', {
#             'root': '/contact_client/contact_client',
#             'objects': http.request.env['contact_client.contact_client'].search([]),
#         })

#     @http.route('/contact_client/contact_client/objects/<model("contact_client.contact_client"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contact_client.object', {
#             'object': obj
#         })
