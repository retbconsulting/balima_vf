# -*- encoding: utf-8 -*-

{
    'name': 'HR Payments',
    # 'version': '19.0',
    'category': 'hr',
    'description': "Un module permettant d'intégrer les OV en format EDI",
    'author': 'R&B Consulting',
    'website': 'http://www.r-bconsulting.com',
    'depends': ["base","hr_payroll_ma"],
    'init_xml': [
    ],
    'update_xml': [
               'hr_payroll_ma_view.xml'  
    ],
    'demo_xml': [
    ],
    'test': [
             ],
    'installable': True,
    'active': False,
}