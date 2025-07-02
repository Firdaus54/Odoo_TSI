# -*- coding: utf-8 -*-
# from odoo import http


# class ContactAssociate(http.Controller):
#     @http.route('/contact_associate/contact_associate', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contact_associate/contact_associate/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('contact_associate.listing', {
#             'root': '/contact_associate/contact_associate',
#             'objects': http.request.env['contact_associate.contact_associate'].search([]),
#         })

#     @http.route('/contact_associate/contact_associate/objects/<model("contact_associate.contact_associate"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contact_associate.object', {
#             'object': obj
#         })
