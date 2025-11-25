# -*- coding: utf-8 -*-

import time
from lxml import etree
from odoo import models, fields, _
import base64
import datetime as dt
import xlwt
from io import StringIO,BytesIO
from odoo.exceptions import ValidationError

class IrDeclaration(models.Model):
    
    def _get_effectif(self):
        for record in self:
            record.effectifTotal = record.nbrPersoPermanent + record.nbrPersoOccasionnel + record.nbrStagiaires
    
    def _get_nombre_personne_permanent(self):
        for record in self:
            record.nbrPersoPermanent = len(record.pp_lines)
    
    def _get_nombre_personne_occasionnel(self):
        for record in self:
            record.nbrPersoOccasionnel = len(record.po_lines)
    
    def _get_nombre_personne_stagiaire(self):
        for record in self:
            record.nbrStagiaires = len(record.ps_lines)
    
    def _get_total_paye(self):
        for record in self:
            record.totalSommePayeRTS = record.montantPermanent + record.montantOccasionnel + record.montantStagiaire
    
    def _get_total_brut_imposable_pp(self):
        for record in self:
            somme = 0
            for pp_line in record.pp_lines:
                somme += pp_line.mtRevenuBrutImposable
            record.totalMtRevenuBrutImposablePP = somme
    
    def _get_total_net_imposable_pp(self):
        for record in self:
            somme = 0
            for pp_line in record.pp_lines:
                somme += pp_line.mtRevenuNetImposable
            record.totalMtRevenuNetImposablePP = somme
    
    def _get_total_deduction_pp(self):
        for record in self:
            somme = 0
            for pp_line in record.pp_lines:
                somme += pp_line.mtTotalDeduction
            record.totalMtTotalDeductionPP = somme
    
    def _get_total_ir_preleve_pp(self):
        for record in self:
            somme = 0
            for pp_line in record.pp_lines:
                somme += pp_line.irPreleve
            record.totalMtIrPrelevePP = somme
    
    def _get_montant_permanent(self):
        for record in self:
            somme = 0
            for pp_line in record.pp_lines:
                somme += pp_line.mtBrutTraitementSalaire
            record.montantPermanent = somme
    
    def _get_mt_brut_po(self):
        for record in self:
            somme = 0
            for po_line in record.po_lines:
                somme += po_line.mtBrutSommes
            record.totalMtBrutSommesPO = somme
    
    def _get_ir_preleve_po(self):
        for record in self:
            somme = 0
            for po_line in record.po_lines:
                somme += po_line.irPreleve
            record.totalIrPrelevePO = somme
    
    def _get_montant_occasionnel(self):
        for record in self:
            somme = 0
            for po_line in record.po_lines:
                somme += po_line.mtBrutSommes
            record.montantOccasionnel = somme

    def _get_mt_brut_trait_sal_stg(self):
        for record in self:
            somme = 0
            for ps_line in record.ps_lines:
                somme += ps_line.mtBrutTraitementSalaire
            record.totalMtBrutTraitSalaireSTG = somme
    
    def _get_mt_brut_indemnite_stg(self):
        for record in self:
            somme = 0
            for ps_line in record.ps_lines:
                somme += ps_line.mtBrutIndemnites
            record.totalMtBrutIndemnitesSTG = somme
    
    def _get_mt_retenus_stg(self):
        for record in self:
            somme = 0
            for ps_line in record.ps_lines:
                somme += ps_line.mtRetenues
            record.totalMtRetenuesSTG = somme
    
    def _get_mt_revenu_net_imp_stg(self):
        for record in self:
            somme = 0
            for ps_line in record.ps_lines:
                somme += ps_line.mtRevenuNetImposable
            record.totalMtRevenuNetImpSTG = somme
    
    def _get_montant_stagiaire(self):
        for record in self:
            somme = 0
            for ps_line in record.ps_lines:
                somme += ps_line.mtBrutTraitementSalaire
            record.montantStagiaire = somme
    
    _rec_name = "nom"
    _name = "ir.declaration"
    
    nom = fields.Char('Nom', size=64,required=True)
    prenom = fields.Char(u'Prénom', size=64)
    company_ids = fields.Many2many(comodel_name='res.company', string='Sociétés', required=True)
    raison_sociale = fields.Char('Raison sociale')
    date_from = fields.Date('Du')
    date_to = fields.Date('Au')
    annee = fields.Char('Année')
    commune = fields.Many2one('ir.ville', 'Commune')
    effectifTotal = fields.Integer(compute="_get_effectif", string='Effectif total')
    nbrPersoPermanent = fields.Integer(compute="_get_nombre_personne_permanent", string='Personnel permanent')
    nbrPersoOccasionnel = fields.Integer(compute="_get_nombre_personne_occasionnel", string='Personnel occasionnel')
    nbrStagiaires = fields.Float(compute="_get_nombre_personne_stagiaire", string='Stagiaires', type="integer")
    totalMtRevenuBrutImposablePP = fields.Float(compute="_get_total_brut_imposable_pp", string='Total des Montants du revenu brut imposable du personnel permanent')
    totalMtRevenuNetImposablePP = fields.Float(compute="_get_total_net_imposable_pp", string='Total des Montants du revenu net imposable du personnel permanent')
    totalMtTotalDeductionPP = fields.Float(compute="_get_total_deduction_pp", string='Total des déductions sur revenus du personnel permanent')
    totalMtIrPrelevePP = fields.Float(compute="_get_total_ir_preleve_pp", string='Total de la colonne de l’ I.R. Prélevé du personnel permanent')
    totalMtBrutSommesPO = fields.Float(compute="_get_mt_brut_po", string='Total des montants brut des sommes payées du personnel occasionnel')
    totalIrPrelevePO = fields.Float(compute="_get_ir_preleve_po", string='Total de la colonne de l’ I.R. Prélevé du personnel occasionnel')
    totalMtBrutTraitSalaireSTG = fields.Float(compute="_get_mt_brut_trait_sal_stg", string='Total des montants brut des traitements,salaires et émoluments du tableau des stagiaires')
    totalMtBrutIndemnitesSTG = fields.Float(compute="_get_mt_brut_indemnite_stg", string='Total des montants brut des indemnités des stagiaires')
    totalMtRetenuesSTG = fields.Float(compute="_get_mt_retenus_stg", string='Total des montants des retenues opérées des stagiaires')
    totalMtRevenuNetImpSTG = fields.Float(compute="_get_mt_revenu_net_imp_stg", string='Total des montants du revenu net imposable des stagiaires')
    totalSommePayeRTS = fields.Float(compute="_get_total_paye", string='Total des sommes payées (A) +(B)+ (C)')
    totalmtAnuuelRevenuSalarial = fields.Float('Total du montant annuel du revenu salarial')
    totalmtAbondement = fields.Float('Total du montant de l’abondement versé')
    montantPermanent = fields.Float(compute="_get_montant_permanent", string='Montant des traitements, salaires,indemnités et émoluments versés au personnel permanent (A)')
    montantOccasionnel = fields.Float(compute="_get_montant_occasionnel", string='Montant des traitements, salaires, indemnités et émoluments versés au personnel occasionnel (B)')
    montantStagiaire = fields.Float(compute="_get_montant_stagiaire", string='Montant des traitements, salaires,indemnités et émoluments versés aux stagiaires (C)')
    referenceDeclaration = fields.Float('Référence de la déclaration')
    pp_lines = fields.One2many(comodel_name='ir.personnel.permanant', inverse_name='personnel_id', string='Personnel permanant')
    po_lines = fields.One2many(comodel_name='ir.personnel.occasionel', inverse_name='personnel_id', string='Personnel occasionnel')
    ps_lines = fields.One2many(comodel_name='ir.personnel.stagiaire', inverse_name='personnel_id', string='Stagiaires')
    pb_lines = fields.One2many(comodel_name='ir.personnel.beneficiare', inverse_name='personnel_id', string='Personnel beneficiaire')
    pbe_lines = fields.One2many(comodel_name='ir.personnel.beneficiare.epargne', inverse_name='personnel_id', string='Personnel bénéficiaire d’abondement')
    pe_lines = fields.One2many(comodel_name='ir.personnel.exonere', inverse_name='personnel_id', string='Salariés exonérés', help="Introduit dans la MAJ 3.0")
    pd_lines = fields.One2many(comodel_name='ir.personnel.doctorant', inverse_name='personnel_id', string='Doctorants', help="Introduit dans la MAJ 3.0")
    recapitulatif_lines = fields.One2many(comodel_name='ir.recapitulatif', inverse_name='personnel_id', string='Recapitulatif')
    output = fields.Binary(string='Declaration EDI',readonly=True)
    output_name = fields.Char(string='File name', default="output_name")
    file_data_permanent = fields.Binary(string='Fichier CSV')
    file_name_permanent = fields.Char(string='File name')
    file_data_exonere = fields.Binary(string='Fichier CSV', help="Introduit dans MAJ 3")
    file_name_exonere = fields.Char(string='File name', help="Introduit dans MAJ 3")
    file_data_occasionnel = fields.Binary(string='Fichier CSV')
    file_name_occasionnel = fields.Char(string='File name')
    file_data_stagiaire = fields.Binary(string='Fichier CSV')
    file_name_stagiaire = fields.Char(string='File name'),
    file_data_doctorant = fields.Binary(string='Fichier CSV', help="Introduit dans MAJ 3")
    file_name_doctorant = fields.Char(string='File name', help="Introduit dans MAJ 3")
    file_data_recap = fields.Binary(string='Fichier CSV')
    file_name_recap = fields.Char(string='File name')
    create_uid = fields.Many2one(comodel_name='res.users',string='Utilisateur', readonly=True)
    hr_payroll_ma_ids = fields.One2many(comodel_name='hr.payroll_ma', inverse_name='hr_ir_id', string='Saisies mensuelles')
    state = fields.Selection([('draft', 'Brouillon'),
            ('prepare', u'Préparation'),
            ('load_xml', 'Génération XML'),
            ('close', 'Clôture')], string='State', readonly=True, default='draft')
    file_data = fields.Binary('Excel File', readonly=True, attachment=False)
    filename = fields.Char(string='Filename', size=256, readonly=True)
    
    def export_report(self):
        _pfc = '26'
        _bc = '28'
        xls_styles = {
            'xls_title': 'font: bold true, height 240;',
            'xls_title2': 'font: bold true, height 200;',
            'bold': 'font: bold true;',
            'underline': 'font: underline true;',
            'italic': 'font: italic true;',
            'fill': 'pattern: pattern solid, fore_color %s;' % _pfc,
            'fill_blue': 'pattern: pattern solid, fore_color 27;',
            'fill_grey': 'pattern: pattern solid, fore_color 22;',
            'borders_all':
                'borders: left thin, right thin, top thin, bottom thin,'
                'left_colour %s, right_colour %s, \
                top_colour %s, bottom_colour %s;'
                % (_bc, _bc, _bc, _bc),
            'borders_all2':
                'borders: left thin, right thin, top thick, bottom thin,'
                'left_colour %s, right_colour %s, top_colour %s, \
                bottom_colour %s;'
                % (_bc, _bc, _bc, _bc),
            'left': 'align: horz left;',
            'center': 'align: horz center;',
            'right': 'align: horz right;',
            'wrap': 'align: wrap true;',
            'top': 'align: vert top;',
            'ver_top': 'align: vert center;',
            'bottom': 'align: vert bottom;',
        }

        cell_format = xls_styles['borders_all'] + xls_styles['wrap'] + xls_styles['ver_top']
        cell_style_header_tab = xlwt.easyxf(cell_format + xls_styles['bold'] +
                                    xls_styles['center'] + xls_styles['fill'])
        cell_style_number = xlwt.easyxf(cell_format + xls_styles['right'],
                                        num_format_str='#,##0.00')
        cell_style_normal = xlwt.easyxf(cell_format + xls_styles['left'])
        date_style = xlwt.easyxf(cell_format + xls_styles['right'], num_format_str='YYYY-MM-DD')
        filename = 'Etat_9421.xls'
        workbook = xlwt.Workbook(encoding="UTF-8")
        worksheet = workbook.add_sheet('Etat 9421')
        '''worksheet.col(1).width = int(15100)
        worksheet.col(5).width = int(3100)
        worksheet.col(6).width = int(3100)
        worksheet.col(7).width = int(6100)
        worksheet.write_merge(0, 0, 0, 13, 'PERSONNEL PERMANENT', cell_style_header_tab)
        worksheet.write_merge(1, 1, 0, 13, 'SOCIETE : ATLAS SERVAIR', cell_style_header_tab)
        worksheet.write_merge(2, 2, 0, 13, self.annee, cell_style_header_tab)
        worksheet.write_merge(4, 5, 0, 0, 'MATR', cell_style_header_tab)
        worksheet.write(4, 1, 'NOM ET PRENOM', cell_style_header_tab)
        worksheet.write(5, 1, 'ADRESSE PERSONNELLE', cell_style_header_tab)
        worksheet.write(4, 2, 'No.CIN', cell_style_header_tab)
        worksheet.write(5, 2, 'No.Cnss', cell_style_header_tab)
        worksheet.write_merge(4, 5, 3, 3, 'ID FISCALE', cell_style_header_tab)
        worksheet.write_merge(4, 5, 4, 4, 'S.F', cell_style_header_tab)
        worksheet.write(4, 5, 'Brut.TRT.sal', cell_style_header_tab)
        worksheet.write(5, 5, 'AVTG.NAT/ARG', cell_style_header_tab)
        worksheet.write(4, 6, 'Indem.F.Prof', cell_style_header_tab)
        worksheet.write(5, 6, 'ELEM.EXON', cell_style_header_tab)
        worksheet.write_merge(4, 5, 7, 7, 'Montant Revenu brut Imposable', cell_style_header_tab)
        worksheet.write(4, 8, 'T.F.P', cell_style_header_tab)
        worksheet.write(5, 8, 'FRAIS PROF.', cell_style_header_tab)
        worksheet.write(4, 9, 'Cot.Ass.Retraite', cell_style_header_tab)
        worksheet.write(5, 9, 'ECHE.PRELEV.', cell_style_header_tab)
        worksheet.write_merge(4, 4, 10, 11, 'Retenu.Operees', cell_style_header_tab)
        worksheet.write(5, 10, 'DATE AC', cell_style_header_tab)
        worksheet.write(5, 11, 'DATE PH', cell_style_header_tab)
        worksheet.write(4, 12, 'Net.Imposable', cell_style_header_tab)
        worksheet.write(5, 12, 'I.R PRELEVE', cell_style_header_tab)
        worksheet.write(4, 13, 'Nbre.Jours', cell_style_header_tab)
        worksheet.write(5, 13, 'NBR.REDT/C.F', cell_style_header_tab)
        row = 6
        mtBrutTraitementSalaire = mtAvantages = mtFraisProfess = mtExonere = mtRevenuBrutImposable = mtCotisationAssur = mtEcheances = mtAutresRetenues = mtRevenuNetImposable = irPreleve = periode = nbrReductions = 0
        mtAvantages
        for permanent in self.pp_lines:
            worksheet.write_merge(row, row+1, 0, 0, permanent.numMatricule, cell_style_normal)
            worksheet.write(row, 1, permanent.nom + permanent.prenom, cell_style_normal)
            worksheet.write(row+1, 1, permanent.adressePersonnelle, cell_style_normal)
            worksheet.write(row, 2, permanent.numCNI, cell_style_normal)
            worksheet.write(row+1, 2, permanent.numCNSS, cell_style_normal)
            worksheet.write_merge(row, row+1, 3, 3, permanent.ifu, cell_style_normal)
            worksheet.write_merge(row, row+1, 4, 4, permanent.refSituationFamiliale.libelle, cell_style_normal)
            
            worksheet.write(row, 5, permanent.mtBrutTraitementSalaire , cell_style_normal)
            mtBrutTraitementSalaire += permanent.mtBrutTraitementSalaire
            
            worksheet.write(row+1, 5, permanent.mtAvantages, cell_style_normal)
            mtAvantages += permanent.mtAvantages
            
            worksheet.write(row, 6, permanent.mtFraisProfess, cell_style_normal)
            mtFraisProfess += permanent.mtFraisProfess
            
            worksheet.write(row+1, 6, permanent.mtExonere, cell_style_normal)
            mtExonere += permanent.mtExonere
            
            worksheet.write_merge(row, row+1, 7, 7, permanent.mtRevenuBrutImposable, cell_style_normal)
            mtRevenuBrutImposable += permanent.mtRevenuBrutImposable
            
            worksheet.write(row, 8, permanent.refTaux.code, cell_style_normal)
            worksheet.write(row+1, 8, permanent.mtFraisProfess, cell_style_normal)
            worksheet.write(row, 9, permanent.mtCotisationAssur, cell_style_normal)
            mtCotisationAssur += permanent.mtCotisationAssur
            
            worksheet.write(row+1, 9, permanent.mtEcheances, cell_style_normal)
            mtEcheances += permanent.mtEcheances
            
            worksheet.write_merge(row, row, 10, 11, permanent.mtAutresRetenues, cell_style_normal)
            mtAutresRetenues += permanent.mtAutresRetenues
            worksheet.write(row+1, 10, '', cell_style_normal)
            worksheet.write(row+1, 11, '', cell_style_normal)
            worksheet.write(row, 12, permanent.mtRevenuNetImposable, cell_style_normal)
            mtRevenuNetImposable += permanent.mtRevenuNetImposable
            
            worksheet.write(row+1, 12, permanent.irPreleve, cell_style_normal)
            irPreleve += permanent.irPreleve
            
            worksheet.write(row, 13, permanent.periode, cell_style_normal)
            periode += permanent.periode
            worksheet.write(row+1, 13, permanent.nbrReductions, cell_style_normal)
            nbrReductions += permanent.nbrReductions
            row += 2
            
        worksheet.write_merge(row, row+1, 0, 0, 'Total', cell_style_header_tab)
        worksheet.write(row, 1, '', cell_style_header_tab)
        worksheet.write(row+1, 1, '', cell_style_header_tab)
        worksheet.write(row, 2, '', cell_style_header_tab)
        worksheet.write(row+1, 2, '', cell_style_header_tab)
        worksheet.write_merge(row, row+1, 3, 3, '', cell_style_header_tab)
        worksheet.write_merge(row, row+1, 4, 4, '', cell_style_header_tab)
        worksheet.write(row, 5, mtBrutTraitementSalaire, cell_style_number)
        worksheet.write(row+1, 5, mtAvantages, cell_style_number)
        worksheet.write(row, 6, mtFraisProfess, cell_style_number)
        worksheet.write(row+1, 6, mtExonere, cell_style_number)
        worksheet.write_merge(row, row+1, 7, 7, mtRevenuBrutImposable, cell_style_number)
        worksheet.write(row, 8, '', cell_style_header_tab)
        worksheet.write(row+1, 8, mtFraisProfess, cell_style_number)
        worksheet.write(row, 9, mtCotisationAssur, cell_style_number)
        worksheet.write(row+1, 9, mtEcheances, cell_style_number)
        worksheet.write_merge(row, row, 10, 11, mtAutresRetenues, cell_style_number)
        worksheet.write(row+1, 10, '', cell_style_header_tab)
        worksheet.write(row+1, 11, '', cell_style_header_tab)
        worksheet.write(row, 12, mtRevenuNetImposable, cell_style_number)
        worksheet.write(row+1, 12, irPreleve, cell_style_number)
        worksheet.write(row, 13, periode, cell_style_number)
        worksheet.write(row+1, 13, '', cell_style_header_tab)
        '''
        worksheet.write(0, 1, 'Prénom', cell_style_header_tab)
        worksheet.write(0, 2, 'Nom', cell_style_header_tab)
        worksheet.write(0, 3, 'Mnt Brut Traitement Salaire', cell_style_header_tab)
        worksheet.write(0, 4, 'Mnt Element Exo ', cell_style_header_tab)
        worksheet.write(0, 5, 'Revenus Brut Imposable IR', cell_style_header_tab)
        worksheet.write(0, 6, 'Mnt Frais Professionnel ', cell_style_header_tab)
        worksheet.write(0, 7, 'Montant des cotisations d\'assurance retraite', cell_style_header_tab)
        worksheet.write(0, 8, 'Montant des échéances prélevées', cell_style_header_tab)
        worksheet.write(0, 9, 'Montant des autres retenues', cell_style_header_tab)
        worksheet.write(0, 10, 'Total du revenu net imposable', cell_style_header_tab)
        worksheet.write(0, 11, 'nombre de Déduction pour charge de famille', cell_style_header_tab)
        worksheet.write(0, 12, 'Montant de l\'IR', cell_style_header_tab)
        worksheet.write(0, 13, 'Total des périodes en jour du personnel', cell_style_header_tab)
        
        row = 1
        for permanent in self.pp_lines:
            worksheet.write(row, 1, permanent.prenom, cell_style_normal)
            worksheet.write(row, 2, permanent.nom, cell_style_normal)
            worksheet.write(row, 3, permanent.mtBrutTraitementSalaire, cell_style_normal)
            worksheet.write(row, 4, permanent.mtExonere, cell_style_normal)
            worksheet.write(row, 5, permanent.mtRevenuBrutImposable, cell_style_normal)
            worksheet.write(row, 6, permanent.mtFraisProfess, cell_style_normal)
            worksheet.write(row, 7, permanent.mtCotisationAssur, cell_style_normal)
            worksheet.write(row, 8, permanent.mtEcheances, cell_style_normal)
            worksheet.write(row, 9, permanent.mtAutresRetenues, cell_style_normal)
            worksheet.write(row, 10, permanent.mtRevenuNetImposable, cell_style_normal)
            worksheet.write(row, 11, permanent.nbrReductions, cell_style_normal)
            worksheet.write(row, 12, permanent.irPreleve, cell_style_normal)
            worksheet.write(row, 13, permanent.periode, cell_style_normal)
            row += 1
            
        fp = BytesIO()
        workbook.save(fp)
        self.write({
            'file_data': base64.encodestring(fp.getvalue()),
            'filename': filename,
        })
        fp.close()
        
        return {
            'type': 'ir.actions.act_url',
            'url': "web/content/?model=ir.declaration&id=" + str(self.id) + "&filename_field=filename&field=file_data&download=true&filename=" + filename,
            'target': 'self',
        }
    
    def back_draft(self):
        for record in self:
            record.state = 'draft'

    def prepare(self):
        for record in self:
            payroll_obj = self.env['hr.payroll_ma']
            mois = []
            mois = ['01/'+str(record.annee),'02/'+str(record.annee),'03/'+str(record.annee)]
            mois += ['04/'+str(record.annee),'05/'+str(record.annee),'06/'+str(record.annee)]
            mois += ['07/'+str(record.annee),'08/'+str(record.annee),'09/'+str(record.annee)]
            mois += ['10/'+str(record.annee),'11/'+str(record.annee),'12/'+str(record.annee)]
            payrolls = payroll_obj.search([('period_id.name','in',mois), ('company_id','in',record.company_ids.ids)])
            for payroll in payrolls:
                payroll.update({'hr_ir_id': record.id})
            record.state = 'prepare'
    
    def load_data(self):
        for record in self:
            mois = []
            mois = ['01/'+str(record.annee),'02/'+str(record.annee),'03/'+str(record.annee)]
            mois += ['04/'+str(record.annee),'05/'+str(record.annee),'06/'+str(record.annee)]
            mois += ['07/'+str(record.annee),'08/'+str(record.annee),'09/'+str(record.annee)]
            mois += ['10/'+str(record.annee),'11/'+str(record.annee),'12/'+str(record.annee)]
            permanent_line = self.env['ir.personnel.permanant']
            employees = self.mapped('hr_payroll_ma_ids').mapped('bulletin_line_ids').mapped('employee_id')
            record.mapped('pp_lines').unlink()
            data = {}
            for employee in employees:
                bulletins = self.mapped('hr_payroll_ma_ids').mapped('bulletin_line_ids').filtered(lambda r:r.employee_id.id == employee.id)
                data["nom"] = employee.name
                data["prenom"] = employee.prenom
                data["adressePersonnelle"] = employee.private_street if employee.private_street else ''
                data["numCNI"] = employee.identification_id if employee.identification_id else 'None'
                data["numCE"] = ''
                data["numPPR"] = ''
                data["numCNSS"] = employee.ssnid
                data["ifu"] = ''
                data["salaireBaseAnnuel"] = sum(line.subtotal_employee for line in bulletins.mapped('salary_line_ids').filtered(lambda r:r.name == 'Salaire de base'))
                data["mtBrutTraitementSalaire"] = sum(bulletin.salaire_brute for bulletin in bulletins)
                data["periode"] = sum(bulletin.working_days + bulletin.conges_payes for bulletin in bulletins)
                data["mtExonere"] = sum(bulletin.salaire_brute - bulletin.salaire_brute_imposable_ir for bulletin in bulletins)
                data["mtEcheances"] = sum(loan_line.interet_amount for loan_line in self.env['hr.payroll.loan.line'].search([('hr_payroll_loan_id.employee_id', '=', employee.id), ('period_id.name', 'in', mois)]))
                data["nbrReductions"] = employee.chargefam if employee.chargefam else 0
                data["mtIndemnite"] = 0
                data["mtAvantages"] = 0
                data["mtRevenuBrutImposable"] = sum(bulletin.salaire_brute_imposable_ir for bulletin in bulletins)
                data["mtFraisProfess"] = sum((bulletin.salaire_brute_imposable_ir * 0.2 if bulletin.salaire_brute_imposable_ir * 0.2 < 2500 else 2500) for bulletin in bulletins)
                data["mtCotisationAssur"] = sum(line.subtotal_employee for line in bulletins.mapped('salary_line_ids').filtered(lambda r:r.name in ['PER', 'Retraite Complémentaire']))
                data["mtAutresRetenues"] = sum(line.subtotal_employee for line in bulletins.mapped('salary_line_ids').filtered(lambda r:r.name in ['Cotisation  MUPRAS','Retraite  complémentaire RECORE','CIMR 3%', 'Cimr 3%', 'Retenue CIMR','MUTUELLE RAM MUPRAS', 'ASSURANCE RECORE RAM', 'Retraite complémentaire RECORE', 'Cotisation MUPRAS', 'CNSS', 'AMO', 'Retenue CNSS', 'Assurance maladie obligatoire', 'Mutuelle Maladie et Maternité', 'Mutuelle décès', 'Mutuelle incapacité', 'Décès accidentel',  'Accident de travail', 'Cnss','Amo', 'Mutuelle', 'MUTUELLE', 'MUTUELLE DECES', 'MUTUELLE INCAPACITÉ', 'DECES ACCIDENTEL', 'CIMR', 'Cimr']))
                data["mtRevenuNetImposable"] = sum(bulletin.salaire_net_imposable for bulletin in bulletins)
                data["mtTotalDeduction"] = data["mtFraisProfess"] + data["mtCotisationAssur"] + data["mtAutresRetenues"] + data["mtEcheances"]
                data["irPreleve"] = sum(line.subtotal_employee for line in bulletins.mapped('salary_line_ids').filtered(lambda r:r.name == 'Impot sur le revenu'))
                data["casSportif"] = bulletins[0].employee_id.casSportif
                data["numMatricule"] = bulletins[0].employee_id.matricule
                data["datePermis"] = bulletins[0].employee_id.datePermis
                data["dateAutorisation"] = bulletins[0].employee_id.dateAutorisation
                data["refSituationFamiliale"] = bulletins[0].employee_id.ir_situation_famille.id
                data["refTaux"] = bulletins[0].employee_id.ir_taux_frais.id
                data["personnel_id"] = record.id
                permanent_id = permanent_line.create(data)
                
                
    def load_xml(self):
        for declaration in self:
            declaration.state = 'load_xml'
    
    def close(self):
        for declaration in self:
            declaration.state = 'close'
    
    def file_parsing_permanent(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid,ids, context=context):
            cr.execute(""" delete from ir_personnel_permanant where personnel_id='%s' """ % rec.id)
        permanent_line = self.pool.get('ir.personnel.permanant')
        element_exonere_permanent_line = self.pool.get('ir.personnel.permanant.element.exonere')
        data_table = self.read(cr, uid, ids[0],  context=context)

        bal_field=data_table['file_data_permanent']
        if not bal_field:
            raise osv.except_osv(('Erreur!'), ("Veuillez indiquer le fichier CSV !"))
        data_bal = unicode(base64.decodestring(bal_field), 'windows-1252', 'strict').encode('utf-8').strip()
        if data_bal:
            reader = data_bal.split('\n')
            data = {}
            i = 0
            liste_elements_exoneres = []
            for row in reader:
                i += 1
                if i == 1:
                    first_line = row.split(';')
                    if len(first_line) > 29:
                        for j in range(29,len(first_line),1):
                            liste_elements_exoneres.append(first_line[j])
                    continue
                line = row.split(';')
                if len(line) == 1:
                    continue
                empty_row = True
                for l in line:
                    if l.strip():
                        empty_row = False
                        break
                if empty_row:
                    continue
                data["nom"] = line[0]
                data["prenom"] = line[1]                       
                data["adressePersonnelle"] = line[2]
                data["numCNI"] = line[3]
                data["numCE"] = line[4]
                data["numPPR"] = line[5]
                data["numCNSS"] = line[6]
                data["ifu"] = line[7]
                data["salaireBaseAnnuel"] = line[8]
                data["mtBrutTraitementSalaire"] = line[9]
                data["periode"] = line[10]
                data["mtExonere"] = line[11]
                data["mtEcheances"] = line[12]
                data["nbrReductions"] = line[13]
                data["mtIndemnite"] = line[14]
                data["mtAvantages"] = line[15]
                data["mtRevenuBrutImposable"] = line[16]
                data["mtFraisProfess"] = line[17]
                data["mtCotisationAssur"] = line[18]
                data["mtAutresRetenues"] = line[19]
                data["mtRevenuNetImposable"] = line[20]
                data["mtTotalDeduction"] = line[21]
                data["irPreleve"] = line[22]
                if line[23] == 1:
                    data["casSportif"] = 1
                else:
                    data["casSportif"] = 0
                data["numMatricule"] = line[24]
                if line[25]:
                    data["datePermis"] = line[25] or ""
                if line[26]:
                    data["dateAutorisation"] = line[26]
                situation_id = self.pool.get('ir.situation.famille').search(cr,uid,[('code','=',line[27])],limit=1)
                if not situation_id:
                    raise osv.except_osv(('Erreur!'), ("%s")% (line[27],))
                data["refSituationFamiliale"] = situation_id[0]
                taux_id = self.pool.get('ir.taux.frais').search(cr,uid,[('valeur','=',line[28])],limit=1)
                if taux_id:
                    data["refTaux"] = taux_id[0]
                data["personnel_id"] = rec.id
                permanent_id = permanent_line.create(cr,uid,data)
                
                position = 0
                for element in liste_elements_exoneres:
                    if line[ 29 + position] == "\r" or not line[ 29 + position] or line[ 29 + position] == "0" or line[ 29 + position] == "0\r":
                        position = position + 1
                        continue
                    data_element_exonere = {}
                    ir_element_exonere_id = self.pool.get('ir.element.exonere').search(cr,uid,[('libelle','=',element.replace("\r", ""))],limit=1)
                    if not ir_element_exonere_id:
                        raise osv.except_osv(('Erreur!'), ("%s n'existe pas")% (element,))
                    data_element_exonere["ir_element_exonere_id"] = ir_element_exonere_id[0]
                    data_element_exonere["montantExonere"] = line[ 29 + position]
                    data_element_exonere["ir_personnel_permanant_id"] = permanent_id
                    element_exonere_permanent_line.create(cr,uid,data_element_exonere)
                    position = position + 1
                data = {}
                data_element_exonere = {}
                
        return True
    
    """ MAJ 3.0 """
    def file_parsing_exonere(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid,ids, context=context):
            cr.execute(""" delete from ir_personnel_exonere where personnel_id='%s' """ % rec.id)
        exonere_line = self.pool.get('ir.personnel.exonere')
        data_table = self.read(cr, uid, ids[0],  context=context)

        bal_field=data_table['file_data_exonere']
        if not bal_field:
            raise osv.except_osv(('Erreur!'), ("Veuillez indiquer le fichier CSV !"))
        data_bal=base64.decodestring(bal_field)
        if data_bal:
            reader = data_bal.split('\n')
            data = {}
            i = 0
            for row in reader:
                i += 1
                if i == 1:
                    continue
                line = row.split(';')
                if len(line) == 1:
                    continue
                empty_row = True
                for l in line:
                    if l.strip():
                        empty_row = False
                        break
                if empty_row:
                    continue
                
                data["nom"] = line[0]
                data["prenom"] = line[1]                       
                data["adressePersonnelle"] = line[2]
                data["numCNI"] = line[3]
                data["numCE"] = line[4]
                data["numCNSS"] = line[5]
                data["ifu"] = line[6]
                data["periode"] = line[7]
                data["dateRecrutement"] = line[8]
                data["mtBrutTraitementSalaire"] = line[9]
                data["mtIndemniteArgentNature"] = line[10]
                data["mtIndemniteFraisPro"] = line[11]
                data["mtRevenuBrutImposable"] = line[12]
                data["mtRetenuesOperees"] = line[13]
                data["mtRevenuNetImposable"] = line[14]
                data["personnel_id"] = rec.id
                exonere_line.create(cr,uid,data)
                data = {}
                
        return True
    """"""""""""""""""
    
    def file_parsing_occasionnel(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid,ids, context=context):
            cr.execute(""" delete from ir_personnel_occasionel where personnel_id='%s' """ % rec.id)
        occasionel_line = self.pool.get('ir.personnel.occasionel')
        data_table = self.read(cr, uid, ids[0],  context=context)

        bal_field=data_table['file_data_occasionnel']
        if not bal_field:
            raise osv.except_osv(('Erreur!'), ("Veuillez indiquer le fichier CSV !"))
        data_bal=base64.decodestring(bal_field)
        if data_bal:
            reader = data_bal.split('\n')
            data = {}
            i = 0
            for row in reader:
                i += 1
                if i == 1:
                    continue
                line = row.split(';')
                if len(line) == 1:
                    continue
                empty_row = True
                for l in line:
                    if l.strip():
                        empty_row = False
                        break
                if empty_row:
                    continue
                
                data["nom"] = line[0]
                data["prenom"] = line[1]                       
                data["adressePersonnelle"] = line[2]
                data["numCNI"] = line[3]
                data["numCE"] = line[4]
                data["ifu"] = line[5]
                data["mtBrutSommes"] = line[6]
                data["irPreleve"] = line[7]
                data["profession"] = line[8]
                data["personnel_id"] = rec.id
                occasionel_line.create(cr,uid,data)
                data = {}
                
        return True
    
    def file_parsing_stagiaire(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid,ids, context=context):
            cr.execute(""" delete from ir_personnel_stagiaire where personnel_id='%s' """ % rec.id)
        stagiaire_line = self.pool.get('ir.personnel.stagiaire')
        data_table = self.read(cr, uid, ids[0],  context=context)

        bal_field=data_table['file_data_stagiaire']
        if not bal_field:
            raise osv.except_osv(('Erreur!'), ("Veuillez indiquer le fichier CSV !"))
        data_bal=base64.decodestring(bal_field)
        if data_bal:
            reader = data_bal.split('\n')
            data = {}
            i = 0
            for row in reader:
                i += 1
                if i == 1:
                    continue
                line = row.split(';')
                if len(line) == 1:
                    continue
                empty_row = True
                for l in line:
                    if l.strip():
                        empty_row = False
                        break
                if empty_row:
                    continue
                
                data["nom"] = line[0]
                data["prenom"] = line[1]                       
                data["adressePersonnelle"] = line[2]
                data["numCNI"] = line[3]
                data["numCE"] = line[4]
                data["numCNSS"] = line[5]
                data["ifu"] = line[6]
                data["mtBrutTraitementSalaire"] = line[7]
                data["mtBrutIndemnites"] = line[8]
                data["mtRetenues"] = line[9]
                data["mtRevenuNetImposable"] = line[10]
                data["periode"] = line[11]
                data["personnel_id"] = rec.id
                stagiaire_line.create(cr,uid,data)
                data = {}
        return True
    
    """ MAJ 3.0 """
    def file_parsing_doctorant(self):
        for rec in self:
            cr.execute(""" delete from ir_personnel_doctorant where personnel_id='%s' """ % rec.id)
        doctorant_line = self.pool.get('ir.personnel.doctorant')
        data_table = self.read(cr, uid, ids[0],  context=context)

        bal_field=data_table['file_data_doctorant']
        if not bal_field:
            raise osv.except_osv(('Erreur!'), ("Veuillez indiquer le fichier CSV !"))
        data_bal=base64.decodestring(bal_field)
        if data_bal:
            reader = data_bal.split('\n')
            data = {}
            i = 0
            for row in reader:
                i += 1
                if i == 1:
                    continue
                line = row.split(';')
                if len(line) == 1:
                    continue
                empty_row = True
                for l in line:
                    if l.strip():
                        empty_row = False
                        break
                if empty_row:
                    continue
                
                data["nom"] = line[0]
                data["prenom"] = line[1]                       
                data["adressePersonnelle"] = line[2]
                data["numCNI"] = line[3]
                data["numCE"] = line[4]
                data["mtBrutIndemnites"] = line[5]
                data["personnel_id"] = rec.id
                doctorant_line.create(data)
                data = {}
        return True
    """"""""""""""""""
    
    def file_parsing_recap(self):
        for rec in self:
            cr.execute(""" delete from ir_recapitulatif where personnel_id='%s' """ % rec.id)
        recapitulatif_line = self.pool.get('ir.recapitulatif')
        recapitulatif_line_detail = self.pool.get('ir.paiement.detail')
        data_table = self.read(cr, uid, ids[0],  context=context)
        bal_field=data_table['file_data_recap']
        if not bal_field:
            raise osv.except_osv(('Erreur!'), ("Veuillez indiquer le fichier CSV !"))
        data_bal=base64.decodestring(bal_field)
        if data_bal:
            reader = data_bal.split('\n')
            data = {}
            data_line = {}
            i = 0
            for row in reader:
                i += 1
                if i == 1:
                    continue
                line = row.split(';')
                if len(line) == 1:
                    continue
                empty_row = True
                for l in line:
                    if l.strip():
                        empty_row = False
                        break
                if empty_row:
                    continue
                data["mois"] = line[0]
                data["totalVersement"] = line[1]                       
                data["dateDerniereVersment"] = line[2]
                data["personnel_id"] = rec.id
                recap = recapitulatif_line.create(cr,uid,data)
                data_line["totalVerse"] = line[3]
                data_line["totalVerse"] = line[4]
                data_line["principal"] = line[5]
                data_line["penalite"] = line[6]
                data_line["majorations"] = line[7]
                data_line["dateVersement"] = line[8]
                ref_paiement_id = None
                if line[9] == 'espece':
                    ref_paiement_id = self.pool.get('ir.mode.paiement').search(cr,uid,[('code','=','ES')],limit=1)
                if line[9] == 'cheque':
                    ref_paiement_id = self.pool.get('ir.mode.paiement').search(cr,uid,[('code','=','CH')],limit=1)
                if line[9] == 'telepaiement':
                    ref_paiement_id = self.pool.get('ir.mode.paiement').search(cr,uid,[('code','=','SIR')],limit=1)
                if ref_paiement_id:
                    data_line["refMoyenPaiement"] = ref_paiement_id[0]
                data_line["numQuittance"] = line[10]
                data_line["recap_id"] = recap
                recapitulatif_line_detail.create(cr,uid,data_line)
                data = {}

        return True
    
    def generate_head(self):
        for rec in self:
            model_id = rec.company_ids[0].identifiantFiscal
            doc = etree.Element("TraitementEtSalaire", nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance'})
            id = etree.SubElement(doc, "identifiantFiscal")
            if model_id:
                id.text = str(model_id.encode('windows-1252'))
            else:
                raise ValidationError(_(u"Merci de configurer l'identifiant fiscal." ))
            nom = etree.SubElement(doc, "nom")
            nom.text = str(rec.nom or "")
            prenom = etree.SubElement(doc, "prenom")
            prenom.text = rec.prenom or ""
            raisonSociale = etree.SubElement(doc, "raisonSociale")
            raisonSociale.text = "ATLAS SERVAIR"
            exerciceFiscalDu = etree.SubElement(doc, "exerciceFiscalDu")
            exerciceFiscalDu.text = str(rec.date_from or "")
            exerciceFiscalAu = etree.SubElement(doc, "exerciceFiscalAu")
            exerciceFiscalAu.text = str(rec.date_to or "")
            annee = etree.SubElement(doc, "annee")
            annee.text = str(rec.annee or "")
            commune = etree.SubElement(doc, "commune")
            code = etree.SubElement(commune,'code')
            if rec.commune:
                code.text = str(rec.commune.code or "")
            adresse = etree.SubElement(doc, "adresse")
            country = ""
            if rec.company_ids[0].country_id:
                country = rec.company_ids[0].country_id.name
            adresse.text = str(str(rec.company_ids[0].street or "") + " " + str(rec.company_ids[0].street2 or "") + " " + str(rec.company_ids[0].city or "") + " " + str(rec.company_ids[0].zip or "") + " " + str(country))
            numeroCIN = etree.SubElement(doc, "numeroCIN")
            numeroCIN.text = str(rec.company_ids[0].numeroCIN or "")
            numeroCNSS = etree.SubElement(doc, "numeroCNSS")
            numeroCNSS.text = str(rec.company_ids[0].numeroCNSS or "")
            numeroCE = etree.SubElement(doc, "numeroCE")
            numeroCE.text = str(rec.company_ids[0].numeroCE or "")
            numeroRC = etree.SubElement(doc, "numeroRC")
            numeroRC.text = str(rec.company_ids[0].numeroRC or "")
            identifiantTP = etree.SubElement(doc, "identifiantTP")
            identifiantTP.text = str(rec.company_ids[0].vat or "")
            numeroFax = etree.SubElement(doc, "numeroFax")
            numeroFax.text = str(rec.company_ids[0].phone or "")
            numeroTelephone = etree.SubElement(doc, "numeroTelephone")
            numeroTelephone.text = str(rec.company_ids[0].phone or "")
            email = etree.SubElement(doc, "email")
            email.text = str(rec.company_ids[0].email or "")
            
            effectifTotal = etree.SubElement(doc, "effectifTotal")
            effectifTotal.text = str(rec.effectifTotal or "")
            nbrPersoPermanent = etree.SubElement(doc, "nbrPersoPermanent")
            nbrPersoPermanent.text = str(rec.nbrPersoPermanent or "")
            nbrPersoOccasionnel = etree.SubElement(doc, "nbrPersoOccasionnel")
            nbrPersoOccasionnel.text = str(rec.nbrPersoOccasionnel or "0")
            nbrStagiaires = etree.SubElement(doc, "nbrStagiaires")
            nbrStagiaires.text = str(rec.nbrStagiaires or "0")
            totalMtRevenuBrutImposablePP = etree.SubElement(doc, "totalMtRevenuBrutImposablePP")
            totalMtRevenuBrutImposablePP.text = str("{0:.2f}".format(float(rec.totalMtRevenuBrutImposablePP)) or "")
            totalMtRevenuNetImposablePP = etree.SubElement(doc, "totalMtRevenuNetImposablePP")
            totalMtRevenuNetImposablePP.text = str("{0:.2f}".format(float(rec.totalMtRevenuNetImposablePP)) or "")
            totalMtTotalDeductionPP = etree.SubElement(doc, "totalMtTotalDeductionPP")
            totalMtTotalDeductionPP.text = str("{0:.2f}".format(float(rec.totalMtTotalDeductionPP)) or "")
            totalMtIrPrelevePP = etree.SubElement(doc, "totalMtIrPrelevePP")
            totalMtIrPrelevePP.text = str("{0:.2f}".format(float(rec.totalMtIrPrelevePP)) or "")
            totalMtBrutSommesPO = etree.SubElement(doc, "totalMtBrutSommesPO")
            totalMtBrutSommesPO.text = str("{0:.2f}".format(float(rec.totalMtBrutSommesPO)) or "")
            totalIrPrelevePO = etree.SubElement(doc, "totalIrPrelevePO")
            totalIrPrelevePO.text = str("{0:.2f}".format(float(rec.totalIrPrelevePO)) or "")
            totalMtBrutTraitSalaireSTG = etree.SubElement(doc, "totalMtBrutTraitSalaireSTG")
            totalMtBrutTraitSalaireSTG.text = str("{0:.2f}".format(float(rec.totalMtBrutTraitSalaireSTG)) or "")
            totalMtBrutIndemnitesSTG = etree.SubElement(doc, "totalMtBrutIndemnitesSTG")
            totalMtBrutIndemnitesSTG.text = str("{0:.2f}".format(float(rec.totalMtBrutIndemnitesSTG)) or "")
            totalMtRetenuesSTG = etree.SubElement(doc, "totalMtRetenuesSTG")
            totalMtRetenuesSTG.text = str("{0:.2f}".format(float(rec.totalMtRetenuesSTG)) or "")
            totalMtRevenuNetImpSTG = etree.SubElement(doc, "totalMtRevenuNetImpSTG")
            totalMtRevenuNetImpSTG.text = str("{0:.2f}".format(float(rec.totalMtRevenuNetImpSTG)) or "")
            totalSommePayeRTS = etree.SubElement(doc, "totalSommePayeRTS")
            totalSommePayeRTS.text = str("{0:.2f}".format(float(rec.totalSommePayeRTS)) or "")
            totalmtAnuuelRevenuSalarial = etree.SubElement(doc, "totalmtAnuuelRevenuSalarial")
            totalmtAnuuelRevenuSalarial.text = str("{0:.2f}".format(float(rec.totalmtAnuuelRevenuSalarial)) or "")
            totalmtAbondement = etree.SubElement(doc, "totalmtAbondement")
            totalmtAbondement.text = str("{0:.2f}".format(float(rec.totalmtAbondement)) or "")
            montantPermanent = etree.SubElement(doc, "montantPermanent")
            montantPermanent.text = str("{0:.2f}".format(float(rec.montantPermanent)) or "")
            montantOccasionnel = etree.SubElement(doc, "montantOccasionnel")
            montantOccasionnel.text = str("{0:.2f}".format(float(rec.montantOccasionnel)) or "")
            montantStagiaire = etree.SubElement(doc, "montantStagiaire")
            montantStagiaire.text = str("{0:.2f}".format(float(rec.montantStagiaire)) or "")
            referenceDeclaration = etree.SubElement(doc, "referenceDeclaration")
            referenceDeclaration.text = str("{0:.2f}".format(float(rec.referenceDeclaration)) or "")
        return doc
    
    def generate_ir_xml(self):
        
        doc = self.generate_head()
        listPersonnelPermanent = etree.SubElement(doc, "listPersonnelPermanent")
        """ MAJ 3.0 """
        listPersonnelExonere = etree.SubElement(doc, "listPersonnelExonere")
        """"""""""""""""""
        listPersonnelOccasionnel = etree.SubElement(doc, "listPersonnelOccasionnel")
        listStagiaires = etree.SubElement(doc, "listStagiaires")
        """ MAJ 3.0 """
        listDoctorants = etree.SubElement(doc, "listDoctorants")
        """"""""""""""""""
        listBeneficiaires = etree.SubElement(doc, "listBeneficiaires")
        listBeneficiairesPlanEpargne = etree.SubElement(doc, "listBeneficiairesPlanEpargne")
        listVersements = etree.SubElement(doc, "listVersements")
        for rec in self:
            for line in rec.pp_lines:
                PersonnelPermanent = line.generate_xml()
                listPersonnelPermanent.append(PersonnelPermanent)
            for line in rec.pe_lines:
                PersonnelExonere = line.generate_xml()
                listPersonnelExonere.append(PersonnelExonere)
            for line in rec.po_lines:
                PersonnelOccasionnel = line.generate_xml()
                listPersonnelOccasionnel.append(PersonnelOccasionnel)
            for line in rec.ps_lines:
                stagiaire = line.generate_xml()
                listStagiaires.append(stagiaire)
            for line in rec.pd_lines:
                Doctorants = line.generate_xml()
                listDoctorants.append(Doctorants)
            for line in rec.pb_lines:
                PersonnelBeneficiaire = line.generate_xml()
                listBeneficiaires.append(PersonnelBeneficiaire)
            for line in rec.pbe_lines:
                PersonnelBeneficiaireepargne = line.generate_xml()
                listBeneficiairesPlanEpargne.append(PersonnelBeneficiaireepargne)
            for line in rec.recapitulatif_lines:
                recap = line.generate_xml()
                listVersements.append(recap)
                
        xml_data = "%s" % (etree.tostring(doc, pretty_print = True, xml_declaration = True, encoding='UTF-8').decode())
        
        return self.write({'output': base64.b64encode(xml_data.encode("utf-8")), 'output_name': 'edi.xml'})


class IrPersonnel(models.AbstractModel):
    
    _rec_name = "nom"
    _name = "ir.personnel"
      
    nom = fields.Char('Nom', required=True)
    prenom = fields.Char(u'Prénom', required=True)
    adressePersonnelle = fields.Char('Adresse', size=128, required=True)
    numCNI = fields.Char('CNI', size=64, required=True)
    numCE = fields.Char('Carte de sejour', size=64)
    ifu = fields.Char('Identifiant fiscal', size=64)
    numCNSS = fields.Char('CNSS', size=64)
    irPreleve = fields.Float('I.R. Prélevé')
    mtBrutTraitementSalaire = fields.Float('Montant brut des traitements, salaires et émoluments')
    mtRevenuNetImposable = fields.Float('Montant du revenu net imposable')
    periode = fields.Float('Periode')
    
    def generate_xml(self, element):
        PersonnelPermanent = etree.Element(element, nsmap={})
        for rec in self:
            nom = etree.SubElement(PersonnelPermanent, "nom")
            nom.text = str(rec.nom or "")
            prenom = etree.SubElement(PersonnelPermanent, "prenom")
            prenom.text = rec.prenom or ""
            adressePersonnelle = etree.SubElement(PersonnelPermanent, "adressePersonnelle")
            adressePersonnelle.text = rec.adressePersonnelle or ""
            numCNI = etree.SubElement(PersonnelPermanent, "numCNI")
            numCNI.text = str(rec.numCNI or "")
            numCE = etree.SubElement(PersonnelPermanent, "numCE")
            numCE.text = str(rec.numCE or "")
            
            ifu = etree.SubElement(PersonnelPermanent, "ifu")
            ifu.text = str(rec.ifu or "")
            numCNSS = etree.SubElement(PersonnelPermanent, "numCNSS")
            numCNSS.text = str(rec.numCNSS or "")
            irPreleve = etree.SubElement(PersonnelPermanent, "irPreleve")
            irPreleve.text = str(rec.irPreleve or "0.00")
            mtBrutTraitementSalaire = etree.SubElement(PersonnelPermanent, "mtBrutTraitementSalaire")
            mtBrutTraitementSalaire.text = str("{0:.2f}".format(float(rec.mtBrutTraitementSalaire)) or "")
            mtRevenuNetImposable = etree.SubElement(PersonnelPermanent, "mtRevenuNetImposable")
            mtRevenuNetImposable.text = str(rec.mtRevenuNetImposable or "")
            periode = etree.SubElement(PersonnelPermanent, "periode")
            periode.text = str(rec.periode or "")
        return PersonnelPermanent
    
class IrPersonnelPermanant(models.Model):
    
    _inherit = 'ir.personnel'
    _name = "ir.personnel.permanant"
        
    personnel_id = fields.Many2one('ir.declaration', 'Declaration')
    numPPR = fields.Char('PPR')
    mtExonere = fields.Float('Montant des éléments exonérés')
    mtEcheances = fields.Float('Montant des échéances prélevées')
    nbrReductions = fields.Integer('Nombre de réductions pour Charges de famille')
    salaireBaseAnnuel = fields.Float('Salaire de base annuel')
    mtIndemnite = fields.Float('Montant des indemnités versées à titre de frais professionnels')
    mtAvantages = fields.Float('Montant des avantages en argent ou en nature')
    mtRevenuBrutImposable = fields.Float('Montant du revenu brut imposable')
    mtFraisProfess = fields.Float('Montant des frais professionnels')
    mtCotisationAssur = fields.Float('Montant des cotisations d\'assurance retraites')
    mtAutresRetenues = fields.Float('Montants des autres retenues')
    mtTotalDeduction = fields.Float('Total des déductions sur revenu')
    casSportif = fields.Boolean('Spécification du cas sportif')
    numMatricule = fields.Char('Matricule', size=128)
    datePermis = fields.Date('Date du permis')
    dateAutorisation = fields.Date('Date de l\'autorisation de construire')
    refSituationFamiliale = fields.Many2one('ir.situation.famille', 'Situation de famille')
    refTaux = fields.Many2one('ir.taux.frais', 'Taux des frais professionnels')
    element_exonere_ids = fields.One2many('ir.personnel.permanant.element.exonere', 'ir_personnel_permanant_id', 'Eléments exonérés d’un personnel permanent')
        
    
    def generate_xml(self, element="PersonnelPermanent"):
        doc = super(IrPersonnelPermanant, self).generate_xml(element)
        for rec in self:
            numPPR = etree.SubElement(doc, "numPPR")
            numPPR.text = str(rec.numPPR or "")
            """ MAJ 3.0 """
            salaireBaseAnnuel = etree.SubElement(doc, "salaireBaseAnnuel")
            salaireBaseAnnuel.text =  str("{0:.2f}".format(float(rec.salaireBaseAnnuel)) or "")
            """"""""""""""""""
            mtExonere = etree.SubElement(doc, "mtExonere")
            mtExonere.text = str("{0:.2f}".format(float(rec.mtExonere)) or "")
            mtEcheances = etree.SubElement(doc, "mtEcheances")
            mtEcheances.text = str("{0:.2f}".format(float(rec.mtEcheances)) or "")
            nbrReductions = etree.SubElement(doc, "nbrReductions")
            nbrReductions.text = str(rec.nbrReductions or "")
            mtIndemnite = etree.SubElement(doc, "mtIndemnite")
            mtIndemnite.text = str("{0:.2f}".format(float(rec.mtIndemnite)) or "")
            mtAvantages = etree.SubElement(doc, "mtAvantages")
            mtAvantages.text = str("{0:.2f}".format(float(rec.mtAvantages)) or "")
            mtRevenuBrutImposable = etree.SubElement(doc, "mtRevenuBrutImposable")
            mtRevenuBrutImposable.text = str("{0:.2f}".format(float(rec.mtRevenuBrutImposable)) or "")
            mtFraisProfess = etree.SubElement(doc, "mtFraisProfess")
            mtFraisProfess.text = str("{0:.2f}".format(float(rec.mtFraisProfess)) or "")
            mtCotisationAssur = etree.SubElement(doc, "mtCotisationAssur")
            mtCotisationAssur.text = str("{0:.2f}".format(float(rec.mtCotisationAssur)) or "")
            mtAutresRetenues = etree.SubElement(doc, "mtAutresRetenues")
            mtAutresRetenues.text = str("{0:.2f}".format(float(rec.mtAutresRetenues)) or "")
            mtTotalDeduction = etree.SubElement(doc, "mtTotalDeduction")
            mtTotalDeduction.text = str("{0:.2f}".format(float(rec.mtTotalDeduction)) or "")
            casSportif = etree.SubElement(doc, "casSportif")
            if rec.casSportif:
                casSportif.text = "1"
            else:
                casSportif.text = "0"
            numMatricule = etree.SubElement(doc, "numMatricule")
            numMatricule.text = str(rec.numMatricule or "")
            datePermis = etree.SubElement(doc, "datePermis")
            datePermis.text = str(rec.datePermis or "")
            dateAutorisation = etree.SubElement(doc, "dateAutorisation")
            dateAutorisation.text = str(rec.dateAutorisation or "")
            refSituationFamiliale = etree.SubElement(doc, "refSituationFamiliale")
            codeFamille = etree.SubElement(refSituationFamiliale, "code")
            if rec.refSituationFamiliale:
                codeFamille.text = str(rec.refSituationFamiliale.code or "")
            refTaux = etree.SubElement(doc, "refTaux")
            codeTaux = etree.SubElement(refTaux, "code")
            if rec.refTaux:
                codeTaux.text = str(rec.refTaux.code or "")
            listElementsExonere = etree.SubElement(doc, "listElementsExonere")
            for line in rec.element_exonere_ids:
                ElementExonerePP = etree.SubElement(listElementsExonere, "ElementExonerePP")
                montantExonere = etree.SubElement(ElementExonerePP, "montantExonere")
                montantExonere.text = str("{0:.2f}".format(float(line.montantExonere)) or "")
                refNatureElementExonere = etree.SubElement(ElementExonerePP, "refNatureElementExonere")
                code = etree.SubElement(refNatureElementExonere, "code")
                code.text = str(line.ir_element_exonere_id.code or "")
        return doc

""" MAJ 3.0 """
class IrPersonnelExonere(models.Model):
    
    _inherit = 'ir.personnel'
    _name = "ir.personnel.exonere"
    
    personnel_id = fields.Many2one('ir.declaration', 'Declaration')
    dateRecrutement = fields.Date('Date recrutement')
    mtIndemniteArgentNature = fields.Float('Montant brut des indemnités payées en argent ou en nature')
    mtIndemniteFraisPro = fields.Float('Montant des indemnités versées à titre de frais professionnels')
    mtRevenuBrutImposable = fields.Integer('Montant du revenu brut imposable')
    mtRetenuesOperees = fields.Integer('Montant des retenues opérées')
    
    def generate_xml(self,element="PersonnelExonere"):
        context.update({'irPreleve':False})
        doc = super(ir_personnel_exonere, self).generate_xml(element)
        for rec in self.browse(cr, uid, ids, context=context):
            dateRecrutement = etree.SubElement(doc, "dateRecrutement")
            dateRecrutement.text = str(rec.dateRecrutement or "")
            mtIndemniteArgentNature = etree.SubElement(doc, "mtIndemniteArgentNature")
            mtIndemniteArgentNature.text =  str("{0:.2f}".format(float(rec.mtIndemniteArgentNature)) or "")
            mtIndemniteFraisPro = etree.SubElement(doc, "mtIndemniteFraisPro")
            mtIndemniteFraisPro.text = str("{0:.2f}".format(float(rec.mtIndemniteFraisPro)) or "")
            mtRevenuBrutImposable = etree.SubElement(doc, "mtRevenuBrutImposable")
            mtRevenuBrutImposable.text = str("{0:.2f}".format(float(rec.mtRevenuBrutImposable)) or "")
            mtRetenuesOperees = etree.SubElement(doc, "mtRetenuesOperees")
            mtRetenuesOperees.text = str("{0:.2f}".format(float(rec.mtRetenuesOperees)) or "")
        return doc
""""""""""""""""""

class IrPersonnelOccasionel(models.Model):
    
    _inherit = 'ir.personnel'
    _name = "ir.personnel.occasionel"
    
    personnel_id = fields.Many2one('ir.declaration', 'Declaration')
    mtBrutSommes = fields.Float('Montant brut des sommes payées')
    profession = fields.Char('Profession')
    
    def generate_xml(self, element="PersonnelOccasionnel"):
        context.update({'numCNSS':False, 'mtBrutTraitementSalaire':False, 'mtRevenuNetImposable':False, 'periode':False})
        doc = super(ir_personnel_occasionel, self).generate_xml(element)
        for rec in self.browse(cr, uid, ids, context=context):
            mtBrutSommes = etree.SubElement(doc, "mtBrutSommes")
            mtBrutSommes.text = str("{0:.2f}".format(float(rec.mtBrutSommes)) or "")
            profession = etree.SubElement(doc, "profession")
            profession.text = rec.profession or ""
                       
        return doc
    
class IrPersonnelStagiaire(models.Model):
    
    _inherit = 'ir.personnel'
    _name = "ir.personnel.stagiaire"
            
    personnel_id = fields.Many2one('ir.declaration', 'Declaration')
    mtBrutIndemnites = fields.Float('Montant brut des indemnités payées en argent ou en nature')
    mtRetenues = fields.Float('Montant des retenues opérées')

    def generate_xml(self,element="Stagiaire"):
        context.update({'irPreleve':False})
        doc = super(ir_personnel_stagiaire, self).generate_xml(element)
        for rec in self.browse(cr, uid, ids, context=context):
            mtBrutIndemnites = etree.SubElement(doc, "mtBrutIndemnites")
            mtBrutIndemnites.text = str("{0:.2f}".format(float(rec.mtBrutIndemnites)) or "")
            mtRetenues = etree.SubElement(doc, "mtRetenues")
            mtRetenues.text = str("{0:.2f}".format(float(rec.mtRetenues)) or "")
                       
        return doc
    
class IrPersonnelBeneficiare(models.Model):
    
    _inherit = 'ir.personnel'
    _name = "ir.personnel.beneficiare"
    
    personnel_id = fields.Many2one('ir.declaration', 'Declaration')
    organisme =  fields.Char('organisme', size=64)
    nbrActionsAcquises = fields.Integer('Nombre d\'actions acquises')
    nbrActionsDistribuees = fields.Integer('Nombre d\'actions distribuées gratuitement')
    prixAcquisition = fields.Float('Prix d\'acquisition')
    valeurActionAttribution = fields.Float('Valeur de l\'action à la date d\'attribution')
    valeurActionLeveeOption = fields.Float('Valeur de l\'action à la date de levée d\'option')
    mtAbondement = fields.Float('Montant de l\'abondement')
    nbrActionsCedees = fields.Integer('Nombre d\'actions cédées')
    complementSalaire = fields.Float('Complément de salaire')
    dateAttribution = fields.Date('Date d\'attribution')
    dateLeveOption = fields.Date('Date de la levée d\'option')
    dateCession = fields.Date('Date de cession')
    
    def generate_xml(self,element="Beneficiaire"):
        context.update({'irPreleve':False, 'mtBrutTraitementSalaire':False, 'mtRevenuNetImposable':False, 'periode':False})
        doc = super(ir_personnel_beneficiare, self).generate_xml(element)
        for rec in self.browse(cr, uid, ids, context=context):
            organisme = etree.SubElement(doc, "organisme")
            organisme.text = str(rec.organisme or "")
            nbrActionsAcquises = etree.SubElement(doc, "nbrActionsAcquises")
            nbrActionsAcquises.text = str(rec.nbrActionsAcquises or "")
            nbrActionsDistribuees = etree.SubElement(doc, "nbrActionsDistribuees")
            nbrActionsDistribuees.text = str(rec.nbrActionsDistribuees or "")
            prixAcquisition = etree.SubElement(doc, "prixAcquisition")
            prixAcquisition.text = str("{0:.2f}".format(float(rec.prixAcquisition)) or "")
            valeurActionAttribution = etree.SubElement(doc, "valeurActionAttribution")
            valeurActionAttribution.text = str("{0:.2f}".format(float(rec.valeurActionAttribution)) or "")
            valeurActionLeveeOption = etree.SubElement(doc, "valeurActionLeveeOption")
            valeurActionLeveeOption.text = str("{0:.2f}".format(float(rec.valeurActionLeveeOption)) or "")
            mtAbondement = etree.SubElement(doc, "mtAbondement")
            mtAbondement.text = str("{0:.2f}".format(float(rec.mtAbondement)) or "")
            nbrActionsCedees = etree.SubElement(doc, "nbrActionsCedees")
            nbrActionsCedees.text = str(rec.nbrActionsCedees or "")
            complementSalaire = etree.SubElement(doc, "complementSalaire")
            complementSalaire.text = str("{0:.2f}".format(float(rec.complementSalaire)) or "")
            dateAttribution = etree.SubElement(doc, "dateAttribution")
            dateAttribution.text = str(rec.dateAttribution or "")
            dateLeveOption = etree.SubElement(doc, "dateLeveOption")
            dateLeveOption.text = str(rec.dateLeveOption or "")
            dateCession = etree.SubElement(doc, "dateCession")
            dateCession.text = str(rec.dateCession or "")
            
        return doc

class IrPersonnelBeneficiareEpargne(models.Model):
    
    _inherit = 'ir.personnel'
    _name = "ir.personnel.beneficiare.epargne"
    
    personnel_id = fields.Many2one('ir.declaration', 'Declaration')
    commune = fields.Many2one('ir.ville', 'Ville')
    numPlan = fields.Char('Numéro du plan', size=64)
    duree = fields.Integer('Durée (en anneés)')
    dateOuverture = fields.Date('Date d’ouverture')
    mtAbondement = fields.Float('Montant de l’abondement versé')
    mtAnuuelRevenuSalarial = fields.Float('Montant annuel du revenu salarial imposable')
  
    
    def generate_xml(self, element="BeneficiairePlanEpargne"):
        context.update({'ifu':False, 'numCNSS':False, 'irPreleve':False, 'mtBrutTraitementSalaire':False, 'mtRevenuNetImposable':False, 'periode':False})
        doc = super(ir_personnel_beneficiare_epargne, self).generate_xml(element)
        for rec in self.browse(cr, uid, ids, context=context):
            commune = etree.SubElement(doc, "commune")
            code = etree.SubElement(commune, "code")
            if rec.commune:
                code.text = str(rec.commune.code)
            numPlan = etree.SubElement(doc, "numPlan")
            numPlan.text = str(rec.numPlan or "")
            duree = etree.SubElement(doc, "duree")
            duree.text = str(rec.duree or "")
            dateOuverture = etree.SubElement(doc, "dateOuverture")
            dateOuverture.text = str(rec.dateOuverture or "")
            mtAbondement = etree.SubElement(doc, "mtAbondement")
            mtAbondement.text = str("{0:.2f}".format(float(rec.mtAbondement)) or "")
            mtAnuuelRevenuSalarial = etree.SubElement(doc, "mtAnuuelRevenuSalarial")
            mtAnuuelRevenuSalarial.text = str("{0:.2f}".format(float(rec.mtAnuuelRevenuSalarial)) or "")
        return doc
        
""" MAJ 3.0 """
class IrPersonnelDoctorant(models.Model):
    
    _inherit = 'ir.personnel'
    _name = "ir.personnel.doctorant"
    
    personnel_id = fields.Many2one('ir.declaration', 'Declaration')
    mtBrutIndemnites = fields.Float('Montant brut des indemnités payées en argent ou en nature')
    
    def generate_xml(self, element="Doctorant"):
        context.update({'ifu':False, 'numCNSS':False, 'irPreleve':False, 'mtBrutTraitementSalaire':False, 'mtRevenuNetImposable':False, 'periode':False})
        doc = super(ir_personnel_doctorant, self).generate_xml(element)
        for rec in self.browse(cr, uid, ids, context=context):
            mtBrutIndemnites = etree.SubElement(doc, "mtBrutIndemnites")
            mtBrutIndemnites.text =  str("{0:.2f}".format(float(rec.mtBrutIndemnites)) or "")
        return doc
""""""""""""""""""

class IrPersonnelPermanantElementExonere(models.Model):
    _name = "ir.personnel.permanant.element.exonere"
    
    ir_personnel_permanant_id = fields.Many2one('ir.personnel.permanant', 'Personnel permanent')
    ir_element_exonere_id = fields.Many2one('ir.element.exonere', 'Elément exonéré')
    montantExonere = fields.Float('Montant exonéré')
    
class IrRecapitulatif(models.Model):
    
    _name = "ir.recapitulatif"
    
    personnel_id = fields.Many2one('ir.declaration', 'Declaration')
    mois = fields.Integer('Mois')
    totalVersement = fields.Float('Total de versement par mois')
    dateDerniereVersment = fields.Date('Date du dernier versement')
    details = fields.One2many('ir.paiement.detail', 'recap_id', 'détails des paiements du mois')
    
    
    def generate_xml(self):
        
        VersementTraitementSalaire = etree.Element("VersementTraitementSalaire", nsmap={})
        for rec in self.browse(cr, uid, ids, context=context):
            mois = etree.SubElement(VersementTraitementSalaire, "mois")
            mois.text = str(rec.mois or "")
            totalVersement = etree.SubElement(VersementTraitementSalaire, "totalVersement")
            totalVersement.text = str("{0:.2f}".format(float(rec.totalVersement)) or "")
            dateDerniereVersment = etree.SubElement(VersementTraitementSalaire, "dateDerniereVersment")
            dateDerniereVersment.text = str(rec.dateDerniereVersment or "")
            listDetailPaiement = etree.SubElement(VersementTraitementSalaire, "listDetailPaiement")
            for line in rec.details:
                DetailPaiementTraitementSalaire = etree.SubElement(listDetailPaiement, "DetailPaiementTraitementSalaire")
                reference = etree.SubElement(DetailPaiementTraitementSalaire, "reference")
                reference.text = str(line.reference or "")
                totalVerse = etree.SubElement(DetailPaiementTraitementSalaire, "totalVerse")
                totalVerse.text = str("{0:.2f}".format(float(line.totalVerse)) or "")
                principal = etree.SubElement(DetailPaiementTraitementSalaire, "principal")
                principal.text = str("{0:.2f}".format(float(line.principal)) or "")
                penalite = etree.SubElement(DetailPaiementTraitementSalaire, "penalite")
                penalite.text = str("{0:.2f}".format(float(line.penalite)) or "")
                majorations = etree.SubElement(DetailPaiementTraitementSalaire, "majorations")
                majorations.text = str("{0:.2f}".format(float(line.majorations)) or "")
                dateVersement = etree.SubElement(DetailPaiementTraitementSalaire, "dateVersement")
                dateVersement.text = str(line.dateVersement or "")
                refMoyenPaiement = etree.SubElement(DetailPaiementTraitementSalaire, "refMoyenPaiement")
                code = etree.SubElement(refMoyenPaiement, "code")
                if line.refMoyenPaiement:
                    code.text = str(line.refMoyenPaiement.code or "")
                numQuittance = etree.SubElement(DetailPaiementTraitementSalaire, "numQuittance")
                numQuittance.text = str(line.numQuittance or "")
            
        return VersementTraitementSalaire
    
class IrPaiementDetail(models.Model):
    
    _name = "ir.paiement.detail"

    recap_id = fields.Many2one('ir.recapitulatif', 'Recp ID', ondelete='cascade')
    reference = fields.Char('Référence')
    totalVerse = fields.Float('Total versé')
    principal = fields.Float('Principal')
    penalite = fields.Float('Pénalité (10%)')
    majorations = fields.Float('Majoration (5%+0.5%)')
    dateVersement = fields.Date('Date de versement')
    refMoyenPaiement = fields.Many2one('ir.mode.paiement', 'Mode paiement')
    numQuittance = fields.Char('Numéro de quittance', size=64)
    

class ResCompany(models.Model):
    
    _inherit = 'res.company'
    
    identifiantFiscal = fields.Char('Identifiant fiscal')
    numeroCIN = fields.Char('Numéro CIN')
    numeroCNSS = fields.Char('Numéro CNSS')
    numeroCE = fields.Char('Numéro CE')
    numeroRC = fields.Char('Numéro RC')
