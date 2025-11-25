# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import datetime, timedelta
import base64
from odoo.exceptions import ValidationError

class HrCimr(models.Model):
    
    _name = "hr.cimr"

    name = fields.Char(u'Numéro', readonly = True)
    regime = fields.Selection([('mensuelle', 'Mensuelle'),('trimestrielle', 'Trimestrielle')], string='Régime', required=True)
    company_ids = fields.Many2many(comodel_name='res.company', string='Sociétés', required=True)
    annee = fields.Selection([(str(num), str(num)) for num in range(1900, (datetime.now().year)+1 )], string='Année', required=True)
    trimestre = fields.Selection([('1','1er trimestre'),('2',u'2ème trimestre'),('3','3ème trimestre'),('4','4ème trimestre')], string='Trimestre')
    period_id = fields.Many2one(comodel_name='date.range', string='Période')
    output = fields.Binary(u'Fichier pré établi', readonly=True)
    output_name = fields.Char('File name')
    hr_payroll_ma_ids = fields.One2many(comodel_name='hr.payroll_ma', inverse_name='hr_cimr_id', string='Saisies mensuelles')
    state = fields.Selection([('draft', 'Brouillon'),
                        ('in_progress', 'En cours'),('generated', 'EDI Générée'),('deposed', 'Déposée'),('canceled', 'Annulée')], string='Etat', default='draft')
    
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
                    payroll.update({'hr_cimr_id': record.id})
            record.state = 'in_progress'
                    
    def generate_edi(self):
        for record in self:
            content = ''
            employee_obj = self.env['hr.employee']
            bulletin_obj = self.env['hr.payroll_ma.bulletin']
            for employee in self.mapped('hr_payroll_ma_ids').mapped('bulletin_line_ids').mapped('employee_id').filtered(lambda r: r.cimr_number):
                employee_line = ''
                if employee.contract_id.date_end:
                    employee_line += '7'
                else:
                    employee_line += '2'
                if employee.company_id.name in ['CMN', 'RBA']: 
                    employee_line += '005839'
                elif employee.company_id.name == 'RAK':
                    employee_line += '005440'
                elif employee.company_id.name == 'AGA':
                    employee_line += '005840'
                else:
                    employee_line += '000000'
                
                '''numero_categorie_cimr = employee.numero_categorie_cimr if employee.numero_categorie_cimr else ''
                employee_line += numero_categorie_cimr.ljust(2)'''
                taux_cimr = employee.mapped('contract_id').mapped('cotisation').mapped('cotisation_ids').filtered(lambda r:r.code in ['CIMR', 'CIMR 3%', 'Cimr 3%']).tauxsalarial
                if taux_cimr == 3.00:
                    employee_line += '02'
                
                elif taux_cimr == 7.00:
                    employee_line += '01'
                
                else:
                    employee_line += ''.ljust(2)
                
                cimr_number = employee.cimr_number
                employee_line += cimr_number.rjust(9, "0")
                
                taux_cimr = employee.mapped('contract_id').mapped('cotisation').mapped('cotisation_ids').filtered(lambda r:r.code in ['CIMR', 'Cimr', 'CIMR 3%', 'Cimr 3%', 'CIMR 4,5', 'Retenue CIMR', 'Retenue CIMR 3%']).tauxsalarial * 100
                taux_cimr = str(int(taux_cimr))
                taux_cimr = taux_cimr.rjust(4).replace(' ', '0')
                employee_line += taux_cimr
                
                display_name = employee.name
                display_name = display_name.replace('’', '')
                if (len(display_name) > 25):
                    display_name = display_name[0:25]
                
                employee_line += display_name.ljust(25)
                
                display_name = employee.prenom
                display_name = display_name.replace('’', '')
                if (len(display_name) > 25):
                    display_name = display_name[0:25]
                employee_line += display_name.ljust(25)
                
                
                matricule = employee.matricule
                employee_line += matricule.ljust(6)
                
                if employee.gender == 'male':
                    gender = 'M'
                elif employee.gender == 'female':
                    gender = 'F'
                else:
                    gender = ' '
                employee_line += gender
                
                if employee.country_id.code == 'MA':
                    nationality = 'M'
                else:
                    nationality = 'A'
                employee_line += nationality
                
                date_affiliation_cimr = ''
                if employee.date:
                    date = employee.date
                    date = date.strftime('%d%m%Y')
                employee_line += date.rjust(8)
                
                birthday = ''
                if employee.birthday:
                    birthday = employee.birthday
                    birthday = birthday.strftime('%d%m%Y')
                employee_line += birthday.rjust(8)
                
                if employee.marital == 'single':
                    marital = 'C'
                elif employee.marital == 'married':
                    marital = 'M'
                elif employee.marital == 'widower':
                    marital = 'V'
                elif employee.marital == 'divorced':
                    marital = 'D'
                else:
                    marital = ' ' 
                employee_line += marital
                
                employee_line += str(employee.children) if employee.children else '0'
                
                cimr_lines = self.mapped('hr_payroll_ma_ids').mapped('bulletin_line_ids').filtered(lambda r:r.employee_id.id == employee.id).mapped('salary_line_ids').filtered(lambda r:r.name in ["CIMR", "Retenue CIMR", "Cimr", "Cimr 3%"])
                base_cimr = sum(cimr_line.base for cimr_line in cimr_lines)
                base_cimr = "{:.2f}".format(base_cimr)
                base_cimr = base_cimr.replace('.', '')
                employee_line += base_cimr.rjust(10).replace(' ', '0')
                
                date_end = ''
                if employee.contract_id.date_end:
                    date_end = employee.contract_id.date_end
                    date_end = date_end.strftime('%d%m%Y')
                employee_line += date_end.rjust(8)
                
                cin = employee.identification_id
                employee_line += cin.ljust(10)
                
                ssnid = employee.ssnid
                if not ssnid:
                    raise ValidationError(_('Le numéro de CNSS est non renseigné pour le matricule %s')% (employee.name))
                
                employee_line += ssnid.ljust(10)
                
                phone = employee.phone_home
                if phone:
                    employee_line += phone.ljust(14)
                else:
                    employee_line += '00000000000000'
                
                email = employee.work_email if employee.work_email else ''
                employee_line += email.ljust(35)
                
                employee_line += record.trimestre
                employee_line += record.annee + '\r\n'
                
                content += employee_line
            
            record.output = base64.b64encode(content.encode())
            record.output_name = 'cimr_edi.txt'
            record.state = 'generated'

    def depose(self):
        self.write({
                    'state': 'deposed',
                    })
    
    def cancel(self):
        self.write({
                    'state': 'canceled',
                    })