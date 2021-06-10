# -*- coding: utf-8 -*-

{
    'name': 'pos_discount_type',
    'version': '14.0.0.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Option to add discount in percentage or amount in PoS',
    'description': """
    A new radio button in PoS configuration to select discount in percentage or
    amount. A new button Discount open a text field. The value is taken based on
    the radio button and add discount to the order line and pay with the
    adjusted amount.
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/point_of_sale_assets.xml',
        'views/pos_config_views.xml',
    ],
    'qweb': [
        'static/src/xml/discount_button.xml',
        'static/src/xml/order_line.xml',
        # 'static/src/xml/receipt_line.xml',
    ],
    'installable': True,
    'auto_install': False,
}
