# -*- coding: utf-8 -*-
from odoo import fields, models, api, exceptions


class HotelOrderFood(models.Model):
    _name = "hotel.order.food"
    _description = "Order Food"
    _rec_name = "id"
    _order = "id desc"

    room_id = fields.Many2one('hotel.room', ondelete='restrict',
                              string="Room Number", required=True)
    accommodation_id = fields.Many2one('hotel.accommodation', store=True,
                                       string="Number", ondelete='restrict')
    guest_id = fields.Many2one('res.partner', string='Guest', store=True,
                               ondelete='restrict',
                               related='accommodation_id.guest_id')
    order_time = fields.Datetime(string='Order Time', readonly=True,
                                 default=lambda self: fields.datetime.now())
    category_ids = fields.Many2many('hotel.food.category', store=False,
                                    string="Food Category")
    food_ids = fields.Many2many('hotel.food', required=True, string="Food List")
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    total = fields.Monetary(string='Total', currency_field='currency_id',
                            compute='_compute_total', store=True)
    order_list_ids = fields.One2many('hotel.order.list', 'order_list_id',
                                     string='Order list')
    active_id = fields.Integer(string='Active ID', compute='_compute_active_id')

    @api.onchange('room_id')
    def _onchange_room_id(self):
        if self.room_id:
            self.accommodation_id = self.env['hotel.accommodation'].search(
                [('room_number_id', '=', self.room_id.id),
                 ('state', '=', 'check-in')])

    @api.onchange('category_ids')
    def _onchange_category_ids(self):
        if self.category_ids:
            self.food_ids = self.env['hotel.food'].search(
                [('category_id', 'in', self.category_ids.ids)]).ids
        else:
            self.food_ids = self.env['hotel.food'].search([]).ids

    @api.depends('order_list_ids')
    def _compute_total(self):
        for record in self:
            lines = record.env['hotel.order.list'].search(
                [('order_list_id', '=', record.active_id)])
            order_total = 0
            if lines:
                for line in lines:
                    order_total += line.subtotal
            record.total = order_total

    def _compute_active_id(self):
        for record in self:
            record.active_id = record.id


class HotelFoodCategory(models.Model):
    _name = "hotel.food.category"
    _description = "Food Category"
    _rec_name = "food_category"

    food_category = fields.Char(string='Food Category', required=True)


class HotelFood(models.Model):
    _name = "hotel.food"
    _description = "Food"
    _rec_name = "food"

    food = fields.Char(string='Name', required=True)
    category_id = fields.Many2one('hotel.food.category', string='Category',
                                  required=True, ondelete='restrict')
    image = fields.Image(string='Image', max_width=128, max_height=128,
                         store=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    price = fields.Monetary(string='Price', currency_field='currency_id')
    quantity = fields.Integer(string='Quantity', required=True, default=0)
    description = fields.Text(string='Description', required=True)

    def add_to_list(self):
        if self.quantity < 1:
            raise exceptions.ValidationError("Order minimum 1 quantity")
        else:
            active_id = self.env.context['active_record_id']
            orders = self.env['hotel.order.list'].search(
                [('order_list_id', '=', active_id)])
            existing_item = 0
            for record in orders:
                if record.name_id.id == self.id:
                    existing_item = 1
            if existing_item:
                raise exceptions.ValidationError("Item Already Added!")
            else:
                values = {
                    'name_id': self.id,
                    'quantity': self.quantity,
                    'price': self.price,
                }
                lines = [(0, 0, values)]
                self.env['hotel.order.food'].search(
                    [('id', '=', active_id)]).order_list_ids = lines
            self.quantity = 0


class HotelOrderList(models.Model):
    _name = "hotel.order.list"
    _description = "Order List"
    _rec_name = "order_list_id"

    order_list_id = fields.Many2one('hotel.order.food', string='Number',
                                    ondelete='restrict')
    accommodation_id = fields.Many2one(
        'hotel.accommodation', string='Number', ondelete='restrict', store=True,
        related='order_list_id.accommodation_id', readonly=False)
    name_id = fields.Many2one('hotel.food', string='Item Name',
                              ondelete='restrict')
    product = fields.Char(string="Product Name", store=True,
                          related='name_id.food', readonly=False)
    description = fields.Text(string='Description', store=True,
                              related='name_id.description')
    quantity = fields.Integer(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='UoM',
                             default=lambda self: self.env.ref(
                                 'uom.product_uom_unit').id)
    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.user.company_id.currency_id.id)
    price = fields.Monetary(string='Unit Price', currency_field='currency_id')
    subtotal = fields.Monetary(string='Subtotal Price', store=True,
                               currency_field='currency_id',
                               compute='_compute_subtotal')

    @api.depends('quantity', 'price')
    def _compute_subtotal(self):
        for record in self:
            if record.quantity and record.price:
                record.subtotal = record.quantity * record.price
