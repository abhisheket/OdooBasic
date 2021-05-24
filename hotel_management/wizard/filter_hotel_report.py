# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HotelReportFilter(models.TransientModel):
    _name = "hotel.report.filter"
    _description = "Hotel Management Report Filter"

    from_date = fields.Date(string='Date from')
    to_date = fields.Date(string='Date to')
    guest_id = fields.Many2one('res.partner', string='Guest name')

    @api.onchange('from_date', 'to_date')
    def _onchange_date(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValidationError("Invalid date range")

    def action_print_report_pdf(self):
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'guest_id': self.guest_id.id,
            'guest_name': self.guest_id.name,
        }
        return self.env.ref(
            'hotel_management.hotel_action_report_pdf').report_action(
            None, data=data)

    def action_print_report_xlsx(self):
        return self.env.ref(
            'hotel_management.hotel_action_report_xlsx').report_action(self)
