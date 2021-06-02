# -*- coding: utf-8 -*-

from odoo import fields, models


class HotelRoom(models.Model):
    _name = "hotel.room"
    _description = "Rooms"
    _rec_name = "room_number"

    room_number = fields.Char(string="Room Number", required=True)
    bed = fields.Selection(
        selection=[('single', 'Single'), ('double', 'Double'),
                   ('dormitory', 'Dormitory')], string='Bed Type',
        required=True)
    available_bed = fields.Integer(string="Available Beds")
    facility_ids = fields.Many2many('hotel.facility', string='Facilities',
                                    required=True)
    currency_id = fields.Many2one(
        'res.currency', string='Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)
    rent = fields.Monetary(string='Rent', currency_field='currency_id',
                           help='Room rent per day')
    room_available = fields.Boolean(string="Room Available", default=True)


class HotelFacility(models.Model):
    _name = "hotel.facility"
    _description = "Facilities"
    _rec_name = "facility"

    facility = fields.Char(string='Facilities', required=True)
