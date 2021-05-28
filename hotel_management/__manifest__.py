{
    'name': 'Hotel Management',
    'summary': """
        This module can be used to manage rooms & accommodation of
        hotel
    """,
    'description': """
        Hotel management module can be used to manage:
            - Room
            - Accommodation
            - Food
    """,

    'author': "Abhishek E T",

    'category': 'Test',
    'version': '14.0.1.2.0',

    'depends': ['account', 'base', 'mail', 'report_xlsx', 'uom'],
    'license': 'LGPL-3',

    'data': [
        'security/ir.model.access.csv',
        'security/hotel_management_security.xml',
        'data/sequence_data.xml',
        'views/hotel_rooms_views.xml',
        'views/hotel_accommodation_views.xml',
        'views/hotel_order_food_views.xml',
        'report/hotel_management_report_views.xml',
        'wizard/filter_hotel_report_views.xml',
    ],
}
