# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class LeaveRequest(http.Controller):

    @http.route('/leave_requests', type='http', auth='user', website=True)
    def create_leave_request(self):
        values = {
            'status' : "Request status"
        }
        return request.render("website_leave_request.leave_requests", values)
