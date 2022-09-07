# -*- coding: utf-8 -*-
# from odoo import http


# class Nalinkdanea(http.Controller):
#     @http.route('/na_linkdanea/na_linkdanea', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/na_linkdanea/na_linkdanea/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('na_linkdanea.listing', {
#             'root': '/na_linkdanea/na_linkdanea',
#             'objects': http.request.env['na_linkdanea.na_linkdanea'].search([]),
#         })

#     @http.route('/na_linkdanea/na_linkdanea/objects/<model("na_linkdanea.na_linkdanea"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('na_linkdanea.object', {
#             'object': obj
#         })
