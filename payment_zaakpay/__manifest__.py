# -*- coding: utf-8 -*-

{
    'name': 'Zaakpay Payment Acquirer',
    'category': 'Accounting/Payment Acquirers',
    'sequence': 505,
    'summary': 'Payment Acquirer: Zaakpay Implementation',
    'version': '14.0.0.0.0',
    'description': """Zaakpay Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_views.xml',
        'views/payment_zaakpay_templates.xml',
        'data/payment_acquirer_data.xml',
    ],
    'application': True,
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'uninstall_hook': 'uninstall_hook',
}
