# -*- coding: utf-8 -*-

{
    'name': 'Hotel Management',
    'version': '14.0.0.0.0',
    'category': 'Test',
    'summary': """
        This module can be used to manage rooms & accommodation of hotel
    """,
    'description': """
        Hotel management module can be used to manage:
            - Room
            - Accommodation
            - Food
    """,
    'author': "Abhishek E T",
    'website': "http://allwebpages-com.stackstaging.com/",
    'depends': ['account', 'base', 'mail', 'uom'],
    'license': 'LGPL-3',
    'data': [
        'security/hotel_management_groups.xml',
        'security/ir.model.access.csv',
        'data/hotel_management_data.xml',
        'views/action_manager.xml',
        'views/hotel_management_views.xml',
        'views/hotel_order_food_views.xml',
        'views/hotel_rooms_views.xml',
        'report/hotel_management_reports.xml',
        'report/hotel_management_templates.xml',
        'wizard/filter_hotel_report_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

