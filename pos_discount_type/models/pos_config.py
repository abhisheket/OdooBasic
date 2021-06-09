# -*- coding: utf-8 -*-

from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    discount_type = fields.Selection(
        string='Discount', default='percentage', help='Discount Type',
        selection=[('percentage', 'Percentage'), ('amount', 'Amount')])
