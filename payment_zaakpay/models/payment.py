# -*- coding: utf-8 -*-

from werkzeug import urls

from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

import logging

_logger = logging.getLogger(__name__)


class AcquirerZaakpay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('zaakpay', 'Zaakpay')],
                                ondelete={'zaakpay': 'set default'})
    zaakpay_merchant_identifier = fields.Char(
        'Merchant Identifier', required_if_provider='zaakpay',
        groups='base.group_user')
    zaakpay_secret_key = fields.Char(
        'Secret Key', required_if_provider='zaakpay', groups='base.group_user')

    def _get_zaakpay_urls(self, environment):
        """ Zaakpay URLs"""
        if environment == 'prod':
            return {'zaakpay_form_url': 'https://'}
        else:
            return {'zaakpay_form_url': 'https://'}
