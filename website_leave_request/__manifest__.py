# -*- coding: utf-8 -*-

{
    'name': 'Leave Request',
    'version': '14.0.0.0.0',
    'category': 'Website/Website',
    'summary': 'Manage leave request from website',
    'description': """
    Portal user can able to create leave request from the website. User can able
    to see the status of request from the website and also able to delete
    requests 
    """,
    'depends': ['website', 'hr_holidays'],
    'data': [
        'data/leave_request_data.xml',
        'views/website_leave_request_templates.xml',
        'views/assets.xml',
    ],
    'installable': True,
    'auto_install': False,
}
