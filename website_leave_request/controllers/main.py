# -*- coding: utf-8 -*-

import math
from collections import namedtuple
from datetime import datetime, time, timedelta
from pytz import timezone, UTC

from odoo import fields, http, SUPERUSER_ID
from odoo.http import request
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY


class LeaveRequest(http.Controller):

    @http.route('/leave_requests', type='http', auth='user', website=True)
    def load_leave_request(self):
        employee_id = request.env['hr.employee'].sudo().search(
            [('user_id.id', '=', request.uid)]).id or request.env[
                          'hr.employee'].sudo().search(
            [('address_home_id', '=', request.env[
                'res.users'].sudo().search(
                [('id', '=', request.uid)]).partner_id.id)]).id
        values = {
            'leave_records': request.env['hr.leave'].sudo().search(
                [('employee_id', '=', employee_id)],
                order='request_date_from desc'),
        }
        return request.render("website_leave_request.leave_requests", values)

    @http.route('/leave_requests/new_request', type='http', auth='user',
                website=True)
    def new_leave_request(self):
        value = {
            'user': request.uid,
            'leave_types': request.env['hr.leave.type'].sudo().search(
                ['&', ('virtual_remaining_leaves', '>', 0), '|',
                 ('allocation_type', 'in', ['fixed_allocation', 'no']), '&',
                 ('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')]),
            'leave_data': request.env['hr.leave'].sudo().search([]),
            'hour_list': list(range(1, 12)),
        }
        return request.render("website_leave_request.new_leave_request", value)

    @http.route('/leave_requests/new_request_validate', type='json',
                auth='user', website=True)
    def compute_and_validate_dates(self, **kwargs):
        date_to = date_from = fields.Datetime
        DummyAttendance = namedtuple(
            'DummyAttendance',
            'hour_from, hour_to, dayofweek, day_period, week_type')
        request_date_from_period = kwargs.get('request_date_from_period')
        request_hour_from = kwargs.get('request_hour_from')
        request_hour_to = kwargs.get('request_hour_to')
        request_date_from = datetime.strptime(
            kwargs.get('request_date_from'), "%Y-%m-%d").date()
        if kwargs.get('request_date_to'):
            request_date_to = datetime.strptime(
                kwargs.get('request_date_to'), "%Y-%m-%d").date()
        else:
            request_date_to = False
        request_unit_half = False if kwargs.get(
            'request_unit_half') == 'false' else True
        request_unit_hours = False if kwargs.get(
            'request_unit_hours') == 'false' else True
        request_unit_custom = False if kwargs.get(
            'request_unit_custom') == 'false' else True
        number_of_hours_text = kwargs.get('number_of_hours_text')
        employee_id = request.env['hr.employee'].sudo().search(
            [('user_id.id', '=', request.uid)]) or request.env[
                          'hr.employee'].sudo().search(
            [('address_home_id', '=', request.env[
                'res.users'].sudo().search(
                [('id', '=', request.uid)]).partner_id.id)])
        number_of_days = 0.0
        number_of_hours = 0
        if request_date_from and request_date_to and \
                request_date_from > request_date_to:
            request_date_to = request_date_from
        if not request_date_from:
            date_from = False
        elif not request_unit_half and not request_unit_hours and not \
                request_date_to:
            date_to = False
        else:
            if request_unit_half or request_unit_hours:
                request_date_to = request_date_from
            company = request.env.company
            resource_calendar_id = employee_id.resource_calendar_id or \
                                   company.resource_calendar_id
            domain = [('calendar_id', '=', resource_calendar_id.id),
                      ('display_type', '=', False)]
            attendances = request.env[
                'resource.calendar.attendance'].with_user(
                SUPERUSER_ID).read_group(
                domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)',
                         'hour_to:max(hour_to)', 'week_type', 'dayofweek',
                         'day_period'], ['week_type', 'dayofweek',
                                         'day_period'], lazy=False)
            attendances = sorted(
                [DummyAttendance(group['hour_from'], group['hour_to'],
                                 group['dayofweek'], group['day_period'],
                                 group['week_type']) for group in attendances],
                key=lambda att: (att.dayofweek, att.day_period != 'morning'))
            default_value = DummyAttendance(0, 0, 0, 'morning', False)
            if resource_calendar_id.two_weeks_calendar:
                start_week_type = int(math.floor(
                    (request_date_from.toordinal() - 1) / 7) % 2)
                attendance_actual_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) == start_week_type]
                attendance_actual_next_week = [
                    att for att in attendances if
                    att.week_type is False or int(
                        att.week_type) != start_week_type]
                attendance_filtered = [
                    att for att in attendance_actual_week if int(
                        att.dayofweek) >= request_date_from.weekday()]
                attendance_filtered += list(attendance_actual_next_week)
                attendance_filtered += list(attendance_actual_week)
                end_week_type = int(math.floor(
                    (request_date_to.toordinal() - 1) / 7) % 2)
                attendance_actual_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) == end_week_type]
                attendance_actual_next_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) != end_week_type]
                attendance_filtered_reversed = list(reversed(
                    [att for att in attendance_actual_week if
                     int(att.dayofweek) <= request_date_to.weekday()]))
                attendance_filtered_reversed += list(
                    reversed(attendance_actual_next_week))
                attendance_filtered_reversed += list(
                    reversed(attendance_actual_week))
                attendance_from = attendance_filtered[0]
                attendance_to = attendance_filtered_reversed[0]
            else:
                attendance_from = next(
                    (att for att in attendances if int(
                        att.dayofweek) >= request_date_from.weekday()),
                    attendances[0] if attendances else default_value)
                attendance_to = next(
                    (att for att in reversed(attendances) if
                     int(att.dayofweek) <= request_date_to.weekday()),
                    attendances[-1] if attendances else default_value)
            compensated_request_date_from = request_date_from
            compensated_request_date_to = request_date_to
            if request_unit_half:
                if request_date_from_period == 'am':
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_from.hour_to)
                else:
                    hour_from = float_to_time(attendance_to.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
            elif request_unit_hours:
                hour_from = float_to_time(float(request_hour_from))
                hour_to = float_to_time(float(request_hour_to))
            elif request_unit_custom:
                hour_from = datetime.combine(
                    request_date_from, datetime.min.time()).time()
                hour_to = datetime.combine(
                    request_date_to, datetime.max.time()).time()
                user_tz = timezone(
                    request.env.user.tz if request.env.user.tz else 'UTC')
                request_date_from_utc = UTC.localize(datetime.combine(
                    request_date_from, time(0, 0, 0))).astimezone(
                    user_tz).replace(tzinfo=None)
                if request_date_from_utc.date() < request_date_from:
                    compensated_request_date_from = request_date_from + \
                                                    timedelta(days=1)
                elif request_date_from_utc.date() > request_date_from:
                    compensated_request_date_from = request_date_from - \
                                                    timedelta(days=1)
                else:
                    compensated_request_date_from = request_date_from
                request_date_to_utc = UTC.localize(datetime.combine(
                    request_date_to, time(0, 0, 0))).astimezone(
                    user_tz).replace(tzinfo=None)
                if request_date_to_utc.date() < request_date_to:
                    compensated_request_date_to = request_date_to + \
                                                  timedelta(days=1)
                elif request_date_to_utc.date() > request_date_to:
                    compensated_request_date_to = request_date_to - \
                                                  timedelta(days=1)
                else:
                    compensated_request_date_to = request_date_to
            else:
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
            date_from = timezone(request.env.user.tz).localize(
                datetime.combine(compensated_request_date_from,
                                 hour_from)).astimezone(UTC).replace(
                tzinfo=None)
            date_to = timezone(request.env.user.tz).localize(
                datetime.combine(compensated_request_date_to,
                                 hour_to)).astimezone(UTC).replace(tzinfo=None)
            if request_unit_half:
                result = employee_id._get_work_days_data_batch(
                    date_from, date_to)[employee_id.id]
                result['days'] = 0.5
                number_of_days = result['days']
                number_of_hours = result['hours']
            else:
                company = request.env.company
                today_hours = company.resource_calendar_id.get_work_hours_count(
                    datetime.combine(date_from.date(), time.min),
                    datetime.combine(date_from.date(), time.max),
                    False)
                if request_unit_custom:
                    hours = company.resource_calendar_id.get_work_hours_count(
                        date_from, date_to, False)
                    days = hours / (today_hours or HOURS_PER_DAY)
                    number_of_days = days
                    number_of_hours = hours
                else:
                    number_of_hours = float(kwargs.get('number_of_hours'))
                    number_of_days = number_of_hours / 8
            number_of_hours_text = '%s%g %s%s' % (
                '' if request_unit_half or request_unit_hours else '(',
                float_round(number_of_hours, precision_digits=2),
                _('Hours'),
                '' if request_unit_half or request_unit_hours else ')')
        hr_leave = request.env['hr.leave'].sudo()
        check_error = {}
        domain = [
            ('date_from', '<', date_to),
            ('date_to', '>', date_from),
            ('employee_id', '=', employee_id.id),
            ('state', 'not in', ['cancel', 'refuse']),
        ]
        number_of_holidays = hr_leave.search_count(domain)
        if number_of_holidays:
            check_error = {
                'checks': "exists",
            }
        holiday_status_id = int(kwargs.get('holiday_status_id'))
        hr_leave_type = request.env['hr.leave.type'].sudo().browse(
            holiday_status_id)
        mapped_days = hr_leave_type.get_employees_days(
            request.env['hr.employee'].sudo().browse(employee_id.id).ids)
        leave_days = mapped_days[employee_id.id][holiday_status_id]
        if hr_leave_type.allocation_type != 'no':
            if request_unit_custom and hr_leave_type.request_unit == 'day':
                if leave_days['virtual_remaining_leaves'] < number_of_days:
                    check_error = {
                        'checks': "over",
                    }
            else:
                if leave_days['virtual_remaining_leaves'] < number_of_hours:
                    check_error = {
                        'checks': "over",
                    }
        date_data = {
            'date_from': date_from,
            'date_to': date_to,
            'number_of_days': number_of_days,
            'number_of_hours': number_of_hours,
            'number_of_hours_text': number_of_hours_text,
            'checks': "",
        }
        date_data.update(check_error)
        return date_data

    @http.route('/leave_requests/create_request', type='http', auth='user',
                website=True)
    def create_leave_request(self, **kwargs):
        data = {}
        employee_id = request.env['hr.employee'].sudo().search(
            [('user_id.id', '=', request.uid)]).id or request.env[
                          'hr.employee'].sudo().search(
            [('address_home_id', '=', request.env[
                'res.users'].sudo().search(
                [('id', '=', request.uid)]).partner_id.id)]).id
        if employee_id:
            values = {
                'holiday_status_id': int(kwargs.get('holiday_status_id')),
                'name': kwargs.get('name'),
                'employee_id': employee_id,
                'request_date_from': kwargs.get('request_date_from'),
                'date_from': kwargs.get('date_from'),
                'date_to': kwargs.get('date_to'),
            }
            if not kwargs.get('request_hour_from') and not kwargs.get(
                    'request_date_from_period'):
                custom_day_values = {
                    'request_date_to': kwargs.get('request_date_to'),
                    'number_of_days': float(kwargs.get('number_of_days')),
                }
                values.update(custom_day_values)
            elif kwargs.get('request_hour_from') and not kwargs.get(
                    'request_date_from_period'):
                custom_hour_values = {
                    'request_date_to': kwargs.get('request_date_from'),
                    'request_hour_from': kwargs.get('request_hour_from'),
                    'request_hour_to': kwargs.get('request_hour_to'),
                    'number_of_hours_display': float(
                        kwargs.get('number_of_hours')),
                }
                values.update(custom_hour_values)
            else:
                half_day_values = {
                    'request_date_to': kwargs.get('request_date_from'),
                    'request_date_from_period': kwargs.get(
                        'request_date_from_period'),
                    'number_of_hours_display': float(
                        kwargs.get('number_of_hours')),
                    'number_of_days': float(kwargs.get('number_of_days')),
                }
                values.update(half_day_values)
            leave_count = request.env['hr.leave'].sudo().search_count([])
            request.env['hr.leave'].sudo().create(values)
            leave_count_new = request.env['hr.leave'].sudo().search_count([])
            if leave_count == leave_count_new:
                data = {
                    'message': 'Leave request could not be created!',
                    'error_check': 0,
                }
            else:
                data = {
                    'message': 'Leave request created successfully.',
                    'error_check': 1,
                }
        return request.render("website_leave_request.message_page", data)

    @http.route(
        ['/leave_requests/delete_request/<model("hr.leave"):leave_record>'],
        type='http', auth='user', website=True)
    def delete_leave_request(self, leave_record):
        if leave_record.state == 'confirm':
            cancel_record = request.env['hr.leave'].sudo().search(
                [('id', '=', leave_record.id)])
            cancel_record.write({'state': 'cancel'})
            if cancel_record.state == 'cancel':
                data = {
                    'message': 'Leave request cancelled successfully.',
                    'error_check': 1,
                }
            else:
                error = '''OOPs! Leave request could not be cancelled!'''
                data = {
                    'message': error,
                    'error_check': 0,
                }
            # cancel_record.unlink()
        else:
            error = 'You can cancel only leave request with status "To Approve"'
            data = {
                'message': error,
                'error_check': 0,
            }
        return request.render("website_leave_request.message_page", data)
