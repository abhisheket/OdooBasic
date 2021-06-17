# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class LeaveRequest(http.Controller):

    @http.route('/leave_requests', type='http', auth='user', website=True)
    def load_leave_request(self):
        leave_records = request.env['hr.leave'].sudo().search(
            [('user_id.id', '=', request.uid)])
        values = {
            'leave_records': leave_records,
        }
        return request.render("website_leave_request.leave_requests", values)

    @http.route('/leave_requests/new_request', type='http', auth='user',
                website=True)
    def new_leave_request(self):
        leave_types = request.env['hr.leave.type'].sudo().search(
            ['&', ('virtual_remaining_leaves', '>', 0), '|',
             ('allocation_type', 'in', ['fixed_allocation', 'no']), '&',
             ('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')])
        leave_data = request.env['hr.leave'].sudo().search([])
        hour_list = list(range(1, 12))
        user = request.uid
        value = {
            'user': user,
            'leave_types': leave_types,
            'leave_data': leave_data,
            'hour_list': hour_list,
        }
        return request.render("website_leave_request.new_leave_request", value)

    @http.route('/leave_requests/create_request', type='http', auth='user',
                website=True)
    def create_leave_request(self, **kwargs):
        print(kwargs)
        # # last_record = request.env['hr.leave'].search(
        # #     [], limit=1, order='id desc')
        # # print(last_record.id)
        # add_values = {
        #     'department_id': request.uid,
        # }
        # print(add_values)
        # kwargs.update(add_values)
        # print(kwargs)
        # request.env['hr.leave'].sudo().create(kwargs)

        employee = request.env['hr.employee'].sudo().search(
            [('user_id.id', '=', request.uid)])
        employee_id = employee.id
        if employee:
            values = {
                'holiday_status_id': 2,
                'request_date_from': '2018-06-28',
                'request_date_to': '2018-06-29',
                'number_of_days': 2.00,
                'name': 'Repair laptop.',
                # 'department_id': department_id,
                'employee_id': employee_id,
                # 'company_id': company_id,
            }
        print(values)
        # request.env['hr.leave'].sudo().create(values)
        return request.redirect('/leave_requests/create_request')

    @http.route(
        ['/leave_requests/delete_request/<model("hr.leave"):leave_record>'],
        type='http', auth='user', website=True)
    def delete_leave_request(self, leave_record):
        request.env['hr.leave'].sudo().search(
            [('id', '=', leave_record.id)]).unlink()
        return request.redirect('/leave_requests')
