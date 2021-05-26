# -*- coding: utf-8 -*-

import pytz
from datetime import datetime

from odoo import api, models


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
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, docids):
        self._cr.execute("""
                    SELECT from_date, to_date, guest_id, res_partner.name
                    FROM hotel_report_filter
                    LEFT JOIN res_partner
                    ON hotel_report_filter.guest_id = res_partner.id
                    WHERE hotel_report_filter.id = """ + str(docids.id))
        filter_data = [
            value for tuples in self._cr.fetchall() for value in tuples]
        from_date, to_date, guest_id, guest_name = filter_data
        self._cr.execute("""
                    SELECT id, check_in, check_out, INITCAP(state), guest
                    FROM hotel_report""")
        docs = self._cr.fetchall()
        print(docs)
        sheet = workbook.add_worksheet('Hotel Management Report')
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        table_head = workbook.add_format({'font_size': '12px', 'bold': True})
        table_values = workbook.add_format({'font_size': '10px'})
        if guest_id:
            sheet.merge_range('A1:G2', 'Hotel Management Report', head)
            sheet.merge_range('A3:G3', '')
        else:
            sheet.merge_range('A1:I2', 'Hotel Management Report', head)
            sheet.merge_range('A3:I3', '')
        column = 0
        if from_date:
            sheet.merge_range(3, column, 3, column + 1, 'Date From', table_head)
            sheet.merge_range(4, column, 4, column + 1,
                              from_date.strftime('%d/%m/%Y'), table_values)
            column += 2
        if to_date:
            sheet.merge_range(3, column, 3, column + 1, 'Date To', table_head)
            sheet.merge_range(4, column, 4, column + 1,
                              to_date.strftime('%d/%m/%Y'), table_values)
            column += 2
        if guest_id:
            sheet.merge_range(3, column, 3, column + 1,
                              'Guest Name', table_head)
            sheet.merge_range(4, column, 4, column + 1,
                              guest_name, table_values)
        if from_date or to_date or guest_id:
            line = 5
        else:
            line = 3
        sheet.write(line, 0, 'SL.No', table_head)
        column = 1
        if not guest_id:
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
            if not guest_id:
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
