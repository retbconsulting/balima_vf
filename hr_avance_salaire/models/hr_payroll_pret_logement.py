# -*- encoding: utf-8 -*-

from odoo import fields, models,api
import datetime, calendar
import base64
from odoo.exceptions import ValidationError

class HrPayrollPretLogement(models.Model):
    
        _name = 'hr.payroll.pret.logement'
        
        def _employee_get(self):
            ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
            if ids:
                return ids[0]
            return False
        
        def _rubrique_get(self):
            ids = self.env['hr.payroll_ma.rubrique'].search([('name', '=', 'Avance')])
            if ids:
                return ids[0]
            return False
        
        def appliquer(self):
            return True
        
        def annuler(self):
            return True
        
        prlog_employe = fields.Many2one('hr.employee',string="Employé", required=True, default=_employee_get)
        prlog_montant = fields.Float(string="Somme empruntée", required=True)
        prlog_rubrique = fields.Many2one('hr.payroll_ma.rubrique', string="Rubrique", required=True, default=_rubrique_get)
        prlog_frequence = fields.Integer(string=u"Durée du prêt", required=True)
        prlog_taux = fields.Float(string=u"Taux nominal HT", required=True)
        prlog_mois_debut = fields.Date(string="Mois de début", required=True)
        rubrique_line_ids = fields.One2many(comodel_name = 'hr.payroll_ma.ligne_rubrique' , inverse_name = 'employee_pret_id' )
        fichier_import = fields.Binary(string="Tableau d'amortissement")
        prlog_echeance_ids = fields.One2many('hr.payroll.pret.logement.line','id_pret', string="Echéances")
        state = fields.Selection(selection=(('draft','Brouillon'),('en_cours',u'Echéances en cours'),('applied',u'Appliquée'),('canceled',u'Annulée')),default='draft')
        
        
        def generer_echeances(self):
            for record in self:
                ligne_pret = self.env['hr.payroll.pret.logement.line']
                if not record.fichier_import:
                    raise ValidationError("Erreur! Veuillez indiquer le fichier CSV !")
                fichier_importation_binary = base64.decodestring(record.fichier_import)
                
                if fichier_importation_binary:
                    reader_lines = fichier_importation_binary.split('\n')
                    data = {}
                    i=0
                    for row in reader_lines:
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
                        ligne_pret.create({
                            'id_pret':record.id,
                            'date_ech':line[0],
                            'montant_ech':line[1],
                            'reliquat_ech':line[2],
                            'interet':line[3],                           
                            'reliquat_interet':line[4],                                       
                                       })
            self.state = 'en_cours'
    
            
            
class HrPayrollPretLogementLine(models.Model):
        
        _name = 'hr.payroll.pret.logement.line'

        id_pret = fields.Many2one('hr.payroll.pret.logement')
        reliquat_interet = fields.Float(string="Reliquat Interet")
        interet = fields.Float(string="Interet")
        date_ech = fields.Date(string="Date")
        montant_ech = fields.Float(string="Mensualite")
        reliquat_ech = fields.Float(string="Reliquat")
        decaler = fields.Boolean(string="Décaler")
        mois_decalage = fields.Integer(string="Mois décalage")
        period_id = fields.Many2one('date.range', string=u'Période', states={'draft':[('readonly', False)]})
        
