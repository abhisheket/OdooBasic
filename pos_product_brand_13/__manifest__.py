# -*- coding: utf-8 -*-

{
    'name': 'pos_product_brand_13',
    'version': '13.0.0.0.0',
    'category': 'Sales/Point of Sale',
    'summary': 'Product Brand in Order Line and Receipt in PoS',
    'description': """
    A new field brand in product page which will be available in the order line
    and receipt in the Point of Sale
    """,
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/point_of_sale_assets.xml',
        'views/product_template_views.xml',
    ],
    'qweb': [
        'static/src/xml/order_line.xml',
        # 'static/src/xml/receipt_line.xml',
    ],
    'installable': True,
    'auto_install': False,
}
