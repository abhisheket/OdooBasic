# -*- coding: utf-8 -*-

import logging
import pprint
import werkzeug

from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError

_logger = logging.getLogger(__name__)


class ZaakpayController(http.Controller):
    _return_url = '/payment/zaakpay/return'

    @http.route(['/shop/payment/zaakpay/return'], type='http', auth='public',
                methods=['POST', 'GET'], csrf=False)
    def zaakpay_return(self, **post):
        """ Zaakpay return """
        _logger.info('Beginning Zaakpay form_feedback with post data %s',
                     pprint.pformat(post))  # debug
        print(post)
        # try:
        #     # res = self.zaakpay_validate_data(**post)
        # except ValidationError:
        #     _logger.exception('Unable to validate the Zaakpay payment')
        # return werkzeug.utils.redirect('/payment/process')
