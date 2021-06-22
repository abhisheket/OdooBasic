# -*- coding: utf-8 -*-

from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class CustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'leave_count' in counters:
            employee_id = request.env['hr.employee'].sudo().search(
                [('user_id.id', '=', request.uid)]).id or request.env[
                'hr.employee'].sudo().search(
                [('address_home_id', '=', request.env[
                    'res.users'].sudo().search(
                    [('id', '=', request.uid)]).partner_id.id)]).id
            values['leave_count'] = request.env['hr.leave'].sudo().search_count(
                    [('employee_id', '=', employee_id)])
        return values
