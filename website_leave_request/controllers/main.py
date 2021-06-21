# -*- coding: utf-8 -*-

import math

from collections import namedtuple

from datetime import datetime, time, timedelta
from pytz import timezone, UTC

from odoo import http
from odoo.http import request
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _


class LeaveRequest(http.Controller):

    @http.route('/leave_requests', type='http', auth='user', website=True)
    def load_leave_request(self):
        employee_id = request.env['hr.employee'].sudo().search(
            [('address_home_id', '=', request.env['res.users'].sudo().search(
                [('id', '=', request.uid)]).partner_id.id)]).id
        if employee_id:
            leave_records = request.env['hr.leave'].sudo().search(
                [('employee_id', '=', employee_id)],
                order='request_date_from desc')
        else:
            leave_records = request.env['hr.leave'].sudo().search(
                [('user_id.id', '=', request.uid)],
                order='request_date_from desc')

        values = {
            'leave_records': leave_records,
        }
        return request.render("website_leave_request.leave_requests", values)

    @http.route('/leave_requests/new_request', type='http', auth='user',
                website=True)
    def new_leave_request(self):
        leave_types = request.env['hr.leave.type'].sudo().search(
            ['&', ('virtual_remaining_leaves', '>', 0), '|',
             ('allocation_type', 'in', ['fixed_allocation', 'no']), '&',
             ('allocation_type', '=', 'fixed'), ('max_leaves', '>', '0')])
        leave_data = request.env['hr.leave'].sudo().search([])
        hour_list = list(range(1, 12))
        user = request.uid
        value = {
            'user': user,
            'leave_types': leave_types,
            'leave_data': leave_data,
            'hour_list': hour_list,
        }
        return request.render("website_leave_request.new_leave_request", value)

    @http.route('/leave_requests/new_request_validate', type='json',
                auth='user', website=True)
    def compute_date_from_date_to(self, **kwargs):
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
        employee_id = request.env['hr.employee'].sudo().search(
                    [('user_id.id', '=', request.uid)])
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
            resource_calendar_id = employee_id.resource_calendar_id or \
                                   request.env.company.resource_calendar_id
            domain = [('calendar_id', '=', resource_calendar_id.id),
                      ('display_type', '=', False)]
            attendances = request.env[
                'resource.calendar.attendance'].read_group(domain, [
                'ids:array_agg(id)', 'hour_from:min(hour_from)',
                'hour_to:max(hour_to)', 'week_type', 'dayofweek',
                'day_period'], ['week_type', 'dayofweek', 'day_period'],
                                                           lazy=False)

            # Must be sorted by dayofweek ASC and day_period DESC
            attendances = sorted(
                [DummyAttendance(group['hour_from'], group['hour_to'],
                                 group['dayofweek'], group['day_period'],
                                 group['week_type']) for group in attendances],
                key=lambda att: (att.dayofweek, att.day_period != 'morning'))

            default_value = DummyAttendance(0, 0, 0, 'morning', False)

            if resource_calendar_id.two_weeks_calendar:
                # find week type of start_date
                start_week_type = int(math.floor(
                    (request_date_from.toordinal() - 1) / 7) % 2)
                attendance_actual_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) == start_week_type]
                attendance_actual_next_week = [
                    att for att in attendances if
                    att.week_type is False or int(
                        att.week_type) != start_week_type]
                # First, add days of actual week coming after date_from
                attendance_filtred = [
                    att for att in attendance_actual_week if int(
                        att.dayofweek) >= request_date_from.weekday()]
                # Second, add days of the other type of week
                attendance_filtred += list(attendance_actual_next_week)
                # Third, add days of actual week (to consider days that we have
                # remove first because they coming before date_from)
                attendance_filtred += list(attendance_actual_week)

                end_week_type = int(math.floor(
                    (request_date_to.toordinal() - 1) / 7) % 2)
                attendance_actual_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) == end_week_type]
                attendance_actual_next_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) != end_week_type]
                attendance_filtred_reversed = list(reversed(
                    [att for att in attendance_actual_week if
                     int(att.dayofweek) <= request_date_to.weekday()]))
                attendance_filtred_reversed += list(
                    reversed(attendance_actual_next_week))
                attendance_filtred_reversed += list(
                    reversed(attendance_actual_week))

                # find first attendance coming after first_day
                attendance_from = attendance_filtred[0]
                # find last attendance coming before last_day
                attendance_to = attendance_filtred_reversed[0]
            else:
                # find first attendance coming after first_day
                attendance_from = next(
                    (att for att in attendances if int(
                        att.dayofweek) >= request_date_from.weekday()),
                    attendances[0] if attendances else default_value)
                # find last attendance coming before last_day
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
                # hour_from = float_to_time(attendance_from.hour_from)
                # hour_to = float_to_time(attendance_to.hour_to)
                print('hour_from', type(hour_from))
                print('hour_to', hour_to)
                print(time())
                user_tz = timezone(
                    request.env.user.tz if request.env.user.tz else 'UTC')

                request_date_from_utc = UTC.localize(datetime.combine(
                    request_date_from, time(0, 0, 0))).astimezone(
                    user_tz).replace(tzinfo=None)
                print(request_date_from_utc)
                if request_date_from_utc.date() < request_date_from:
                    compensated_request_date_from = request_date_from + timedelta(days=1)
                    print("+++++ from")
                elif request_date_from_utc.date() > request_date_from:
                    compensated_request_date_from = request_date_from - timedelta(days=1)
                    print("------ from")
                else:
                    compensated_request_date_from = request_date_from
                    print("same from")
                print('c-date_from', compensated_request_date_from)
                request_date_to_utc = UTC.localize(datetime.combine(
                    request_date_to, time(0, 0, 0))).astimezone(
                    user_tz).replace(tzinfo=None)
                print(request_date_to_utc)
                if request_date_to_utc.date() < request_date_to:
                    compensated_request_date_to = request_date_to + timedelta(days=1)
                    print("+++++ to")
                elif request_date_to_utc.date() > request_date_to:
                    compensated_request_date_to = request_date_to - timedelta(days=1)
                    print("------ to")
                else:
                    compensated_request_date_to = request_date_to
                    print("same to")
                print('c-date_to', compensated_request_date_to)
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
                print("if", request_unit_half, request_unit_hours,
                      request_unit_custom)
                result = employee_id._get_work_days_data_batch(
                    date_from, date_to)[employee_id.id]
                result['days'] = 0.5
                number_of_days = result['days']
                number_of_hours = result['hours']
            elif request_unit_custom:
                print("elif", request_unit_half, request_unit_hours,
                      request_unit_custom)
                company = request.env.company
                today_hours = company.resource_calendar_id.get_work_hours_count(
                    datetime.combine(date_from.date(), time.min),
                    datetime.combine(date_from.date(), time.max),
                    False)
                print('today_hours', today_hours)
                hours = company.resource_calendar_id.get_work_hours_count(
                    date_from, date_to, False)
                print('hours', hours)
                print('HOURS_PER_DAY', HOURS_PER_DAY)
                days = hours / (today_hours or HOURS_PER_DAY)
                print('days', days)
                number_of_days = days
                number_of_hours = hours
            else:
                number_of_days = 0
                number_of_hours = 0
            if request_unit_hours or request_unit_half:
                number_of_hours_text = '%s%g %s%s' % (
                    '' if request_unit_half or request_unit_hours else '(',
                    float_round(number_of_hours, precision_digits=2),
                    _('Hours'),
                    '' if request_unit_half or request_unit_hours else ')')
                print(number_of_hours_text)
            else:
                number_of_hours_text = ''

        date_data = {
            'date_from': date_from,
            'date_from_disp': date_from.astimezone(
                timezone(request.env.user.tz)).replace(tzinfo=None),
            'date_to': date_to,
            'date_to_disp': date_to.astimezone(
                timezone(request.env.user.tz)).replace(tzinfo=None),
            'number_of_days': number_of_days,
            'number_of_hours': number_of_hours,
            'number_of_hours_text': number_of_hours_text,
        }
        return date_data

    @http.route('/leave_requests/create_request', type='http', auth='user',
                website=True)
    def create_leave_request(self, **kwargs):
        employee_id = request.env['hr.employee'].sudo().search(
            [('user_id.id', '=', request.uid)]).id or \
                      request.env['hr.employee'].sudo().search(
                          [('address_home_id', '=',
                            request.env['res.users'].sudo().search(
                                [('id', '=', request.uid)]).partner_id.id)]).id
        if employee_id:
            values = {
                'holiday_status_id': int(kwargs.get('holiday_status_id')),
                'number_of_days': float(kwargs.get('number_of_days')),
                'employee_id': employee_id,
            }
            kwargs.update(values)
            kwargs.pop('number_of_days')
            print(kwargs)
            # request.env['hr.leave'].sudo().create(kwargs)
        return request.redirect('/leave_requests/')

    @http.route(
        ['/leave_requests/delete_request/<model("hr.leave"):leave_record>'],
        type='http', auth='user', website=True)
    def delete_leave_request(self, leave_record):
        if leave_record.state == 'confirm':
            print("deleting...")
            # request.env['hr.leave'].sudo().search(
            #     [('id', '=', leave_record.id)]).unlink()
        else:
            print("error...")
        return request.redirect('/leave_requests')
