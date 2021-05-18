# -*- coding: utf-8 -*-
from odoo import api, exceptions, fields, models


class HotelReportFilter(models.TransientModel):
    _name = "hotel.report.filter"
    _description = "Hotel Management Report Filter"

    from_date = fields.Date(string='Date from', required=True)
    to_date = fields.Date(string='Date to', required=True)
    guest_id = fields.Many2one('res.partner', string='Guest name',
                                    required=True)

    @api.onchange('from_date', 'to_date')
    def _onchange_date(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise exceptions.ValidationError("Invalid date range")

    def action_print_report(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'guest_id': self.guest_id.id,
            'guest_name': self.guest_id.name,
        }
        # docids = self.env['sale.order'].search([]).ids
        return self.env.ref(
            'hotel_management.hotel_management_action_report').report_action(
            None, data=data)
