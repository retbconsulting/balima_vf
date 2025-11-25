# -*- encoding: utf-8 -*-

{
    'name': 'HR CIMR',
    # 'version': '19.0',
    'category': 'hr',
    'description': "Le système de Télédéclaration et de Télépaiement de la CIMR",
    'author': 'R&B Consulting',
    'website': 'http://www.ak.ma',
    'depends': ["base","hr_payroll_ma"],
    'init_xml': [
    ],
    'data': [
               'security/ir.model.access.csv',
               'views/hr_cimr_view.xml'  
    ],
    'demo_xml': [
    ],
    'test': [
             ],
    'installable': True,
    'active': False,
}