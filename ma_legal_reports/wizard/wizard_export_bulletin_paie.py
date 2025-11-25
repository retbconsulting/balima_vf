# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import base64
import logging
import xlwt
from io import StringIO,BytesIO
import os
import os.path
import urllib
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class WizardExportBulletinPaie(models.TransientModel):
    _name = 'wizard.export.bulletin.paie'
    _description = 'Export Journal de Paie'
    
    year = fields.Selection(selection=[(str(num), str(num)) for num in range(2020, (datetime.now().year)+1 )], string="Année", required=True)
    file_data = fields.Binary('Excel File', readonly=True, attachment=False)
    filename = fields.Char(string='Filename', size=256, readonly=True)



    # ------------------------------------------------------------------------
    # METHODS
    # ------------------------------------------------------------------------
    def get_all_rubriques(self, bulletins):
        sql='''
                    SELECT DISTINCT l.name, l.type
                    FROM hr_payroll_ma_bulletin_line l
                    where L.id_bulletin in %s
                    order by l.type
                    '''% (bulletins)
        return sql

    def button_confirm(self):
        employee = self.env['hr.employee'].browse(self._context.get('active_id'))
        _pfc = '26'  
        _bc = '28'
        xls_styles = {
            'xls_title': 'font: bold true, height 140;',
            'xls_title2': 'font: bold true, height 140;',
            'bold': 'font: bold true;',
            'underline': 'font: underline true;',
            'italic': 'font: italic true;',
            'fill': 'pattern: pattern solid, fore_color %s;' % _pfc,
            'fill_blue': 'pattern: pattern solid, fore_color 27;',
            'fill_grey': 'pattern: pattern solid, fore_color 22;',
            'borders_all': 'borders: left thin, right thin, top thin, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' % (_bc, _bc, _bc, _bc),
            'borders_all2': 'borders: left thin, right thin, top thick, bottom thin, '
                'left_colour %s, right_colour %s, top_colour %s, bottom_colour %s;' % (_bc, _bc, _bc, _bc),
            'left': 'align: horz left;',
            'center': 'align: horz center;',
            'right': 'align: horz right;',
            'wrap': 'align: wrap true;',
            'top': 'align: vert top;',
            'ver_top': 'align: vert center;',
            'bottom': 'align: vert bottom;',
        }
        cell_format = xls_styles['xls_title'] + xls_styles['borders_all'] + xls_styles['wrap'] + xls_styles['ver_top']
        cell_body_format = xls_styles['xls_title2'] +  xls_styles['ver_top']
        cell_style_header_tab = xlwt.easyxf(cell_format + xls_styles['bold']+ xls_styles['center'] + xls_styles['fill'])
        cell_style_body_tab = xlwt.easyxf(cell_body_format)
        date_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD')
        datetime_style = xlwt.easyxf('align: wrap yes', num_format_str='YYYY-MM-DD HH:mm:SS')
        filename= 'Fiche_Individuelle_' + employee.name + '_' + employee.prenom + '_' + self.year +'.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        worksheet= workbook.add_sheet(filename)
        worksheet.write(0,0,u'Libellé.',cell_style_header_tab)
        worksheet.write(0,1,'Janvier',cell_style_header_tab)
        worksheet.write(0,2,'Février',cell_style_header_tab)
        worksheet.write(0,3,'Mars',cell_style_header_tab)
        worksheet.write(0,4,'Avril',cell_style_header_tab)
        worksheet.write(0,5,'Mai',cell_style_header_tab)
        worksheet.write(0,6,'Juin',cell_style_header_tab)
        worksheet.write(0,7,'Juillet',cell_style_header_tab)
        worksheet.write(0,8,'Aout',cell_style_header_tab)
        worksheet.write(0,9,'Septembre',cell_style_header_tab)
        worksheet.write(0,10,'Octobre',cell_style_header_tab)
        worksheet.write(0,11,'Novembre',cell_style_header_tab)
        worksheet.write(0,12,'Décembre',cell_style_header_tab)
        
        periods = []
        for month in range(1,13,1):
            periods.append(str(month).rjust(2,'0') + "/" + str(self.year))
        periods_ids = self.env['date.range'].search([('name','in',periods), ('company_id','=',employee.company_id.id)])
        
        bulletins_ids = self.env['hr.payroll_ma.bulletin'].search([('employee_id', '=', employee.id), ('period_id', 'in', periods_ids.ids)])
        bulletin_ids_query = str(tuple(bulletins_ids.ids))
        if tuple(bulletins_ids.ids).__len__() == 1:
            bulletin_ids_query='('+str(bulletins_ids.ids[0])+')'
        self.env.cr.execute(self.get_all_rubriques(bulletin_ids_query))
        rubriques = self.env.cr.dictfetchall()
        row = 1
        for rubrique in rubriques:
            worksheet.write(row,0,rubrique['name'],cell_style_header_tab)
            column = 1
            for period in periods_ids:
                current_bulletin = bulletins_ids.filtered(lambda r: r.period_id.id == period.id)
                current_line = current_bulletin.mapped('salary_line_ids').filtered(lambda r: r.name == rubrique['name'])
                if current_bulletin and current_line:
                    worksheet.write(row,column,current_line.subtotal_employee,cell_style_body_tab)
                else:
                    worksheet.write(row,column,0,cell_style_body_tab)
                column += 1
            row += 1
        
        column = 1
        worksheet.write(row,0,"Net à payer",cell_style_header_tab)
        for period in periods_ids:
            current_bulletin = bulletins_ids.filtered(lambda r: r.period_id.id == period.id)
            if current_bulletin:
                worksheet.write(row,column,current_bulletin.salaire_net_a_payer,cell_style_body_tab)
            else:
                worksheet.write(row,column,0,cell_style_body_tab)
            column += 1
        fp = BytesIO()
        workbook.save(fp)
        self.write({
            'file_data': base64.encodestring(fp.getvalue()),
            'filename': filename,
        })
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=wizard.export.bulletin.paie&id=" + str(self.id) + "&filename_field=filename&field=file_data&download=true&filename=" + filename,
            'target': 'self',
        }