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
        company_name = workbook.add_format(
            {'font_size': '12px', 'bold': True, 'bg_color': '#FFFFFF'})
        company_data = workbook.add_format(
            {'font_size': '10px', 'bold': True, 'bg_color': '#FFFFFF'})
        head = workbook.add_format({'align': 'center', 'bold': True,
                                    'font_size': '20px', 'bg_color': '#D3D3D3'})
        filter_head = workbook.add_format(
            {'font_size': '10px', 'bold': True, 'bg_color': '#FFFFFF'})
        filter_value = workbook.add_format(
            {'font_size': '10px', 'bg_color': '#FFFFFF'})
        table_head = workbook.add_format({'font_size': '12px', 'bold': True,
                                          'bg_color': '#D3D3D3', 'border': 1})
        table_value = workbook.add_format({'font_size': '10px', 'border': 1})
        if data['guest_id']:
            report_width = 8
        else:
            report_width = 10
        sheet.merge_range(0, 0, 0, 3, self.env.company.name, company_name)
        sheet.merge_range(0, 4, 0, report_width, '', company_data)
        line = 1
        if self.env.company.partner_id.street:
            sheet.merge_range(line, 0, line, 3,
                              self.env.company.partner_id.street, company_data)
            sheet.merge_range(line, 4, line, report_width, '', company_data)
            line += 1
        if self.env.company.partner_id.street2:
            sheet.merge_range(line, 0, line, 3,
                              self.env.company.partner_id.street2, company_data)
            sheet.merge_range(line, 4, line, report_width, '', company_data)
            line += 1
        if self.env.company.city or self.env.company.zip:
            sheet.merge_range(line, 0, line, 3, self.env.company.city + ' ' +
                              self.env.company.zip, company_data)
            sheet.merge_range(line, 4, line, report_width, '', company_data)
            line += 1
        if self.env.company.state_id:
            sheet.merge_range(line, 0, line, 3,
                              self.env.company.state_id.name + ' ' +
                              self.env.company.state_id.code, company_data)
            sheet.merge_range(line, 4, line, report_width, '', company_data)
            line += 1
        if self.env.company.country_id.name:
            sheet.merge_range(line, 0, line, 3,
                              self.env.company.country_id.name, company_data)
            sheet.merge_range(line, 4, line, report_width, '', company_data)
            line += 1
        sheet.insert_image(0, 4, '../web/binary/company_logo')
        sheet.merge_range(line, 0, line + 1, report_width,
                          'Hotel Management Report', head)
        line += 2
        sheet.merge_range(line, 0, line, 1, 'Date of Report  :', filter_head)
        sheet.merge_range(line, 2, line, 4,
                          datetime.today().astimezone(pytz.timezone(
                              self.env.user.tz)).strftime(
                              '%d/%m/%Y %H:%M:%S'), filter_value)
        sheet.merge_range(line, 5, line, report_width, '', filter_value)
        line += 1
        sheet.merge_range(line, 0, line, 1, 'Date From        :', filter_head)
        sheet.merge_range(
            line, 2, line, 4, datetime.strptime(
                data['from_date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
            filter_value)
        sheet.merge_range(line, 5, line, report_width, '', filter_value)
        line += 1
        sheet.merge_range(line, 0, line, 1, 'Date To            :', filter_head)
        sheet.merge_range(
            line, 2, line, 4, datetime.strptime(
                data['to_date'], '%Y-%m-%d').strftime('%d/%m/%Y'),
            filter_value)
        sheet.merge_range(line, 5, line, report_width, '', filter_value)
        if data['guest_id']:
            line += 1
            sheet.merge_range(line, 0, line, 1, 'Guest Name     :', filter_head)
            sheet.merge_range(line, 2, line, 4,
                              data['guest_name'], filter_value)
            sheet.merge_range(line, 5, line, report_width, '', filter_value)
        line += 1
        sheet.write(line, 0, 'SL.No', table_head)
        column = 1
        if not data['guest_id']:
            sheet.merge_range(line, column, line, column + 1,
                              'Guest', table_head)
            column += 2
        sheet.merge_range(line, column, line, column + 2,
                          'Check-In', table_head)
        column += 3
        sheet.merge_range(line, column, line, column + 2,
                          'Check-Out', table_head)
        column += 3
        sheet.merge_range(line, column, line, column + 1, 'State', table_head)
        line += 1
        for doc in docs:
            sheet.write(line, 0, doc[0], table_value)
            column = 1
            if not data['guest_id']:
                sheet.merge_range(line, column, line, column + 1,
                                  doc[4], table_value)
                column += 2
            sheet.merge_range(
                line, column, line, column + 2, doc[1].astimezone(pytz.timezone(
                    self.env.user.tz)).strftime('%d/%m/%Y %H:%M:%S'),
                table_value)
            column += 3
            if doc[2]:
                sheet.merge_range(line, column, line, column + 2,
                                  doc[2].astimezone(pytz.timezone(
                                      self.env.user.tz)).strftime(
                                      '%d/%m/%Y %H:%M:%S'), table_value)
            else:
                sheet.merge_range(
                    line, column, line, column + 2, '', table_value)
            column += 3
            sheet.merge_range(
                line, column, line, column + 1, doc[3], table_value)
            line += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
