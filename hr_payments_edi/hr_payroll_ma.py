# -*- encoding: utf-8 -*-

from odoo import fields, models
from datetime import date
import base64

class HrPayrollMa(models.Model):
    
    _inherit = "hr.payroll_ma"

    file_payment_edi = fields.Binary(string=u'Ordre de virement', readonly=True)
    file_name = fields.Char('Filename', size=256, readonly=True)
    
    def generate_payment_edi(self):
        today = date.today()
        today_str = today.strftime("%d-%m-%Y")
        filename= 'virement_' + today_str +'.txt'
        content = ''
        header = ''
        footer = ''
        for record in self:
            code_register = '03'
            header += code_register
            code_operation = '02'
            header += code_operation.ljust(18)
            code_remise = '1'
            header += code_remise.ljust(5)
            header += today.strftime("%d%m") + str(today.year)[-1]
            company = 'ATLAS SERVAIR'
            header += company.ljust(24)
            ref = 'P.' + record.period_id.name
            header += ref.ljust(32)
            company_bank = self.env['res.partner.bank'].search([('is_bank_for_payroll', '=', True),('company_id.name', '=', 'CMN')], limit=1)
            if company_bank:
                company_account = company_bank.acc_number
            header += company_account[6:22].ljust(17)
            header += '2'
            header += company.ljust(45)
            
            header += '00'
            header += company_account[0:6] + company_account[22:24]
            header += ' '
            content += header + '\n'
            for bulletin in record.bulletin_line_ids.filtered(lambda r:r.employee_id.mode_reglement == 'virement'):
                if bulletin.salaire_net_a_payer:
                    code_register = '06'
                    content += code_register
                    code_operation = '02'
                    content += code_operation.ljust(16)
                    matricule = bulletin.employee_id.matricule if bulletin.employee_id.matricule else ''
                    content += matricule.ljust(12)
                    full_name = bulletin.employee_id.name + ' ' + bulletin.employee_id.prenom
                    content += full_name.ljust(24)
                    bank = bulletin.employee_id.bank.name
                    content += bank.ljust(32)
                    compte = bulletin.employee_id.compte
                    content += compte[6:22].ljust(16)
                    salaire = "{:.2f}".format(bulletin.salaire_net_a_payer)
                    salaire = salaire.replace('.', '')
                    content += salaire.rjust(16).replace(' ', '0')
                    content += '00'.rjust(33)
                    content += compte[0:6] + compte[22:24]
                    content += ' '
                    content += '\n'
            code_register = '08'
            footer += code_register
            code_operation = '02'
            footer += code_operation.ljust(100)
            total = "{:.2f}".format(record.total_net_a_payer_vrt)
            total = total.replace('.', '')
            footer += total.rjust(16).replace(' ', '0')
            footer += ''.rjust(42)
            content += footer
        record.file_payment_edi = base64.encodestring(content.encode())
        record.file_name = filename
