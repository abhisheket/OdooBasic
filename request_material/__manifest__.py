# -*- coding: utf-8 -*-

{
    'name': 'Material Request',
    'version': '14.0.0.0.0',
    'category': 'Test',
    'summary': """
        This module can be used to manage material requests of employees
    """,
    'description': """
        Employees can create material requests and submit to requisition 
        managers.
        They can request for multiple materials/Product.
        For each product in the request, there will be an option to select 
        whether the product can get by a purchase order or internal transfer.
        If it is a RFQ can be created for multiple vendors
        The request first need to get approved by requisition department manager 
        and then requisition Head.
        Only requisition Head can reject the request.
        Only requisition Users can create the request.
    """,
    'author': "Abhishek E T",
    'depends': ['base', 'hr', 'purchase', 'stock'],
    'license': 'LGPL-3',
    'data': [
        'security/request_material_groups.xml',
        'security/ir.model.access.csv',
        'data/request_material_data.xml',
        'views/request_material_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}