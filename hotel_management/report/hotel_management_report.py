# -*- coding: utf-8 -*-

import io
import pytz
from datetime import datetime

from odoo import api, models

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class HotelReport(models.AbstractModel):
    _name = "report.hotel_management.report_pdf"

    @api.model
    def _get_report_values(self, docids, data=None):
        if data['from_date']:
            data['from_date'] = datetime.strptime(
                data['from_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        if data['to_date']:
            data['to_date'] = datetime.strptime(
                data['to_date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        self._cr.execute("""
            SELECT id, check_in, check_out, INITCAP(state), guest
            FROM hotel_report""")
        docs = self._cr.fetchall()
        return {
            'doc_ids': docids,
            'docs': docs,
            'data': data,
        }


class HotelReportXLSX(models.AbstractModel):
    _name = "report.hotel_management.report_xlsx"

    def get_xlsx_report(self, data, response):
        self._cr.execute("""SELECT id, check_in, check_out,
                            INITCAP(state), guest
                            FROM hotel_report""")
        docs = self._cr.fetchall()
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('Hotel Management Report')
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        table_head = workbook.add_format({'font_size': '12px', 'bold': True})
        table_values = workbook.add_format({'font_size': '10px'})
        sheet.merge_range('A3:B3', 'Generated On:', table_head)
        if data['guest_id']:
            sheet.merge_range('A1:G2', 'Hotel Management Report', head)
            sheet.merge_range('C3:G3', datetime.today().strftime(
                '%d/%m/%Y %H:%M:%S'), table_values)
        else:
            sheet.merge_range('A1:I2', 'Hotel Management Report', head)
            sheet.merge_range('C3:I3', datetime.today().astimezone(
                pytz.timezone(self.env.user.tz)).strftime(
                '%d/%m/%Y %H:%M:%S'), table_values)
        column = 0
        if data['from_date']:
            sheet.merge_range(3, column, 3, column + 1, 'Date From', table_head)
            sheet.merge_range(
                4, column, 4, column + 1, datetime.strptime(
                    data['from_date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                table_values)
            column += 2
        if data['to_date']:
            sheet.merge_range(3, column, 3, column + 1, 'Date To', table_head)
            sheet.merge_range(
                4, column, 4, column + 1, datetime.strptime(
                    data['to_date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
                table_values)
            column += 2
        if data['guest_id']:
            sheet.merge_range(3, column, 3, column + 1,
                              'Guest Name', table_head)
            sheet.merge_range(4, column, 4, column + 1,
                              data['guest_name'], table_values)
        if data['from_date'] or data['to_date'] or data['guest_id']:
            line = 5
        else:
            line = 3
        sheet.write(line, 0, 'SL.No', table_head)
        column = 1
        if not data['guest_id']:
            sheet.merge_range(line, column, line, column + 1,
                              'Guest', table_head)
            column += 2
        sheet.merge_range(line, column, line, column + 1,
                          'Check-In', table_head)
        column += 2
        sheet.merge_range(line, column, line, column + 1,
                          'Check-Out', table_head)
        column += 2
        sheet.merge_range(line, column, line, column + 1, 'State', table_head)
        line += 1
        for doc in docs:
            sheet.write(line, 0, doc[0], table_values)
            column = 1
            if not data['guest_id']:
                sheet.merge_range(line, column, line, column + 1,
                                  doc[4], table_values)
                column += 2
            sheet.merge_range(
                line, column, line, column + 1, doc[1].astimezone(pytz.timezone(
                    self.env.user.tz)).strftime('%d/%m/%Y %H:%M:%S'),
                table_values)
            column += 2
            if doc[2]:
                sheet.merge_range(line, column, line, column + 1,
                                  doc[2].astimezone(pytz.timezone(
                                      self.env.user.tz)).strftime(
                                      '%d/%m/%Y %H:%M:%S'), table_values)
            else:
                sheet.merge_range(
                    line, column, line, column + 1, '', table_values)
            column += 2
            sheet.merge_range(line, column, line, column + 1, doc[3],
                              table_values)
            line += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
