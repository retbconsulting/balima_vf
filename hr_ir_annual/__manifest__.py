# -*- coding: utf-8 -*-
{
    'name': 'Etat 9421',
    # "version": "19.0",
    "summary": "IR",
    "author": "R&B Consulting",
    "website": "https://www.r-bconsulting.com",
    "category": "Generic",
    'depends': [
        'base',
        'hr',
        'hr_holidays',
        'hr_payroll_ma'
    ],
    'data': [
        # Data
        'data/configuration_data.xml',
        # Wizards
        

        # Views
        'views/declaration_config_view.xml',
        'views/ir_declaration_view.xml',
        # Menu

        # Report
        

        # Security
        "security/ir.model.access.csv"
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'qweb': [],
}