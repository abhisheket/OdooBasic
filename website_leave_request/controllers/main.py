# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class LeaveRequest(http.Controller):

    @http.route('/leave_requests', type='http', auth='user', website=True)
    def load_leave_request(self):
        leave_records = request.env['hr.leave'].search(
            [('user_id.id', '=', request.uid)])
        values = {
            'leave_records': leave_records,
        }
        return request.render("website_leave_request.leave_requests", values)

    @http.route('/leave_requests/create_new_request', type='http', auth='user',
                website=True)
    def new_leave_request(self):
        leave_types = request.env['hr.leave.type'].search([])
            # ['&', ('virtual_remaining_leaves', '>', 0), '|',
            #  ('allocation_type', 'in', ['fixed_allocation', 'no']), '&',
            #  ('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')])
        leave_data = request.env['hr.leave'].search([])
        hour_list = list(range(1, 12))
        user = request.uid
        value = {
            'user': user,
            'leave_types': leave_types,
            'leave_data': leave_data,
            'hour_list': hour_list,
        }
        return request.render("website_leave_request.new_leave_request", value)
