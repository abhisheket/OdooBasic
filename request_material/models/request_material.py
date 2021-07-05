# -*- coding: utf-8 -*-

from odoo import api, fields, models


class MaterialRequest(models.Model):
    _name = "material.request"
    _description = "Material Request"
    _order = "name desc"

    name = fields.Char(string="Number", required=True, copy=False,
                       readonly=True, default=lambda self: 'New')
    user_id = fields.Many2one(
        'res.users', string='Requester',  default=lambda self: self.env.uid,
        ondelete='restrict', readonly=True)
    operation_type = fields.Selection(
        selection=[('purchase', 'Purchase Order'),
                   ('internal', 'Internal Transfer')], string='Operation Type',
        required=True)
    request_date = fields.Datetime(string="Date", readonly=True, copy=False,
                                   help="Date of Request")
    manager_id = fields.Many2one(
        'res.users', string='Manager', ondelete='restrict', required=True,
        domain=lambda self: [('id', 'in', (self.env['res.groups'].search(
                [('name', 'ilike',
                  'Requisition Department Manager')]).users).ids)],
        help="Requisition Department Manager")
    head_id = fields.Many2one(
        'res.users', string='Head', ondelete='restrict', required=True,
        domain=lambda self: [('id', 'in', (self.env['res.groups'].search(
                [('name', 'ilike', 'Requisition Head')]).users).ids)],
        help="Requisition Head")
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
        self.state = "validate"
        if self.operation_type == 'internal':
            for record in self.material_list_ids:
                move_line = {
                    'name': record.product_id.display_name,
                    'product_id': record.product_id.id,
                    'product_uom_qty': record.product_qty,
                    'product_uom': record.uom_id.id,
                }
                self.env['stock.picking'].create({
                    'picking_type_id': self.env['stock.picking.type'].search(
                        [('name', 'ilike', 'Internal Transfer')]).id,
                    'location_id': record.location_id.id,
                    'location_dest_id': record.location_dest_id.id,
                    'origin': self.name,
                    'scheduled_date': fields.Datetime.now(),
                    'move_type': 'one',
                    'move_ids_without_package': [(0, 0, move_line)],
                })
        else:
            vendors = set()
            for record in self.material_list_ids:
                vendors.update(record.partner_ids.ids)
            for vendor in vendors:
                order_lines = []
                for record in self.material_list_ids:
                    if vendor in record.partner_ids.ids:
                        supplierinfo = \
                            record.product_id.product_tmpl_id.seller_ids.ids
                        min_qty_list = []
                        for line in self.env[
                                  'product.supplierinfo'].search(
                            [('id', 'in', supplierinfo),
                             ('name.id', '=', vendor)]):
                            min_qty_list.append(line.min_qty)
                        min_qty_list.sort()
                        min_qty = 0
                        for quantity in min_qty_list:
                            if record.product_qty < quantity:
                                break
                            elif record.product_qty >= quantity:
                                min_qty = quantity
                        price = self.env[
                                  'product.supplierinfo'].search(
                            [('id', 'in', supplierinfo),
                             ('name.id', '=', vendor),
                             ('min_qty', '=', min_qty)]).price or \
                                record.product_id.standard_price
                        order_line = (0, 0, {
                            'name': record.product_id.display_name,
                            'product_id': record.product_id.id,
                            'product_qty': record.product_qty,
                            'product_uom': record.uom_id.id,
                            'price_unit': price,
                        })
                        order_lines.append(order_line)
                self.env['purchase.order'].create({
                    'partner_id': vendor,
                    'picking_type_id': self.env['stock.picking.type'].search(
                        [('name', 'ilike', 'Receipts')]).id,
                    'origin': self.name,
                    'date_order': fields.Datetime.now(),
                    'order_line': order_lines,
                })

    def action_reject(self):
        self.state = "reject"


class MaterialList(models.Model):
    _name = "material.list"
    _description = "List of requisition materials"
    _rec_name = "material_list_id"

    material_list_id = fields.Many2one('material.request', string='Number',
                                       ondelete='restrict')
    product_id = fields.Many2one(
        'product.product', string='Product', ondelete='restrict', required=True,
        domain=[('purchase_ok', '=', True), ('type', '=', 'product'),
                ('seller_ids', '!=', False)])
    product_qty = fields.Float(string='Quantity', required=True)
    uom_id = fields.Many2one(
        'uom.uom', 'UoM', required=True, related="product_id.uom_id",
        store=True, domain="[('category_id', '=', product_uom_category_id)]",
        help='Unit of Measure')
    product_uom_category_id = fields.Many2one(related='uom_id.category_id')
    company_id = fields.Many2one(
        'res.company', string='Company', required=True, ondelete='restrict',
        default=lambda self: self.env.company)
    partner_ids = fields.Many2many('res.partner', string='Vendors')
    location_id = fields.Many2one(
        'stock.location', string='Source', check_company=True,
        ondelete='restrict', help="Source Location",
        domain="[('usage','=','internal'), '|', ('company_id', '=', False),"
               "('company_id', '=', company_id)]")
    location_dest_id = fields.Many2one(
        'stock.location', string='Destination', check_company=True,
        ondelete='restrict', help="Destination Location",
        domain="[('usage','=','internal'), '|', ('company_id', '=', False),"
               "('company_id', '=', company_id)]")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            partners = []
            for record in self.product_id.product_tmpl_id.seller_ids:
                partners.append(record.name.id)
            self.partner_ids = partners
            source_location_domain = []
            for record in self.env['stock.quant'].search(
                    [('product_id', '=', self.product_id.id)]):
                if record.location_id.usage == 'internal' and \
                        (record.location_id.company_id.id == self.company_id.id
                         or not record.location_id.company_id.id):
                    source_location_domain.append(record.location_id.id)
            return {'domain': {
                'location_id': [('id', 'in', source_location_domain)]}}
