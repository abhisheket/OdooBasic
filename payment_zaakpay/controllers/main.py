# -*- coding: utf-8 -*-

import logging
import pprint
import requests
import werkzeug

from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class ZaakpayController(http.Controller):
    _return_url = '/payment/zaakpay/return'

    # @http.route(['/shop/payment'], type='http', auth='none',
    #             method='POST', csrf=None, website=True)
    # def zaakpay_checkout(self):
    #
    #     url = 'https://sandbox.zaakpay.com/transactU?v=8' + \
    #           '&merchantIdentifier=' + post.get('merchantIdentifier') + \
    #           '&amount=' + post.get('amount') + \
    #           '&orderId=' + post.get('orderId') + '&mode=' +\
    #           post.get('mode') + '&checksum=' + post.get('checksum')
    #     print(url)
        # headers = {
        #     'merchantIdentifier': post.get('merchantIdentifier'),
        #     'orderId': post.get('orderId'),
        #     'mode': post.get('mode'),
        #     'checksum': post.get('checksum'),
        # }
        # response = requests.post(url)
        # print("Response", response)

    @http.route(['/payment/zaakpay/return'], type='http', auth='public',
                methods=['POST', 'GET'], csrf=False)
    def zaakpay_return(self, **post):
        """ Zaakpay return """
        _logger.info('Beginning Zaakpay form_feedback with post data %s',
                     pprint.pformat(post))  # debug
        # try:
        #     # res = self.zaakpay_validate_data(**post)
        # except ValidationError:
        #     _logger.exception('Unable to validate the Paypal payment')
        # return werkzeug.utils.redirect('/payment/process')
        print("Hai")
