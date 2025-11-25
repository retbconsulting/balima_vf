# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Gestion des avances sur salaires & des prêts',
    # "version": "19.0",
    'category': 'HR',
    'complexity': "normal",
    'description': """
    Gestion des avances sur salaires & des prêts
""",
    'author': 'R&B Consulting',
    'website': 'http://www.ak.ma',
    'images': [],
    'depends': ['hr_payroll_ma'],
    'data': [
        'views/hr_avance_salaire_view.xml',
        'views/hr_payroll_pret_logement_view.xml',
    ],
    'demo': [
        '',
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}