# -*- coding: utf-8 -*-

import hmac
import hashlib
import logging
from datetime import datetime
from werkzeug import urls

from odoo import api, fields, models
from odoo.http import request


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

    @api.model
    def _get_zaakpay_urls(self, environment):
        print("Get URL")
        """ Zaakpay URLs"""
        if environment == 'prod':
            return {'zaakpay_form_url': '/shop/payment/zaakpay'}
        else:
            return {'zaakpay_form_url': '/shop/payment/zaakpay'}

    def zaakpay_form_generate_values(self, values):
        print("loading...............")
        print(values)
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        zaakpay_values = dict(
            merchantIdentifier=self.zaakpay_merchant_id,
            orderId=values.get('reference'),
            returnUrl=urls.url_join(base_url, 'shop/payment/zaakpay/return/'),
            buyerEmail=values.get('partner_email'),
            buyerFirstName=values.get('partner_first_name'),
            buyerLastName=values.get('partner_last_name'),
            buyerAddress=values.get('partner_address'),
            buyerCity=values.get('partner_city'),
            buyerState=values.get('partner_state').name,
            buyerPincode=values.get('partner_zip'),
            buyerPhoneNumber=values.get('partner_phone'),
            txnType=1,
            zpPayOption=1,
            mode=0,
            currency=values.get('currency').name,
            amount=int(float(values['amount']) * 100),
            merchantIpAddress=str(request.httprequest.remote_addr),
            txnDate=datetime.today().strftime('%Y-%m-%d'),
            purpose=0 if self.env['product.template'].type == 'service' else 1,
            productDescription='New order',
            # debitorcredit='credit',
        )
        zaakpay_values['checksum'] = self.generate_checksum(
            zaakpay_values, self.zaakpay_secret_key)
        print(zaakpay_values)
        return zaakpay_values

    def zaakpay_get_form_action_url(self):
        print("Action URL")
        self.ensure_one()
        # environment = 'prod' if self.state == 'enabled' else 'test'
        # return self._get_zaakpay_urls(environment)['zaakpay_form_url']
        return urls.url_join(self.get_base_url(), '/shop/payment/zaakpay')

    def generate_checksum(self, param_dict, secret_key):
        checksum_string = ''
        for key, value in param_dict.items():
            if value:
                if checksum_string:
                    checksum_string += '&'
                checksum_string += key + "=" + str(value)
        print('checksum_string', checksum_string)
        checksum = hmac.new(bytes(secret_key, 'latin-1'),
                            msg=bytes(checksum_string, 'latin-1'),
                            digestmod=hashlib.sha256).hexdigest()
        print('checksum', checksum)
        return checksum
