# -*- encoding: utf-8 -*-

from odoo import fields, models
from datetime import date
import base64

class HrPayrollMa(models.Model):
    
    _inherit = "hr.payroll_ma"

    hr_ir_id = fields.Many2one(comodel_name="ir.declaration", string=u'CIMR')
    
class HrEmployee(models.Model):
    
    _inherit = "hr.employee"

    ir_situation_famille = fields.Many2one(comodel_name="ir.situation.famille", string=u'Situation familiale')
    ir_taux_frais = fields.Many2one(comodel_name="ir.taux.frais", string=u'Taux professionnel')
    casSportif = fields.Boolean(string="Cas sportif")
    datePermis = fields.Date(string="Date permis")
    dateAutorisation = fields.Date(string="Date autorisation")