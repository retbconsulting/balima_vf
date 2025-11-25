# -*- encoding: utf-8 -*-

from odoo import fields, models

class e_bds_sortant(models.Model):
    
    _name = "e_bds.sortant"

    name = fields.Many2one('date.range', string=u'Période',required=True)
    e_bds_sortant_line_ids = fields.One2many('e_bds.sortant.line','e_bds_sortant_id',string=u'e_bds_sortant_line')


class e_bds_sortant_line(models.Model):
    
    _name = "e_bds.sortant.line"
    
    employee_id = fields.Many2one('hr.employee', string=u'Employé', required=True)
    situation = fields.Selection([('SO', 'Sortant'),
                                               ('DE', 'Decédé'),
                                               ('IT', 'Maternité'),
                                               ('IL', 'Maladie'),
                                               ('AT', 'Accident de Travail'),
                                               ('CS', 'Congé Sans salaire'),
                                               ('MS', 'Maintenu Sans Salaire'),
                                               ('MP', 'Maladie Professionnelle')], string=u'Situation')
    e_bds_sortant_id = fields.Many2one('e_bds.sortant', u'e_bds_sortant')


class hr_payroll_ma_bulletin(models.Model):
    
    _inherit = "hr.payroll_ma.bulletin" 

    normal = fields.Boolean(string=u'Normal')