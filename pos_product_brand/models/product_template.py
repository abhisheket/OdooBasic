# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    brand = fields.Many2one('product.brand', string='Brand',
                            help='Product Brand', ondelete='restrict')


class ProductBrand(models.Model):
    _name = 'product.brand'

    name = fields.Char(string='Brand')
