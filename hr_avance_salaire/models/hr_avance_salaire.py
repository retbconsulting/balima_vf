# -*- encoding: utf-8 -*-

from odoo import fields, models,api
import datetime, calendar
import base64
from odoo.exceptions import UserError, ValidationError

class pret_dans_ligne_rubrique(models.Model):
    
    _inherit = 'hr.payroll_ma.ligne_rubrique'
    
    employee_pret_id = fields.Many2one(comodel_name = 'hr.avance.salaire')


class HrAvanceSalaire(models.Model):
    
        _name = 'hr.avance.salaire'
        
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
        
        pr_employe = fields.Many2one('hr.employee',string="Employé", required=True, default=_employee_get)
        pr_montant = fields.Float(string="Montant", required=True)
        pr_rubrique = fields.Many2one('hr.payroll_ma.rubrique', string="Rubrique", required=True, default=_rubrique_get)
        pr_frequence = fields.Selection(selection='get_nbr_echeances',string="Nombre d'échéances", required=True)
        pr_mois_debut = fields.Date(string="Mois de début", required=True)
        pr_montant_paye = fields.Float(compute='calcul_montant_paye',string="Montant payé",store=True)
        pr_montant_restant = fields.Float(compute='calcul_montant_paye',string="Montant restant",store=True)
        rubrique_line_ids = fields.One2many(comodel_name = 'hr.payroll_ma.ligne_rubrique' , inverse_name = 'employee_pret_id' )
        pr_echeance_ids = fields.One2many('hr.avance.salaire.line','id_pret', string="Echéances")
        state = fields.Selection(selection=(('draft','Brouillon'),('en_cours',u'En cours'),('applied',u'Appliquée'),('canceled',u'Annulée')),default='draft')
        
        def annuler_echeance(self):
            l_contrat = self.env['hr.payroll_ma.ligne_rubrique']
            for rec in self:
                l_contrat.search([('employee_pret_id','=',rec.id)]).unlink()
            self.state = 'canceled'
            
        
        def generer_echeances(self):
            ligne_pret = self.env['hr.avance.salaire.line']
            for rec in self:
                mt_echeance = rec.pr_montant / float(rec.pr_frequence)
                mois_ref = rec.pr_mois_debut.split('-',3)[1]
                annee_ref = rec.pr_mois_debut.split('-',3)[0]
                i=0
                for i in range(0,int(rec.pr_frequence)):
                    m = int(mois_ref) + i
                    y = int(annee_ref)
                    if m > 12:
                        m = m - 12
                        y = y + 1
                    reliquat_ech  = rec.pr_montant - ((i+1)*mt_echeance)
                    ligne_pret.create({'id_pret':rec.id,
                                       'reliquat_ech':reliquat_ech,
                                       'montant_ech':mt_echeance,
                                       'date_ech':datetime.date(y, m, 1)})
            self.state = 'en_cours'
        
        
        def appliquer_echeances(self):
            cnt = self.env['hr.version']
            l_contrat = self.env['hr.payroll_ma.ligne_rubrique']
            for rec in self:
                contrat = cnt.search([('employee_id','=',rec.pr_employe.id)])[0]
                mt_echeance = rec.pr_montant / float(rec.pr_frequence)
                mois_ref = rec.pr_mois_debut.split('-',3)[1]
                annee_ref = rec.pr_mois_debut.split('-',3)[0]
                i=0
                for i in range(0,int(rec.pr_frequence)):
                    m = int(mois_ref) + i
                    y = int(annee_ref)
                    if m > 12:
                        m = m - 12
                        y = y + 1
                    dernier_j = calendar.monthrange(y, m)[1]
                    l_contrat.create({'employee_pret_id':rec.id,
                                      'rubrique_id':rec.pr_rubrique.id,
                                      'montant':mt_echeance,
                                      'taux':1,
                                      'date_start':datetime.date(y, m, 1),
                                      'date_stop':datetime.date(y, m, dernier_j),
                                      'id_contract':contrat.id
                                      })
            self.state = 'applied'


        @api.depends('pr_montant_paye','pr_montant_restant')
        def calcul_montant_paye(self):
            cnt = self.env['hr.version']

            for rec in self:
                contrat = cnt.search([('employee_id','=',rec.pr_employe.id)])
                if contrat:
                    l= contrat[0].rubrique_ids
                    date_today = datetime.date.today()
                    for c in l:
                        if c.date_stop:
                            mois_stop = c.date_stop.split('-',3)[1]
                            annee_stop = c.date_stop.split('-',3)[0]
                            stop = str(annee_stop) + str(mois_stop)
                            now = str(date_today.year) + str(date_today.month).rjust(2,'0')
                            if int(c.rubrique_id.id) == rec.pr_rubrique.id:
                                if int(now) >= int(stop):
                                    rec.pr_montant_paye += c.montant

                            rec.pr_montant_restant = rec.pr_montant - rec.pr_montant_paye


        def get_nbr_echeances(self):
            return (
                ('1','1'),
                ('2','2'),
                ('3','3'),
                ('4','4'),
                ('5','5'),
                ('6','6'),
                ('7','7'),
                ('8','8'),
                ('9','9'),
                ('10','10'),
                ('11','11'),
                ('12','12'),)

class HrAvanceSalaireLine(models.Model):
        
        _name = 'hr.avance.salaire.line'

        id_pret = fields.Many2one('hr.avance.salaire')
        date_ech = fields.Date(string="Date")
        montant_ech = fields.Float(string="Montant")
        reliquat_ech = fields.Float(string="Reliquat")
        decaler = fields.Boolean(string="Décaler")
        mois_decalage = fields.Integer(string="Mois décalage")
        period_id = fields.Many2one('date.range', string=u'Période', states={'draft':[('readonly', False)]})

     
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
        period_id = fields.Many2one('account.period', string=u'Période', states={'draft':[('readonly', False)]})
        
