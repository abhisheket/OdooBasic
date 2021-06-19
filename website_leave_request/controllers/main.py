# -*- coding: utf-8 -*-

import math

from collections import namedtuple

from datetime import datetime
from pytz import timezone, UTC

from odoo import http
from odoo.http import request
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY


class LeaveRequest(http.Controller):

    @http.route('/leave_requests', type='http', auth='user', website=True)
    def load_leave_request(self):
        leave_records = request.env['hr.leave'].sudo().search(
            [('user_id.id', '=', request.uid)])
        # print(request.env['hr.employee'].sudo().search(
        #     [('user_id', '=', request.uid)]).address_id)
        # print(request.env['res.users'].sudo().search(
        #     [('id', '=', request.uid)]).partner_id)
        # print(request.env['hr.employee'].sudo().search(
        #     [('address_home_id', '=', request.env['res.users'].sudo().search(
        #         [('id', '=', request.uid)]).partner_id.id)]))
        # employee_id = request.env['hr.employee'].sudo().search(
        #     [('address_home_id', '=', request.env['res.users'].sudo().search(
        #         [('id', '=', request.uid)]).partner_id.id)]).id
        # leave_records = request.env['hr.leave'].sudo().search(
        #     [('employee_id', '=', employee_id)])
        # if employee_id:
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
    def compute_date_from_to(self, **kwargs):
        print(kwargs)
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
        request_unit_half = kwargs.get('request_unit_half')
        request_unit_hours = kwargs.get('request_unit_hours')
        request_unit_custom = kwargs.get('request_unit_custom')
        employee_id = request.env['hr.employee'].sudo().search(
                    [('user_id.id', '=', request.uid)])

        if not request_date_from:
            date_from = False
        elif not request_unit_half and not request_unit_hours and not request_date_to:
            date_to = False
        else:
            if request_unit_half or request_unit_hours:
                request_date_to = request_date_from
            resource_calendar_id = employee_id.resource_calendar_id or request.env.company.resource_calendar_id
            print('resource_calendar_id', resource_calendar_id)
            domain = [('calendar_id', '=', resource_calendar_id.id),
                      ('display_type', '=', False)]
            attendances = request.env[
                'resource.calendar.attendance'].read_group(domain, [
                'ids:array_agg(id)', 'hour_from:min(hour_from)',
                'hour_to:max(hour_to)', 'week_type', 'dayofweek',
                'day_period'], ['week_type', 'dayofweek', 'day_period'],
                                                           lazy=False)
            print('attendances', attendances)

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
                print('start_week_type', start_week_type)
                attendance_actual_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) == start_week_type]
                print('attendance_actual_week', attendance_actual_week)
                attendance_actual_next_week = [
                    att for att in attendances if
                    att.week_type is False or int(
                        att.week_type) != start_week_type]
                print('attendance_actual_next_week', attendance_actual_next_week)
                # First, add days of actual week coming after date_from
                attendance_filtred = [
                    att for att in attendance_actual_week if int(
                        att.dayofweek) >= request_date_from.weekday()]
                print('attendance_filtred', attendance_filtred)
                # Second, add days of the other type of week
                attendance_filtred += list(attendance_actual_next_week)
                print('attendance_filtred', attendance_filtred)
                # Third, add days of actual week (to consider days that we have
                # remove first because they coming before date_from)
                attendance_filtred += list(attendance_actual_week)
                print('attendance_filtred', attendance_filtred)

                end_week_type = int(math.floor(
                    (request_date_to.toordinal() - 1) / 7) % 2)
                print('end_week_type', end_week_type)
                attendance_actual_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) == end_week_type]
                print('attendance_actual_week', attendance_actual_week)
                attendance_actual_next_week = [
                    att for att in attendances if att.week_type is False or int(
                        att.week_type) != end_week_type]
                print('attendance_actual_next_week', attendance_actual_next_week)
                attendance_filtred_reversed = list(reversed(
                    [att for att in attendance_actual_week if
                     int(att.dayofweek) <= request_date_to.weekday()]))
                print('attendance_filtred_reversed', attendance_filtred_reversed)
                attendance_filtred_reversed += list(
                    reversed(attendance_actual_next_week))
                print('attendance_filtred_reversed', attendance_filtred_reversed)
                attendance_filtred_reversed += list(
                    reversed(attendance_actual_week))
                print('attendance_filtred_reversed', attendance_filtred_reversed)

                # find first attendance coming after first_day
                attendance_from = attendance_filtred[0]
                print('attendance_from', attendance_from)
                # find last attendance coming before last_day
                attendance_to = attendance_filtred_reversed[0]
                print('attendance_to', attendance_to)
            else:
                # find first attendance coming after first_day
                attendance_from = next(
                    (att for att in attendances if int(
                        att.dayofweek) >= request_date_from.weekday()),
                    attendances[0] if attendances else default_value)
                print('attendance_from', attendance_from)
                # find last attendance coming before last_day
                attendance_to = next(
                    (att for att in reversed(attendances) if
                     int(att.dayofweek) <= request_date_to.weekday()),
                    attendances[-1] if attendances else default_value)
                print('attendance_to', attendance_to)

            compensated_request_date_from = request_date_from
            print('compensated_request_date_from', compensated_request_date_from)
            compensated_request_date_to = request_date_to
            print('compensated_request_date_to', compensated_request_date_to)

            if request_unit_half:
                print('request_unit_half', request_unit_half)
                if request_date_from_period == 'am':
                    hour_from = float_to_time(attendance_from.hour_from)
                    hour_to = float_to_time(attendance_from.hour_to)
                    print('am', hour_from, hour_to)
                else:
                    hour_from = float_to_time(attendance_to.hour_from)
                    hour_to = float_to_time(attendance_to.hour_to)
                    print('pm', hour_from, hour_to)
            elif request_unit_hours:
                hour_from = float_to_time(float(request_hour_from))
                hour_to = float_to_time(float(request_hour_to))
                print('request_unit_hours', hour_from, hour_to)
            elif request_unit_custom:
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
                print('request_unit_custom', hour_from, hour_to)
                compensated_request_date_from = self._adjust_date_based_on_tz(
                    request_date_from, hour_from)
                print('compensated_request_date_from', compensated_request_date_from)
                compensated_request_date_to = self._adjust_date_based_on_tz(
                    request_date_to, hour_to)
                print('compensated_request_date_to', compensated_request_date_to)
            else:
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
                print('else', hour_from, hour_to)

            date_from = timezone(request.env.user.tz).localize(
                datetime.combine(compensated_request_date_from,
                                 hour_from)).astimezone(UTC).replace(
                tzinfo=None)
            print('date_from', date_from)
            date_to = timezone(request.env.user.tz).localize(
                datetime.combine(compensated_request_date_to,
                                 hour_to)).astimezone(UTC).replace(tzinfo=None)
            print('date_to', date_to)
        date_data = {
            'request_date_from_period': request_date_from_period,
            'request_hour_from': request_hour_from,
            'request_hour_to': request_hour_to,
            'request_date_from': request_date_from,
            'request_unit_half': request_unit_half,
            'request_unit_hours': request_unit_hours,
            'request_unit_custom': request_unit_custom,
            'request_date_to': request_date_to,
            'date_from': date_from,
            'date_from_disp': date_from.astimezone(
                timezone(request.env.user.tz)).replace(tzinfo=None),
            'date_to': date_to,
            'date_to_disp': date_to.astimezone(
                timezone(request.env.user.tz)).replace(tzinfo=None),
        }
        print(date_data)
        return date_data

    @http.route('/leave_requests/create_request', type='http', auth='user',
                website=True)
    def create_leave_request(self, **kwargs):
        employee_id = request.env['hr.employee'].sudo().search(
            [('user_id.id', '=', request.uid)]).id
        # employee_id = request.env['hr.employee'].sudo().search(
        #     [('address_id', '=', request.env['res.users'].sudo().search(
        #         [('id', '=', request.uid)]).partner_id.id)]).id
        # employee_id = request.env['hr.employee'].sudo().search(
        #     [('address_home_id', '=', request.env['res.users'].sudo().search(
        #         [('id', '=', request.uid)]).partner_id.id)]).id
        if employee_id:
            values = {
                'holiday_status_id': int(kwargs.get('holiday_status_id')),
                # 'number_of_days': float(kwargs.get('number_of_days')),
                'employee_id': employee_id,
            }
            kwargs.update(values)
            print(kwargs)
            kwargs.pop('number_of_days')
            print(kwargs)
            request.env['hr.leave'].sudo().create(kwargs)
        return request.redirect('/leave_requests/')

    @http.route(
        ['/leave_requests/delete_request/<model("hr.leave"):leave_record>'],
        type='http', auth='user', website=True)
    def delete_leave_request(self, leave_record):
        request.env['hr.leave'].sudo().search(
            [('id', '=', leave_record.id)]).unlink()
        return request.redirect('/leave_requests')
