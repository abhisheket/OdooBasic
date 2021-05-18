# -*- coding: utf-8 -*-

from odoo import api, exceptions, fields, models
from odoo.tools import date_utils


class HotelAccommodation(models.Model):
    _name = "hotel.accommodation"
    _description = "Accommodation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Number", required=True, copy=False,
                       readonly=True, default=lambda self: 'New')
    guest_id = fields.Many2one('res.partner', ondelete='restrict',
                               string="Guest", required=True)
    number_of_guest = fields.Integer(string='Number Of Guests', required=True)
    check_in = fields.Datetime(string="Check In", readonly=True)
    check_out = fields.Datetime(string="Check Out", readonly=True)
    bed_type = fields.Selection(
        selection=[('single', 'Single'), ('double', 'Double'),
                   ('dormitory', 'Dormitory')], string='Bed Type',
        required=True)
    facility_ids = fields.Many2many('hotel.facility', string='Facilities',
                                    required=True)
    room_number_id = fields.Many2one('hotel.room', ondelete='restrict',
                                     string="Room", required=True)
    state = fields.Selection(
        selection=[('draft', 'Draft'), ('check-in', 'Check-In'),
                   ('check-out', 'Check-Out'), ('cancel', 'Cancel')],
        required=True, default='draft')
    expected_day = fields.Integer(string='Expected Days')
    expected_date = fields.Datetime(string='Expected Date', store=True,
                                    compute='_compute_expected_date')
    guest_list_ids = fields.One2many('hotel.guest', 'guest_list_id',
                                     string='Guest list')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    rent_per_day = fields.Monetary(string="Rent per Day", store=True,
                                   related='room_number_id.rent')
    rent = fields.Monetary(string='Rent', currency_field='currency_id',
                           compute='_compute_rent', store=True)
    payment_line_ids = fields.One2many('hotel.order.list', 'accommodation_id',
                                       string='Payment Lines')
    total = fields.Monetary(string='Total', currency_field='currency_id',
                            compute='_compute_total', store=True)
    invoice_count = fields.Integer(string='Invoice Count', readonly=True,
                                   default=0)
    payment_status = fields.Boolean(string='Payment Status', default=False,
                                    compute='_compute_payment_status')

    @api.model
    def create(self, values):
        if values.get('name', 'New') == 'New':
            values['name'] = self.env['ir.sequence'].next_by_code(
                'hotel.accommodation.sequence') or 'New'
        result = super(HotelAccommodation, self).create(values)
        return result

    @api.depends('expected_day', 'check_in')
    def _compute_expected_date(self):
        for record in self:
            record.expected_date = False
            if record.check_in:
                record.expected_date = date_utils.add(record.check_in,
                                                      days=record.expected_day)

    @api.onchange('bed_type', 'facility_ids')
    def _onchange_bed_type_and_facility_ids(self):
        match_room_facility = []
        if self.facility_ids:
            facility_list = list(set(self.facility_ids.ids))
            for record in self.env['hotel.room'].search([]):
                if record.facility_ids.ids == facility_list:
                    match_room_facility.append(record.id)
        match_room_bed_type = []
        if self.bed_type:
            for record in self.env['hotel.room'].search([]):
                if record.bed == self.bed_type:
                    match_room_bed_type.append(record.id)
        if match_room_bed_type and match_room_facility:
            return {'domain': {
                'room_number_id': [('room_available', '=', True),
                                   ('id', 'in', match_room_bed_type),
                                   ('id', 'in', match_room_facility)]}}
        else:
            return {'domain': {'room_number_id': [
                ('id', 'not in', self.env['hotel.room'].search([]).ids)]}}

    def action_check_in(self):
        if self.number_of_guest != len(self.guest_list_ids):
            raise exceptions.ValidationError(
                "Please provide all guest details")
        if not self.message_main_attachment_id.id:
            raise exceptions.ValidationError("Please attach the Address proof")
        self.state = "check-in"
        self.check_in = fields.Datetime.now()
        self.env['hotel.room'].search(
            [('id', '=', self.room_number_id.id)]).write(
            {'room_available': False})
        rent_line = self.env['hotel.order.list'].search(
            [('accommodation_id', '=', self.id),
             ('order_list_id', '=', False)]).id
        values = {
            'product': 'Room Rent',
            'accommodation_id': self.id,
            'quantity': self.expected_day,
            'uom_id': self.env.ref('uom.product_uom_day').id,
            'price': self.rent_per_day,
            'subtotal': self.rent,
        }
        if rent_line:
            payment_line = [(1, rent_line, values)]
            self.payment_line_ids = payment_line
        else:
            payment_line = [(0, 0, values)]
            self.payment_line_ids = payment_line

    def action_cancel(self):
        if self.invoice_count:
            raise exceptions.UserError(
                "You can't cancel an entry once invoice is created")
        elif len(self.payment_line_ids) > 1:
            raise exceptions.UserError(
                "You can't cancel an entry once order is created")
        self.state = "cancel"
        self.env['hotel.room'].search(
            [('id', '=', self.room_number_id.id)]).write(
            {'room_available': True})
        self.check_in = False
        self.check_out = False
        self.expected_date = False

    def action_reset_to_draft(self):
        self.state = "draft"
        self.env['hotel.room'].search(
            [('id', '=', self.room_number_id.id)]).write(
            {'room_available': True})

    @api.depends('expected_day')
    def _compute_rent(self):
        for record in self:
            if record.expected_day:
                record.rent = record.expected_day * record.env[
                    'hotel.room'].search(
                    [('id', '=', record.room_number_id.id)]).rent
            else:
                record.rent = 0

    @api.depends('payment_line_ids')
    def _compute_total(self):
        for record in self:
            payment_total = 0
            if record.payment_line_ids:
                for line in record.payment_line_ids:
                    payment_total += line.subtotal
            record.total = payment_total

    def create_invoice(self):
        if not self.env['account.move'].search(
                [('invoice_origin', '=', self.name)]):
            invoice_lines = []
            current_date = fields.Date.today()
            for record in self.payment_line_ids:
                invoice_lines.append((0, 0, {
                    'product_id': record.name_id,
                    'name': record.product,
                    'quantity': record.quantity,
                    'price_unit': record.price,
                    'price_subtotal': record.subtotal,
                }))
            invoice = self.env['account.move'].create({
                'move_type': 'out_invoice',
                'currency_id': self.currency_id.id,
                'invoice_user_id': self.env.uid,
                'partner_id': self.guest_id.id,
                'invoice_origin': self.name,
                'invoice_date': current_date,
                'invoice_line_ids': invoice_lines,
                'company_id': self.env.company.id,
            })
            return invoice

    def action_check_out(self):
        self.state = "check-out"
        self.check_out = fields.Datetime.now()
        self.env['hotel.room'].search(
            [('id', '=', self.room_number_id.id)]).write(
            {'room_available': True})
        self.create_invoice()
        self.invoice_count = 1
        return {
            'name': 'Invoice',
            'view_mode': 'form',
            'views': [[self.env.ref('account.view_move_form').id, 'form']],
            'res_model': 'account.move',
            'res_id': self.env['account.move'].search(
                [('invoice_origin', '=', self.name)]).id,
            'type': 'ir.actions.act_window',
            'target': 'next',
        }

    def action_view_invoice(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "account.action_move_out_invoice_type")
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = self.env['account.move'].search(
            [('invoice_origin', '=', self.name)]).id
        return action

    def _compute_payment_status(self):
        for record in self:
            invoice = record.env['account.move'].search(
                [('invoice_origin', '=', record.name)])
            if invoice:
                if invoice.payment_state == 'paid':
                    record.payment_status = True
                else:
                    record.payment_status = False
            else:
                record.payment_status = False


class HotelGuest(models.Model):
    _name = "hotel.guest"
    _description = "Guest Information"
    _rec_name = "guest_list_id"

    guest_list_id = fields.Many2one('hotel.accommodation', string='Number')
    guest_name_id = fields.Many2one('res.partner', ondelete='restrict',
                                    string="Guest", required=True)
    gender = fields.Selection(
        selection=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        string='Gender')
    age = fields.Integer(string='Age')
