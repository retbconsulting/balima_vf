# -*- coding: utf-8 -*-
from odoo import fields, models,api, osv
from . import convertion
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta, date

class payroll(models.Model):
    _inherit = 'hr.payroll_ma'


    total_net_a_payer = fields.Float(string='Total Net à payer',compute='get_total_net_a_payer')
    total_net_a_payer_vrt = fields.Float(string='Total Net à payer (virement)',compute='get_total_net_a_payer_vrt')
    total_net_a_payer_text = fields.Char(compute='change_amount')
    total_net_a_payer_vrt_text = fields.Char(compute='change_amount_vrt')
    total_bordereau_cnss = fields.Float(string='Total paiement CNSS',compute='get_total_bordereau_cnss')
    total_bordereau_cnss_text = fields.Char(compute='change_amount_cnss')
    taux_prestation_AF = fields.Float(string='AF %',compute='get_taux',default=0)
    taux_prestation_sociales = fields.Float(string='prestations sociales',compute='get_taux',default=0)
    taux_tfp = fields.Float(string='% TFP',compute='get_taux',default=0)
    taux_participation_amo = fields.Float(string='% part. AMO',compute='get_taux',default=0)
    taux_cot_amo = fields.Float(string='% cot. AMO',compute='get_taux',default=0)


    def get_taux(self):

        for rec in self:
            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','allocationsFam'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                rec.taux_prestation_AF = cot.tauxpatronal

            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','CNSS'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                rec.taux_prestation_sociales = cot.tauxpatronal + cot.tauxsalarial

            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','formationPro'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                rec.taux_tfp = cot.tauxpatronal

            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','participationAMO'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                rec.taux_participation_amo = cot.tauxpatronal

            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','AMO'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                rec.taux_cot_amo = cot.tauxpatronal + cot.tauxsalarial


    def get_total_bordereau_cnss(self):

        for rec in self:

            taux_plafonne = 0
            taux_non_plafonne = 0

            # On retrouve le taux plafonne
            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','CNSS'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                taux_plafonne = (cot.tauxsalarial + cot.tauxpatronal)

            # On retrouve les taux non plafonnés
            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','allocationsFam'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                taux_non_plafonne += cot.tauxpatronal

            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','formationPro'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                taux_non_plafonne += cot.tauxpatronal

            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','participationAMO'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                taux_non_plafonne += cot.tauxpatronal

            cot = self.env['hr.payroll_ma.cotisation'].search([('code','=','AMO'),('company_id','=',rec.partner_id.company_id.id)],limit=1)
            if cot:
                taux_non_plafonne += (cot.tauxsalarial + cot.tauxpatronal)

            taux_non_plafonne = taux_non_plafonne/100
            taux_plafonne = taux_plafonne/100

            somme_plafonnee = 0
            somme_non_plafonnee = 0
            for bul in rec.bulletin_line_ids:
                for l in bul.salary_line_ids:
                    if l.name=='Cnss':
                        somme_plafonnee += l.base
                        somme_non_plafonnee += bul.salaire_brute_imposable

            rec.total_bordereau_cnss = (somme_non_plafonnee * taux_non_plafonne) + (somme_plafonnee* taux_plafonne)



    @api.depends('total_bordereau_cnss')
    def change_amount_cnss(self):
        self.total_bordereau_cnss_text = convertion.trad(self.total_bordereau_cnss, 'DHS').upper()
        return True


    def get_total_net_a_payer_vrt(self):

        for rec in self:
            somme = 0
            for bul in rec.bulletin_line_ids:

                if bul.employee_id.mode_reglement == 'virement':
                    somme += bul.salaire_net_a_payer

            rec.total_net_a_payer_vrt = somme

    def get_total_net_a_payer(self):

        for rec in self:
            somme = 0
            for bul in rec.bulletin_line_ids:
                somme += bul.salaire_net_a_payer

            rec.total_net_a_payer = somme

    @api.depends('total_net_a_payer')
    def change_amount(self):
        self.total_net_a_payer_text = convertion.trad(self.total_net_a_payer, 'DHS').upper()
        return True

    @api.depends('total_net_a_payer_vrt')
    def change_amount_vrt(self):
        self.total_net_a_payer_vrt_text = convertion.trad(self.total_net_a_payer_vrt, 'DHS').upper()
        return True

