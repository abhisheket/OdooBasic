# -*- coding: utf-8 -*-

from odoo import fields, models


class HotelReport(models.Model):
    _name = "hotel.report"
    _description = "Hotel Management Report"

    # from_date = fields.Date(string='Date from')
    # to_date = fields.Date(string='Date to')
    # guest_name_id = fields.Many2one('res.partner', string='Guest name')
    # report_line_ids = fields.Many2many('hotel.accommodation',
    #                                    string='Report Lines')
    # number = fields.Integer(string='SL.NO')
    # guest_id = fields.Many2one('res.partner', ondelete='restrict',
    #                            string='Guest')
    # check_in = fields.Datetime(string='Check - In')
    # check_out = fields.Datetime(string='Check - Out')
    # state = fields.Char(string='State')
