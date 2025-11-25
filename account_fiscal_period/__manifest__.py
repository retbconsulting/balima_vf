# -*- coding: utf-8 -*-

{
    'name': 'Account Fiscal Period',
    # 'version': '19.0',
    'category': 'Accounting',
    'author': 'BHECOSERVICES',
    'website': 'http://www.bhecoservices.com',
    'depends': [
        'account_fiscal_year',
    ],
    'data': [
        'data/date_range_type.xml',
        'views/date_range_type.xml',
        'views/date_range.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': True,
}
