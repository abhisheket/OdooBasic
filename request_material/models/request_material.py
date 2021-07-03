# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MaterialRequest(models.Model):
    _name = "material.request"
    _description = "Material Request"
    _order = "name desc"

    name = fields.Char(string="Number", required=True, copy=False,
                       readonly=True, default=lambda self: 'New')
    user_id = fields.Many2one('res.users', string='Requester',
                              default=lambda self: self.env.uid, readonly=True)
    request_date = fields.Datetime(string="Date", readonly=True, copy=False,
                                   help="Date of Request")
    manager_id = fields.Many2one(
        'res.users', string='Manager', readonly=True, store=True,
        compute='_compute_manager_id', help="Requisition Department Manager",
        default=lambda self: (self.env['res.groups'].search(
                [('name', 'ilike',
                  'Requisition Department Manager')]).users).ids[0])
    head_id = fields.Many2one(
        'res.users', string='Head', compute='_compute_head_id', readonly=True,
        default=lambda self: (self.env['res.groups'].search(
                [('name', 'ilike', 'Requisition Head')]).users).ids[0],
        store=True, help="Requisition Head")
    material_list_ids = fields.One2many('material.list', 'material_list_id',
                                        string='Material list')
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('cancel', 'Cancelled'),
                   ('confirm', 'To Approve'), ('reject', 'Rejected'),
                   ('validate1', 'Second Approval'), ('validate', 'Approved')],
        required=True, default='draft')

    @api.model
    def create(self, values):
        if values.get('name', 'New') == 'New':
            values['name'] = self.env['ir.sequence'].next_by_code(
                'material.request.sequence') or 'New'
        result = super(MaterialRequest, self).create(values)
        return result

    @api.depends('user_id')
    def action_submit(self):
        self.state = "confirm"
        self.request_date = fields.Datetime.now()

    def action_reset_to_draft(self):
        self.state = "draft"
        self.request_date = False

    def action_cancel(self):
        self.state = "cancel"

    def action_approve(self):
        self.state = "validate1"

    def action_validate(self):
        # self.state = "validate"
        print("validating")
        print(self.env['stock.picking.type'].search([('name', 'ilike', 'Internal Transfer')]).name)
        for record in self.material_list_ids:
            if record.acquire_method == 'int':
                print("creating int")

    def action_reject(self):
        self.state = "reject"


class MaterialList(models.Model):
    _name = "material.list"
    _description = "List of requisition materials"
    _rec_name = "material_list_id"

    material_list_id = fields.Many2one('material.request', string='Number')
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain=[('purchase_ok', '=', True), ('type', '=', 'product')])
    product_qty = fields.Float(string='Quantity', required=True)
    acquire_method = fields.Selection(
        selection=[('po', 'Purchase Order'), ('int', 'Internal Transfer')],
        string='Acquire Method', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company)
    source_id = fields.Many2one(
        'stock.location', string='Source', check_company=True,
        domain="[('usage','=','internal'), '|', ('company_id', '=', False),"
               "('company_id', '=', company_id)]", help="Source Location")
    destination_id = fields.Many2one(
        'stock.location', string='Destination', check_company=True,
        domain="[('usage','=','internal'), '|', ('company_id', '=', False),"
               "('company_id', '=', company_id)]", help="Destination Location")

    @api.onchange('product_id', 'acquire_method')
    def _onchange_product_id(self):
        if self.product_id and self.acquire_method == 'int':
            stock_quant = self.env['stock.quant'].search(
                [('product_id', '=', self.product_id.id)])
            source_location_domain = []
            for record in stock_quant:
                if record.location_id.usage == 'internal' and \
                        (record.location_id.company_id.id == self.company_id.id
                         or not record.location_id.company_id.id):
                    source_location_domain.append(record.location_id.id)
            return {'domain': {
                'source_id': [('id', 'in', source_location_domain)]}}
