# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz
from odoo import api, models, tools


class HotelReport(models.AbstractModel):
    _name = "report.hotel_management.report_hotel"

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date_timestamp = (datetime.strptime(
            data['from_date'], '%Y-%m-%d') - timedelta(
            hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
        to_date_timestamp = (datetime.strptime(
            data['to_date'], '%Y-%m-%d') - timedelta(
            hours=5, minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
        data['from_date'] = datetime.strptime(
            data['from_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        data['to_date'] = datetime.strptime(
            data['to_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        tools.drop_view_if_exists(self._cr, 'hotel_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW hotel_report AS (
            SELECT row_number() OVER (ORDER BY 1) AS id,
            '""" + str(data['guest_name']) + """' AS guest,
            hotel_report.check_in, hotel_report.check_out, hotel_report.state
            FROM (SELECT hotel_accommodation.check_in AS check_in,
            hotel_accommodation.check_out AS check_out,
            hotel_accommodation.state AS state
            FROM hotel_accommodation
            WHERE ((
            check_out >= '""" + from_date_timestamp + """'
            AND check_out <= '""" + to_date_timestamp + """')
            OR (
            check_in >= '""" + from_date_timestamp + """'
            AND check_in <= '""" + to_date_timestamp + """'))
            AND hotel_accommodation.guest_id = """ + str(data['guest_id']) + """
            ) AS hotel_report)"""
                         )
        self._cr.execute("""
            SELECT id, guest, check_in, check_out, INITCAP(state)
            FROM hotel_report""")
        docs = self._cr.fetchall()
        return {
            'doc_ids': docids,
            'docs': docs,
            'data': data,
        }
