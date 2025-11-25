# -*- encoding: utf-8 -*-

{
    'name': 'HR mutuelle',
    # 'version': '19.0',
    'category': 'hr',
    'description': "Le système de Télédéclaration et de Télépaiement de la Mutuelle",
    'author': 'R&B Consulting',
    'website': 'http://www.r-bconsulting.com',
    'depends': ["base","hr_payroll_ma"],
    'init_xml': [
    ],
    'update_xml': [
               'security/ir.model.access.csv',
               'views/hr_mutuelle_view.xml'
    ],
    'demo_xml': [
    ],
    'test': [
             ],
    'installable': True,
    'active': False,
}