# -*- coding: utf-8 -*-
# from odoo import http


# class Manage(http.Controller):
#     @http.route('/manage/manage', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/manage/manage/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('manage.listing', {
#             'root': '/manage/manage',
#             'objects': http.request.env['manage.manage'].search([]),
#         })

#     @http.route('/manage/manage/objects/<model("manage.manage"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('manage.object', {
#             'object': obj
#         })
