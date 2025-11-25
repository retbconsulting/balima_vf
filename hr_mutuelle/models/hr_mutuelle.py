# -*- encoding: utf-8 -*-

from odoo import fields, models, api
from datetime import datetime, timedelta
import base64
import xlwt
from io import StringIO,BytesIO

class HrMutuelle(models.Model):
    
    _name = "hr.mutuelle"

    name = fields.Char(u'Numéro', readonly = True)
    regime = fields.Selection([('mensuelle', 'Mensuelle'),('trimestrielle', 'Trimestrielle')], string='Régime', required=True)
    company_ids = fields.Many2many(comodel_name='res.company', string='Sociétés', required=True)
    annee = fields.Selection([(str(num), str(num)) for num in range(1900, (datetime.now().year)+1 )], string='Année', required=True)
    trimestre = fields.Selection([('1','1er trimestre'),('2',u'2ème trimestre'),('3','3ème trimestre'),('4','4ème trimestre')], string='Trimestre')
    period_id = fields.Many2one(comodel_name='date.range', string='Période')
    output = fields.Binary(u'Fichier pré établi', readonly=True)
    output_name = fields.Char('File name')
    hr_payroll_ma_ids = fields.One2many(comodel_name='hr.payroll_ma', inverse_name='hr_mutuelle_id', string='Saisies mensuelles')
    state = fields.Selection([('draft', 'Brouillon'),
                        ('in_progress', 'En cours'),('generated', 'Fichier Générée'),('deposed', 'Déposée'),('canceled', 'Annulée')], string='Etat', default='draft')
    
    def validate(self):
        for record in self:
            payroll_obj = self.env['hr.payroll_ma']
            if record.regime:
                if record.regime == 'trimestrielle':
                    mois = []
                    if record.trimestre == '1':
                        mois = ['01/'+str(record.annee),'02/'+str(record.annee),'03/'+str(record.annee)]
                    elif record.trimestre == '2':
                        mois = ['04/'+str(record.annee),'05/'+str(record.annee),'06/'+str(record.annee)]
                    elif record.trimestre == '3':
                        mois = ['07/'+str(record.annee),'08/'+str(record.annee),'09/'+str(record.annee)]
                    elif record.trimestre == '4':
                        mois = ['10/'+str(record.annee),'11/'+str(record.annee),'12/'+str(record.annee)]
                else:
                    mois = [record.period_id.name]
                print (mois)
                payrolls = payroll_obj.search([('period_id.name','in',mois), ('company_id','in',record.company_ids.ids)])
                for payroll in payrolls:
                    payroll.update({'hr_mutuelle_id': record.id})
            record.state = 'in_progress'
                    
    def generate_file(self):
        for record in self:
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
            
            filename = 'mutuelle.xls'
            workbook = xlwt.Workbook(encoding="UTF-8")
            worksheet = workbook.add_sheet('Mutuelle')
            worksheet.write(0,0,'Matr.',cell_style_header_tab)
            worksheet.write(0,1,'Nom - prénom',cell_style_header_tab)
            worksheet.write(0,2,'Base de cotisation',cell_style_header_tab)
            worksheet.write(0,3,'Décès accidentel Employee',cell_style_header_tab)
            worksheet.write(0,4,'Décès accidentel Employeur',cell_style_header_tab)
            
            worksheet.write(0,5,'Mutuelle incapacité Employee',cell_style_header_tab)
            worksheet.write(0,6,'Mutuelle incapacité Employeur',cell_style_header_tab)
            
            worksheet.write(0,7,'Mutuelle Maladie et Maternité Employee',cell_style_header_tab)
            worksheet.write(0,8,'Mutuelle Maladie et Maternité Employeur',cell_style_header_tab)
            
            worksheet.write(0,9,'Mutuelle décès Employee',cell_style_header_tab)
            worksheet.write(0,10,'Mutuelle décès Employeur',cell_style_header_tab)
            
            row = 1
            total_base = 0
            total_m_d_a = 0
            total_m_d_a_p = 0
            total_m_i = 0
            total_m_i_p = 0
            total_m_m_m = 0
            total_m_m_m_p = 0
            total_m_d = 0
            total_m_d_p = 0
            
            for employee in record.mapped('hr_payroll_ma_ids').mapped('bulletin_line_ids').mapped('employee_id'):
                matricule = employee.matricule
                worksheet.write(row,0,matricule,cell_style_body_tab)
                name = employee.display_name
                worksheet.write(row,1,name,cell_style_body_tab)
                employee_salary_lines = record.mapped('hr_payroll_ma_ids').mapped('bulletin_line_ids').filtered(lambda r:r.employee_id.id == employee.id).mapped('salary_line_ids')
                base = sum(line.base for line in employee_salary_lines.filtered(lambda r:r.name in ['Mutuelle Maladie et Maternité', 'MUTUELLE', 'Mutuelle']))
                worksheet.write(row,2,base,cell_style_body_tab)
                total_base += base
                
                m_d_a = sum(line.subtotal_employee for line in employee_salary_lines.filtered(lambda r:r.name in ['Décès accidentel', 'DECES ACCIDENTEL']))
                worksheet.write(row,3,m_d_a,cell_style_body_tab)
                total_m_d_a += m_d_a
                
                m_d_a_p = sum(line.subtotal_employer for line in employee_salary_lines.filtered(lambda r:r.name in ['Décès accidentel', 'DECES ACCIDENTEL']))
                worksheet.write(row,4,m_d_a_p,cell_style_body_tab)
                total_m_d_a_p += m_d_a_p
                
                m_i = sum(line.subtotal_employee for line in employee_salary_lines.filtered(lambda r:r.name in ['Mutuelle incapacité', 'MUTUELLE INCAPACITÉ']))
                worksheet.write(row,5,m_i,cell_style_body_tab)
                total_m_i += m_i
                
                m_i_p = sum(line.subtotal_employer for line in employee_salary_lines.filtered(lambda r:r.name in ['Mutuelle incapacité', 'MUTUELLE INCAPACITÉ']))
                worksheet.write(row,6,m_i_p,cell_style_body_tab)
                total_m_i_p += m_i_p
                
                m_m_m = sum(line.subtotal_employee for line in employee_salary_lines.filtered(lambda r:r.name in ['Mutuelle Maladie et Maternité', 'MUTUELLE', 'Mutuelle']))
                worksheet.write(row,7,m_m_m,cell_style_body_tab)
                total_m_m_m += m_m_m
                
                m_m_m_p = sum(line.subtotal_employer for line in employee_salary_lines.filtered(lambda r:r.name in ['Mutuelle Maladie et Maternité', 'MUTUELLE', 'Mutuelle']))
                worksheet.write(row,8,m_m_m_p,cell_style_body_tab)
                total_m_m_m_p += m_m_m_p
                
                m_d = sum(line.subtotal_employee for line in employee_salary_lines.filtered(lambda r:r.name in ['Mutuelle décès', 'MUTUELLE DECES']))
                worksheet.write(row,9,m_d,cell_style_body_tab)
                total_m_d += m_d
                
                m_d_p = sum(line.subtotal_employer for line in employee_salary_lines.filtered(lambda r:r.name in ['Mutuelle décès', 'MUTUELLE DECES']))
                worksheet.write(row,10,m_d_p,cell_style_body_tab)
                total_m_d_p += m_d_p
                
                row += 1
            worksheet.write(row,0,'TOTAL',cell_style_header_tab)
            worksheet.write(row,1,'-',cell_style_header_tab)
            worksheet.write(row,2,total_base,cell_style_header_tab)
            worksheet.write(row,3,total_m_d_a,cell_style_header_tab)
            worksheet.write(row,4,total_m_d_a_p,cell_style_header_tab)
            worksheet.write(row,5,total_m_i,cell_style_header_tab)
            worksheet.write(row,6,total_m_i_p,cell_style_header_tab)
            worksheet.write(row,7,total_m_m_m,cell_style_header_tab)
            worksheet.write(row,8,total_m_m_m_p,cell_style_header_tab)
            worksheet.write(row,9,total_m_d,cell_style_header_tab)
            worksheet.write(row,10,total_m_d_p,cell_style_header_tab)
            
            fp = BytesIO()
            workbook.save(fp)
            record.output = base64.encodestring(fp.getvalue())
            record.output_name = filename

    def depose(self):
        self.write({
                    'state': 'deposed',
                    })
    
    def cancel(self):
        self.write({
                    'state': 'canceled',
                    })