class bulletin(models.Model):
        _inherit = 'hr.payroll_ma.bulletin'


        salaire_base_mois = fields.Float(string='Salaire de base du mois', compute='get_base_salary')
        jrs_conges = fields.Float(string='Jours de congé', compute='get_nbr_leaves')
        conges_payes = fields.Float(string='Congés payés')
        cnss = fields.Float(string='CNSS', compute='get_cnss_employee')
        cimr_assurance_amo = fields.Float(string='CIMR/ASS/AMO', compute='get_cimr_assurance_amo')
        hsup_25 = fields.Float(string=u'Heures Sup 25%', compute='get_heures_sup')
        hsup_50 = fields.Float(string=u'Heures Sup 50%', compute='get_heures_sup')
        hsup_100 = fields.Float(string=u'Heures Sup 100%', compute='get_heures_sup')


        def get_heures_sup(self):
            for rec in self:

                rub_hsup_25 = self.env.ref('hr_payroll_ma.hsup_25')
                rub_hsup_50 = self.env.ref('hr_payroll_ma.hsup_50')
                rub_hsup_100 = self.env.ref('hr_payroll_ma.hsup_100')


                # Heures Sup 25%
                lines = self.env['hr.payroll_ma.bulletin.line'].search([('id_bulletin','=',rec.id),('name','like',rub_hsup_25.name)])

                somme = 0
                for line in lines:
                    somme += line.rate_employee

                rec.hsup_25 = somme

                # Heures Sup 50%
                lines = self.env['hr.payroll_ma.bulletin.line'].search([('id_bulletin','=',rec.id),('name','like',rub_hsup_50.name)])

                somme = 0
                for line in lines:
                    somme += line.rate_employee

                rec.hsup_50 = somme

                # Heures Sup 100%
                lines = self.env['hr.payroll_ma.bulletin.line'].search([('id_bulletin','=',rec.id),('name','like',rub_hsup_100.name)])

                somme = 0
                for line in lines:
                    somme += line.rate_employee

                rec.hsup_100 = somme



        @api.depends('salaire_base','working_days')
        def get_base_salary(self):
            for rec in self:
                rec.salaire_base_mois = rec.salaire_base * (rec.working_days/26)


        @api.depends('period_id','employee_id')
        def get_nbr_leaves(self):

            for rec in self:
                #conge_paid = self.env.ref('hr_holidays.holiday_status_cl')
                conge_paid = self.env['hr.leave.type'].search([('name', 'like', 'Congés payés'), ('company_id', '=', rec.employee_id.company_id.id)], limit=1)
                start_date_leaves = rec.period_id.date_start - relativedelta(months=1)
                start_date_leaves = start_date_leaves.replace(day=16)
                end_date_leaves = rec.period_id.date_end
                end_date_leaves = end_date_leaves.replace(day=15)
                delta = timedelta(days=1)
                if rec.period_id.name == "01/2022":
                    somme = 0
                    while start_date_leaves <= end_date_leaves:
                        leaves = self.env['hr.leave'].search([
                            ('employee_id','=',rec.employee_id.id),
                            ('holiday_status_id','in',conge_paid.ids),
                            ('state','=','validate'),
                            ('request_date_from','<=', start_date_leaves),
                            ('request_date_to','>=', start_date_leaves)]
                        )
                        if leaves:
                            somme +=1
                        start_date_leaves += delta
                    '''somme = sum(leave.number_of_days for leave in self.env['hr.leave'].search([('employee_id','=',rec.employee_id.id), 
                                                                                                                         ('state','=','validate'),
                                                                                                                        ('holiday_status_id.code', '=', 'IMP'),
                                                                                                                         ('date_from','>=',rec.date_start),
                                                                                                                        ('date_from','<=',rec.date_end)]))'''
                else:
                    somme = 0
                    leaves = self.env['hr.leave'].search([
                            ('employee_id','=',rec.employee_id.id),
                            ('holiday_status_id','in',conge_paid.ids),
                            ('state','=','validate'),
                            ('request_date_from','<=', end_date_leaves),
                            ('request_date_to','>=', start_date_leaves)]
                        )
                    for leave in leaves:
                        somme += leave.number_of_days
                
                '''somme = 0
                for leave in leaves:
                    #if faut que le mois de la date de debut du conge soit le meme que que le mois de la periode
                    if leave.request_date_from.month==rec.period_id.date_start.month:
                        if leave.request_date_to <=rec.period_id.date_end:
                            somme += leave.number_of_days
                        else:
                            somme += (rec.period_id.date_end - leave.request_date_from).days
                    if leave.request_date_to.month==rec.period_id.date_start.month and leave.request_date_from.month!=rec.period_id.date_start.month:
                        #cas du premier jour de mois
                        if rec.period_id.date_start==leave.request_date_to:
                            somme+=1
                        else:
                            somme += abs((rec.period_id.date_start - leave.request_date_to).days)
                    somme += leave.number_of_days'''
                rec.jrs_conges = somme
                rec.conges_payes = somme

        @api.depends('salaire_net')
        def get_nbr_paid_leaves(self):
            for rec in self:
                rub_paid_leaves = self.env.ref('hr_payroll_ma.jrs_conges_payes')
                lines = self.env['hr.payroll_ma.bulletin.line'].search([('id_bulletin','=',rec.id),('name','=',rub_paid_leaves.name)])
                somme = 0
                for line in lines:
                    somme += line.rate_employee
                #rec.conges_payes = somme


        @api.depends('salaire_net')
        def get_cnss_employee(self):

            for rec in self:
                lines = self.env['hr.payroll_ma.bulletin.line'].search([('id_bulletin','=',rec.id),('name','=','Cnss')])

                somme = 0
                for line in lines:
                    somme += line.subtotal_employee

                rec.cnss = somme


        @api.depends('salaire_net')
        def get_cimr_assurance_amo(self):

            for rec in self:
                lines = self.env['hr.payroll_ma.bulletin.line'].search([('id_bulletin','=',rec.id),('name','in',['Cimr','Amo','Mutuelle'])])

                somme = 0
                for line in lines:
                    somme += line.subtotal_employee

                rec.cimr_assurance_amo = somme
