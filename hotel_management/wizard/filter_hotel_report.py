# -*- coding: utf-8 -*-

import json
import pytz
from datetime import datetime, time, timedelta

from odoo import api, fields, models, tools
from odoo.exceptions import ValidationError, MissingError
from odoo.tools import date_utils


class HotelReportFilter(models.TransientModel):
    _name = "hotel.report.filter"
    _description = "Hotel Management Report Filter"

    from_date = fields.Date(string='Date From')
    to_date = fields.Date(string='Date To')
    guest_id = fields.Many2one('res.partner', string='Guest Name')

    @api.onchange('from_date', 'to_date')
    def _onchange_date(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValidationError("Invalid date range")

    def create_report_view(self):
        from_date_timestamp = ''
        if self.from_date:
            from_date_timestamp = pytz.timezone(self.env.user.tz).localize(
                datetime.combine(self.from_date, time())).astimezone(
                pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        to_date_timestamp = ''
        if self.to_date:
            to_date_timestamp = pytz.timezone(self.env.user.tz).localize(
                (datetime.combine(self.to_date, time())) + timedelta(
                    days=1)).astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        if self.guest_id:
            where_clause = """WHERE hotel_accommodation.guest_id = """ + str(
                self.guest_id.id)
            if self.from_date:
                if self.to_date:
                    where_clause += """ AND ((
                            check_out >= '""" + from_date_timestamp + """'
                            AND check_out <= '""" + to_date_timestamp + """')
                            OR (check_in >= '""" + from_date_timestamp + """'
                            AND check_in <= '""" + to_date_timestamp + """'))"""
                else:
                    where_clause += """ AND (
                            check_out >= '""" + from_date_timestamp + """'
                            OR check_in >= '""" + from_date_timestamp + """')"""
            else:
                if self.to_date:
                    where_clause += """ AND (
                            check_out <= '""" + to_date_timestamp + """'
                            OR check_in <= '""" + to_date_timestamp + """')"""
        else:
            if self.from_date:
                if self.to_date:
                    where_clause = """WHERE (
                            check_out >= '""" + from_date_timestamp + """'
                            AND check_out <= '""" + to_date_timestamp + """')
                            OR (check_in >= '""" + from_date_timestamp + """'
                            AND check_in <= '""" + to_date_timestamp + """')"""
                else:
                    where_clause = """WHERE
                            check_out >= '""" + from_date_timestamp + """'
                            OR check_in >= '""" + from_date_timestamp + """'"""
            else:
                if self.to_date:
                    where_clause = """WHERE
                            check_out <= '""" + to_date_timestamp + """'
                            OR check_in <= '""" + to_date_timestamp + """'"""
                else:
                    where_clause = """WHERE state != 'draft'"""
        tools.drop_view_if_exists(self._cr, 'hotel_report')
        self._cr.execute("""CREATE OR REPLACE VIEW hotel_report AS (
                        SELECT row_number() OVER (ORDER BY 1) AS id,
                        hotel_report.check_in, hotel_report.check_out,
                        hotel_report.state, hotel_report.guest
                        FROM (SELECT hotel_accommodation.check_in AS check_in,
                        hotel_accommodation.check_out AS check_out,
                        hotel_accommodation.state AS state,
                        res_partner.name AS guest
                        FROM hotel_accommodation
                        LEFT JOIN res_partner
                        ON hotel_accommodation.guest_id = res_partner.id
                        %s ORDER BY state, hotel_accommodation.id DESC
                        )AS hotel_report)""" % where_clause)

    def get_to_date(self):
        self._cr.execute("""SELECT
                            CASE 
                                WHEN (SELECT max(check_in) FROM hotel_report) > 
                                (SELECT max(check_out) FROM hotel_report) THEN
                                (SELECT max(check_in) FROM hotel_report)
                                ELSE (SELECT max(check_out) FROM hotel_report)
                            END as to_date;""")
        return self._cr.fetchall()[0][0]

    def get_from_date(self):
        self._cr.execute("""SELECT
                            CASE 
                                WHEN (SELECT min(check_in) FROM hotel_report) < 
                                (SELECT min(check_out) FROM hotel_report) THEN
                                (SELECT min(check_in) FROM hotel_report)
                                ELSE (SELECT min(check_out) FROM hotel_report)
                            END as to_date;""")
        return self._cr.fetchall()[0][0]

    def action_print_report_pdf(self):
        self.create_report_view()
        self._cr.execute("SELECT * FROM hotel_report")
        docs = self._cr.fetchall()
        if not docs:
            raise MissingError("Record does not exist or has been deleted.")
        if not self.from_date:
            from_date = self.get_from_date().astimezone(
                        pytz.timezone(self.env.user.tz)).date()
            if self.to_date:
                data = {
                    'from_date': from_date,
                    'to_date': self.to_date,
                    'guest_id': self.guest_id.id,
                    'guest_name': self.guest_id.name,
                }
            else:
                data = {
                    'from_date': from_date,
                    'to_date': self.get_to_date().astimezone(
                        pytz.timezone(self.env.user.tz)).date(),
                    'guest_id': self.guest_id.id,
                    'guest_name': self.guest_id.name,
                }
        elif not self.to_date:
            data = {
                'from_date': self.from_date,
                'to_date': self.get_to_date().astimezone(
                        pytz.timezone(self.env.user.tz)).date(),
                'guest_id': self.guest_id.id,
                'guest_name': self.guest_id.name,
            }
        else:
            data = {
                'from_date': self.from_date,
                'to_date': self.to_date,
                'guest_id': self.guest_id.id,
                'guest_name': self.guest_id.name,
            }
        return self.env.ref(
            'hotel_management.hotel_action_report_pdf').report_action(
            None, data=data)

    def action_print_report_xlsx(self):
        self.create_report_view()
        self._cr.execute("SELECT * FROM hotel_report")
        docs = self._cr.fetchall()
        if not docs:
            raise MissingError("Record does not exist or has been deleted.")
        data = {
            'from_date': self.from_date,
            'to_date': self.to_date,
            'guest_id': self.guest_id.id,
            'guest_name': self.guest_id.name,
        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'report.hotel_management.report_xlsx',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Hotel Management Report',
                     },
            'report_type': 'xlsx',
        }
