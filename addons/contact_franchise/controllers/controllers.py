# -*- coding: utf-8 -*-
# from odoo import http


# class ContactFranchise(http.Controller):
#     @http.route('/contact_franchise/contact_franchise', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contact_franchise/contact_franchise/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contact_franchise.listing', {
#             'root': '/contact_franchise/contact_franchise',
#             'objects': http.request.env['contact_franchise.contact_franchise'].search([]),
#         })

#     @http.route('/contact_franchise/contact_franchise/objects/<model("contact_franchise.contact_franchise"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contact_franchise.object', {
#             'object': obj
#         })
