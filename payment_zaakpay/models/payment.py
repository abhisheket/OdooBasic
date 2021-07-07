# -*- coding: utf-8 -*-

import hmac
import hashlib
import logging
from werkzeug import urls

from odoo import api, fields, models
from odoo.exceptions import ValidationError
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
    # zaakpay_encryption_key_id = fields.Char(
    #     'Encryption Key ID', required_if_provider='zaakpay',
    #     groups='base.group_user')
    # zaakpay_public_key = fields.Text(
    #     'Public Key', required_if_provider='zaakpay',
    #     groups='base.group_user')

    @api.model
    def _get_zaakpay_urls(self, environment):
        print("Get URL")
        """ Zaakpay URLs"""
        if environment == 'prod':
            return {'zaakpay_form_url': 'https://api.zaakpay.com/transactD?v=8'}
        else:
            return {
                'zaakpay_form_url': 'https://zaakstaging.zaakpay.com/api/paymentTransact/V8?'
            }

    def zaakpay_form_generate_values(self, values):
        print("loading...............")
        print(values)
        ip_address = str(request.httprequest.remote_addr)
        base_url = self.env['ir.config_parameter'].sudo().get_param(
            'web.base.url')
        url_with_ip = base_url.replace('localhost', ip_address)
        zaakpay_values = dict(
            amount=int(float(values['amount']) * 100),
            buyerEmail=values.get('partner_email'),
            currency=values.get('currency').name,
            merchantIdentifier=self.zaakpay_merchant_id,
            orderId=values.get('reference'),
            returnUrl=urls.url_join(
                url_with_ip, 'shop/payment/zaakpay/return'),
        )
        zaakpay_values['checksum'] = self.generate_checksum(
            zaakpay_values, self.zaakpay_secret_key)
        print(zaakpay_values)
        return zaakpay_values

    def zaakpay_get_form_action_url(self):
        print("Action URL")
        self.ensure_one()
        environment = 'prod' if self.state == 'enabled' else 'test'
        return self._get_zaakpay_urls(environment)['zaakpay_form_url']

    def generate_checksum(self, param_dict, secret_key):
        checksum_string = ''
        for key, value in param_dict.items():
            checksum_string += key + "=" + str(value) + '&'
        print('checksum_string', checksum_string)
        checksum = hmac.new(bytes(secret_key, 'utf-8'),
                            msg=bytes(checksum_string, 'utf-8'),
                            digestmod=hashlib.sha256).hexdigest()
        print('checksum', checksum)
        return checksum


class PaymentTransactionZaakpay(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _zaakpay_form_get_tx_from_data(self, data):
        print('_zaakpay_form_get_tx_from_data:  ', data)
        # reference = data.get('orderId')
        # if not reference:
        #     error_msg = _(
        #         'Zaakpay: received data with missing reference (%s)') % (
        #                     reference)
        #     _logger.info(error_msg)
        #     raise ValidationError(error_msg)
        #
        # txs = self.env['payment.transaction'].search(
        #     [('reference', '=', reference)])
        # if not txs or len(txs) > 1:
        #     error_msg = 'Paytm: received data for reference %s' % (
        #         reference)
        #     if not txs:
        #         error_msg += '; no order found'
        #     else:
        #         error_msg += '; multiple order found'
        #     _logger.info(error_msg)
        #     raise ValidationError(error_msg)
        # return txs[0]
