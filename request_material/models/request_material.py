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
    department_id = fields.Many2one('hr.department', string='Department',
                                    compute='_compute_department_id',
                                    readonly=True, store=True)
    manager_id = fields.Many2one('hr.employee', string='Manager',
                                 compute='_compute_manager_id', readonly=True,
                                 store=True, help="Department Manager")
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
    def _compute_manager_id(self):
        for record in self:
            employee_id = record.env['hr.employee'].search(
                [('user_id.id', '=', record.user_id.id)])
            if employee_id.id:
                record.manager_id = record.env['hr.department'].search(
                    [('id', '=', employee_id.department_id.id)]).manager_id

    @api.depends('user_id')
    def _compute_department_id(self):
        for record in self:
            employee_id = record.env['hr.employee'].search(
                [('user_id.id', '=', record.user_id.id)])
            if employee_id.id:
                record.department_id = record.env['hr.department'].search(
                    [('id', '=', employee_id.department_id.id)])

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
        domain=lambda self: self._domain_location_id(), help="Source Location")
    destination_id = fields.Many2one(
        'stock.location', string='Destination', check_company=True,
        domain="[('usage','=','internal'), '|', ('company_id', '=', False),"
               "('company_id', '=', company_id)]",help="Destination Location")

