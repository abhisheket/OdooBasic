# -*- coding: utf-8 -*-
from odoo import fields, models


class HotelReportFilter(models.TransientModel):
    _name = "hotel.report.filter"
    _description = "Hotel Management Report Filter"

    from_date = fields.Date(string='Date from', required=True)
    to_date = fields.Date(string='Date to', required=True)
    guest_name_id = fields.Many2one('res.partner', string='Guest name',
                                    required=True)

    def action_print_report(self):
        print("Print report")
