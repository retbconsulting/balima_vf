# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions
import base64
import logging
import xlwt
from io import StringIO,BytesIO
import os
import os.path
import urllib

_logger = logging.getLogger(__name__)

class WizardExportJournalPaie(models.TransientModel):
    _name = 'wizard.export.journal.paie'
    _description = 'Export Journal de Paie'

    file_data = fields.Binary('Excel File', readonly=True, attachment=False)
    filename = fields.Char(string='Filename', size=256, readonly=True)



    # ------------------------------------------------------------------------
    # METHODS
    # ------------------------------------------------------------------------
    def get_all_rubriques(self):
        sql='''
                    SELECT l.name, l.type, sum(subtotal_employee) as total_subtotal_employee , sum(subtotal_employer) as total_subtotal_employer
                    FROM hr_payroll_ma_bulletin_line l
                    RIGHT JOIN hr_payroll_ma_bulletin b ON b.id = l.id_bulletin
                    LEFT JOIN hr_payroll_ma p ON p.id = b.id_payroll_ma 
                    where p.id = %s and l.name is not null
                    group by l.type, l.name  
                    order by l.type
                    '''% (self.env.context.get('active_id'))
        return sql

    def button_confirm(self):
        active_recs = self.env['hr.payroll_ma'].browse(self._context.get('active_ids'))
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
        filename= 'Journal De Paie.xls'
        workbook= xlwt.Workbook(encoding="UTF-8")
        worksheet= workbook.add_sheet('Journal De Paie.xls')
        worksheet.write(0,0,'Matr.',cell_style_header_tab)
        worksheet.write(0,1,'Nom - prénom',cell_style_header_tab)
        worksheet.write(0,2,'FONCTION',cell_style_header_tab)
        worksheet.write(0,3,'GRADE',cell_style_header_tab)
        worksheet.write(0,4,'SERVICE',cell_style_header_tab)
        worksheet.write(0,5,'Jours travaillés',cell_style_header_tab)
        worksheet.write(0,6,'Jours congés',cell_style_header_tab)
        worksheet.write(0,7,'Salaire de base',cell_style_header_tab)
        total_salaire_base = 0.0
        worksheet.write(0,8,'Salaire Brute',cell_style_header_tab)
        total_salaire_brute = 0.0
        worksheet.write(0,9,'Salaire brute imposable',cell_style_header_tab)
        total_salaire_imposable = 0.0
        worksheet.write(0,10,'Salaire Net Imposable',cell_style_header_tab)
        total_salaire_net_imposable = 0.0
        worksheet.write(0,11,'Salaire Net',cell_style_header_tab)
        total_salaire_net = 0.0
        worksheet.write(0,12,'Salaire Net à payer',cell_style_header_tab)
        total_salaire_net_payer = 0.0
        worksheet.write(0,13,'Frais professionnels',cell_style_header_tab)
        total_frais_professionnels = 0.0
        worksheet.write(0,14,'Cotisations employé',cell_style_header_tab)
        total_cotisations_employe = 0.0
        worksheet.write(0,15,'Cotisations employeur',cell_style_header_tab)
        total_cotisations_employeur = 0.0
        end_column = 16
        row = 1
        salary_dict_employee = {}
        salary_dict_employeur = {}
        list_rubriques_employee = []
        list_rubriques_employeur = []
        rubriques_employee = ['Retenue CNSS Employee', 'Rappel sur salaire AMO Employee', 'Prime de responsabilité Employee', 'Indemnité. de transport Employee',
                               'Prime diff individuelle Employee', 'Remboursement accident de travail Employee', 'Prime faisant fonction Employee', 
                               'Prime production VIP REV Employee', 'Impot sur le revenu Employee', 'Décès accidentel Employee', 
                               'Remboursement retenue COVID 19 Employee', 'Retenue CIMR Employee', 'Retenue remboursement accident de travail Employee',
                               'Indemnité de  logement Employee', 'Prime de panier Employee', 'C.O.S Employee', 'Mutuelle incapacité Employee', 
                               'Indemnité différentielle Employee', 'Cotisation MUPRAS Employee', 'Prime de caisse Employee', 'Prime anciennete Employee',
                               'Différentiel intérêt de logement Employee', 'Accident de travail Employee', 'Mutuelle Employee', 'Assurance maladie obligatoire Employee',
                               'Congé de naissance Employee', 'PER Employee', 'Retraite complémentaire RECORE Employee', 'Prime de représentation 1 Employee',
                               'Prime production VIP REV Employee', 'Prime de permanence Employee', 'Mutuelle décês Employee', 'Complément salaire MD/AT Employee',
                               'Prime de scolarité Employee', 'Bonus Employee', 'Retenue avantage en nature Employee', 'Prêt logement Employee', 
                               'Prime de représentation 2 Employee', 'Jours Congés rémunérés Employee', 'Heures de Nuit Employee', 'Jours férié Employee', 
                               'Salaire de base Employee', 'Arrondi Employee', 'Mutuelle Maladie et Maternité Employee', 'Retraite Complémentaire Employee'
                               'Jours fériés Employee', 'Acompte accident de travail Employee', 'Taxe de solidarité Employee', 'Frais de transport/Inventaire Employee',
                               'Prime départ retraite Employee', 'Rappel sur salaire Employee', 'Avance sur salaire Employee', 'Heures é déduire Employee', 
                               'Retraite  complémentaire RECORE Employee', 'Cotisation MUPRAS Employee', 'Retenue CIMR Employee'
                               ] 
        
        rubriques_employeur = ['Retenue CNSS Employeur','Décés accidentel Employeur', 'Taxe de formation professionnelle Employeur', 'Retenue CIMR Employeur',
                               'C.O.S Employeur', 'Couverture des allocations familiales Employeur', 'Mutuelle incapacité Employeur','Cotisation MUPRAS Employeur',
                               'Accident de travail Employeur', 'Mutuelle Employeur', 'Assurance maladie obligatoire Employeur',
                               'Retraite complémentaire RECORE Employeur','Mutuelle décés Employeur','Bonus Employeur', 'Prét logement Employeur',
                               'Participation AMO Employeur', 'Mutuelle Maladie et Maternité Employeur', 'Allocations familiales Employeur', 'Retraite Complémentaire Employeur',
                               'Jours fériés Employeur', 'Acompte accident de travail Employeur', 'Taxe de solidarité Employeur', 
                               'Frais de transport/Inventaire Employeur', 'Prime départ retraite Employeur', 'Rappel sur salaire Employeur', 'Avance sur salaire Employeur',
                               'Heures é déduire Employeur', 'Retraite  complémentaire RECORE Employeur', 'Cotisation MUPRAS Employeur', 'Retenue CIMR Employeur'
                               ]
        
        exclude_list = ['Salaire de base']
        self.env.cr.execute(self.get_all_rubriques())
        rubriques = self.env.cr.dictfetchall()
        for rubrique in rubriques:
            if rubrique['name'] not in exclude_list:
                rubrique_employee = rubrique['name']+' ' + 'Employee'
                rubrique_employeur = rubrique['name']+' ' + 'Employeur'
                #if rubrique_employee in rubriques_employee:
                worksheet.write(0,end_column,rubrique_employee,cell_style_header_tab)
                list_rubriques_employee.append(rubrique_employee)
                salary_dict_employee[rubrique_employee] = end_column
                end_column += 1
                #if rubrique_employeur in rubriques_employeur:
                if rubrique['type'] == 'cotisation':
                    worksheet.write(0,end_column,rubrique_employeur,cell_style_header_tab)
                    list_rubriques_employeur.append(rubrique_employeur)
                    salary_dict_employeur[rubrique_employeur] = end_column
                    end_column += 1
        for payroll in active_recs:
            column = 4
            for line in payroll.bulletin_line_ids:
                matricule = line.employee_id.matricule if line.employee_id else ''
                worksheet.write(row,0,matricule,cell_style_body_tab)
                name = line.employee_id.display_name if line.employee_id else ''
                worksheet.write(row,1,name,cell_style_body_tab)
                fonction = line.employee_id.job_id.display_name if line.employee_id.job_id else line.employee_id.job_title
                worksheet.write(row,2,fonction,cell_style_body_tab)
                grade = line.employee_id.category_ids[0].name if line.employee_id.category_ids else ''
                worksheet.write(row,3,grade,cell_style_body_tab)
                service = line.employee_id.department_id.name if line.employee_id.department_id else ''
                worksheet.write(row,4,service,cell_style_body_tab)
                jours_travailles = line.working_days if line.working_days else 0.0
                worksheet.write(row,5,jours_travailles,cell_style_body_tab)
                jours_leaves = line.conges_payes if line.conges_payes else 0.0
                worksheet.write(row,6,jours_leaves,cell_style_body_tab)
                salaire_base = line.mapped('salary_line_ids').filtered(lambda r: r.name == 'Salaire de base').subtotal_employee if line.mapped('salary_line_ids').filtered(lambda r: r.name == 'Salaire de base') else 0.0
                worksheet.write(row,7,salaire_base,cell_style_body_tab)
                total_salaire_base +=  salaire_base
                salaire_brute = line.salaire_brute if line.salaire_brute else 0.0
                worksheet.write(row,8,salaire_brute,cell_style_body_tab)
                total_salaire_brute +=  line.salaire_brute
                salaire_brute_imposable = line.salaire_brute_imposable if line.salaire_brute_imposable else 0.0
                worksheet.write(row,9,salaire_brute_imposable,cell_style_body_tab)
                total_salaire_imposable += line.salaire_brute_imposable
                salaire_net_imposable = line.salaire_net_imposable if line.salaire_net_imposable else 0.0
                worksheet.write(row,10,salaire_net_imposable,cell_style_body_tab)
                total_salaire_net_imposable += line.salaire_net_imposable
                salaire_net = line.salaire_net if line.salaire_net else 0.0
                worksheet.write(row,11,salaire_net,cell_style_body_tab)
                total_salaire_net += line.salaire_net
                salaire_net_a_payer = line.salaire_net_a_payer if line.salaire_net_a_payer else 0.0
                worksheet.write(row,12,salaire_net_a_payer,cell_style_body_tab)
                total_salaire_net_payer += line.salaire_net_a_payer
                frais_professionnels = line.frais_pro if line.frais_pro else 0.0
                worksheet.write(row,13,frais_professionnels,cell_style_body_tab)
                total_frais_professionnels += line.frais_pro
                cotisations_employe = line.cotisations_employee if line.cotisations_employee else 0.0
                worksheet.write(row,14,cotisations_employe,cell_style_body_tab)
                total_cotisations_employe += line.cotisations_employee
                cotisations_employeur = line.cotisations_employer if line.cotisations_employer else 0.0
                worksheet.write(row,15,cotisations_employeur,cell_style_body_tab)
                total_cotisations_employeur+= line.cotisations_employer
                for salary in line.salary_line_ids:
                    salary_employee = salary.name +' ' + 'Employee'
                    salary_employeur = salary.name +' ' + 'Employeur'
                    if salary_employee in list_rubriques_employee:
                        worksheet.write(row,salary_dict_employee.get(salary_employee),salary.subtotal_employee,cell_style_body_tab)
                    if salary_employeur in list_rubriques_employeur:
                        worksheet.write(row,salary_dict_employeur.get(salary_employeur),salary.subtotal_employer,cell_style_body_tab)
                    else:
                        continue
                    column += 1
                row += 1
        worksheet.write(row,0,'TOTAL',cell_style_header_tab)
        worksheet.write(row,1,'-',cell_style_header_tab)
        worksheet.write(row,2,'-',cell_style_header_tab)
        worksheet.write(row,3,'-',cell_style_header_tab)
        worksheet.write(row,4,'-',cell_style_header_tab)
        worksheet.write(row,5,'-',cell_style_header_tab)
        worksheet.write(row,6,'-',cell_style_header_tab)
        worksheet.write(row,7,total_salaire_base,cell_style_header_tab)
        worksheet.write(row,8,total_salaire_brute,cell_style_header_tab)
        worksheet.write(row,9,total_salaire_imposable,cell_style_header_tab)
        worksheet.write(row,10,total_salaire_net_imposable,cell_style_header_tab)
        worksheet.write(row,11,total_salaire_net,cell_style_header_tab)
        worksheet.write(row,12,total_salaire_net_payer,cell_style_header_tab)
        worksheet.write(row,13,total_frais_professionnels,cell_style_header_tab)
        worksheet.write(row,14,total_cotisations_employe,cell_style_header_tab)
        worksheet.write(row,15,total_cotisations_employeur,cell_style_header_tab)
        end_column = 16
        for rubrique in rubriques:
            if rubrique['name'] not in exclude_list:
                rubrique_employee = rubrique['name']+' ' + 'Employee'
                rubrique_employeur = rubrique['name']+' ' + 'Employeur'
                #if rubrique_employee in rubriques_employee: 
                worksheet.write(row,end_column,rubrique['total_subtotal_employee'],cell_style_header_tab)
                end_column += 1
                #if rubrique_employeur in rubriques_employeur:
                if rubrique['type'] == 'cotisation':
                    worksheet.write(row,end_column,rubrique['total_subtotal_employer'],cell_style_header_tab)
                    end_column += 1
        fp = BytesIO()
        workbook.save(fp)
        file_data = base64.encodebytes(fp.getvalue()).decode('utf-8')
        self.write({
            'file_data': file_data,
            'filename': filename,
        })
        fp.close()
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=wizard.export.journal.paie&id=" + str(self.id) + "&filename_field=filename&field=file_data&download=true&filename=" + filename,
            'target': 'self',
        }
