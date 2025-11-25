# -*- encoding: utf-8 -*-

{
    'name': 'HR Damancom',
    # 'version': '19.0',
    'category': 'hr',
    'description': "Le système de Télédéclaration et de Télépaiement de la caisse Nationale de la sécurité Sociale",
    'author': 'R&B Consulting',
    'website': 'http://www.rb-consulting.com',
    'depends': ["base","hr_payroll_ma"],
    'init_xml': [
    ],
    'data': [
               'wizard/hr_damancom_wizard_view.xml',
               'security/ir.model.access.csv',
               'hr_damancom_view.xml'  
    ],
    'demo_xml': [
    ],
    'test': [
             ],
    'installable': True,
    'active': False,
}