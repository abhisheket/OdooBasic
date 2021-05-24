# -*- coding: utf-8 -*-

import pytz
from datetime import datetime, time, timedelta

from odoo import api, models, tools


class HotelReport(models.AbstractModel):
    _name = "report.hotel_management.report_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        from_date_timestamp = pytz.timezone(self.env.user.tz).localize(
            datetime.strptime(data['from_date'], '%Y-%m-%d')).astimezone(
            pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        to_date_timestamp = pytz.timezone(self.env.user.tz).localize(
            datetime.strptime(data['to_date'], '%Y-%m-%d') + timedelta(
                days=1)).astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        data['from_date'] = datetime.strptime(
            data['from_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        data['to_date'] = datetime.strptime(
            data['to_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        tools.drop_view_if_exists(self._cr, 'hotel_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW hotel_report AS (
            SELECT row_number() OVER (ORDER BY 1) AS id,
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
            ORDER BY state, id DESC) AS hotel_report)""")
        self._cr.execute("""
            SELECT id, check_in, check_out, INITCAP(state)
            FROM hotel_report""")
        docs = self._cr.fetchall()
        return {
            'doc_ids': docids,
            'docs': docs,
            'data': data,
        }


class HotelReportXLSX(models.AbstractModel):
    _name = "report.hotel_management.report_xlsx"
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, docids):
        from_date_timestamp = pytz.timezone(self.env.user.tz).localize(
            datetime.combine(
                self.env['hotel.report.filter'].browse([docids.id]).from_date,
                time())).astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        to_date_timestamp = pytz.timezone(self.env.user.tz).localize(
            (datetime.combine(self.env['hotel.report.filter'].browse(
                [docids.id]).to_date, time())) + timedelta(days=1)).astimezone(
            pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        tools.drop_view_if_exists(self._cr, 'hotel_report')
        self._cr.execute("""
            CREATE OR REPLACE VIEW hotel_report AS (
            SELECT row_number() OVER (ORDER BY 1) AS id,
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
            AND hotel_accommodation.guest_id = """ + str(
            self.env['hotel.report.filter'].browse(
                [docids.id]).guest_id.id) + """
            ORDER BY state, id DESC) AS hotel_report)""")
        self._cr.execute("""
            SELECT id, check_in, check_out, INITCAP(state)
            FROM hotel_report""")
        docs = self._cr.fetchall()
        sheet = workbook.add_worksheet('Hotel Management Report')
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        table_head = workbook.add_format({'font_size': '12px', 'bold': True})
        table_values = workbook.add_format({'font_size': '10px'})
        sheet.merge_range('A1:G2', 'Hotel Management Report', head)
        sheet.merge_range('A3:G3', '')
        sheet.merge_range('A4:B4', 'Date From', table_head)
        sheet.merge_range('A5:B5', self.env['hotel.report.filter'].browse(
            [docids.id]).from_date.strftime('%d/%m/%Y'), table_values)
        sheet.merge_range('C4:D4', 'Date To', table_head)
        sheet.merge_range('C5:D5', self.env['hotel.report.filter'].browse(
            [docids.id]).to_date.strftime('%d/%m/%Y'), table_values)
        sheet.merge_range('E4:G4', 'Guest Name', table_head)
        sheet.merge_range('E5:G5', self.env['hotel.report.filter'].browse(
            [docids.id]).guest_id.name, table_values)
        sheet.merge_range('A6:G6', '')
        sheet.write('A7', 'SL.No', table_head)
        sheet.merge_range('B7:C7', 'Check-In', table_head)
        sheet.merge_range('D7:E7', 'Check-Out', table_head)
        sheet.merge_range('F7:G7', 'State', table_head)
        for doc in docs:
            line = doc[0] + 6
            sheet.write(line, 0, doc[0], table_values)
            sheet.merge_range(
                line, 1, line, 2, doc[1].astimezone(pytz.timezone(
                    self.env.user.tz)).strftime('%d/%m/%Y %H:%M:%S'),
                table_values)
            if doc[2]:
                sheet.merge_range(line, 3, line, 4, doc[2].astimezone(
                    pytz.timezone(self.env.user.tz)).strftime(
                    '%d/%m/%Y %H:%M:%S'), table_values)
            else:
                sheet.merge_range(
                    line, 3, line, 4, '', table_values)
            sheet.merge_range(line, 5, line, 6, doc[3], table_values)
        workbook.close()
