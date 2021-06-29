# -*- coding: utf-8 -*-

import datetime
from werkzeug import urls

from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

import logging

_logger = logging.getLogger(__name__)


class AcquirerZaakpay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('zaakpay', 'Zaakpay')],
                                ondelete={'zaakpay': 'set default'})
    zaakpay_merchant_id = fields.Char(
        'Merchant ID', required_if_provider='zaakpay',
        groups='base.group_user', help='Merchant Identifier')
    zaakpay_secret_key = fields.Char(
        'Secret Key', required_if_provider='zaakpay', groups='base.group_user')

    def _get_zaakpay_urls(self, environment):
        """ Zaakpay URLs"""
        print(environment, "URLs")
        if environment == 'prod':
            return {'zaakpay_form_url': 'https://api.zaakpay.com/transactU?v=8'}
        else:
            return {
                'zaakpay_form_url': 'https://sandbox.zaakpay.com/transactU?v=8'
            }

    def paytm_form_generate_values(self, values):
        console.log("logging", request.httprequest.environ['REMOTE_ADDR'])
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        now = datetime.now()
        zaakpay_values = dict(
            merchantIdentifier = self.zaakpay_merchant_id,
            orderId = values.get('reference'),
            returnUrl = urls.url_join(base_url, '/payment/zaakpay/return/'),
            buyerEmail = values.get('partner_email'),
            buyerFirstName = values.get('partner_first_name'),
            buyerLastName = values.get('partner_last_name'),
            buyerAddress = values.get('partner_address'),
            buyerCity = values.get('partner_city'),
            buyerState = values.get('partner_state').name,
            buyerPincode = values.get('partner_zip'),
            buyerPhoneNumber = values.get('partner_phone'),
            txnType = 11,
            zpPayOption = 1,
            mode = 1,
            currency = values.get('currency').name,
            amount = float(values['amount']) * 100,
            merchantIpAddress = ,
            txnDate = datetime. today().strftime('%Y-%m-%d'),
            purpose = 0 if self.env['product.template'].type == 'service' else 1,
            productDescription = 'New order',
            debitorcredit = 'credit',
        )
        zaakpay_values['reqHashKey'] = self.generate_checksum(zaakpay_values, self.zaakpay_secret_key)
        return zaakpay_values

    def zaakpay_get_form_action_url(self):
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_zaakpay_urls(environment)
