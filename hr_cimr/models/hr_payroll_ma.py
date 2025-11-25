# -*- encoding: utf-8 -*-

from odoo import fields, models
from datetime import date
import base64

class HrPayrollMa(models.Model):
    
    _inherit = "hr.payroll_ma"

    hr_cimr_id = fields.Many2one(comodel_name="hr.cimr", string=u'CIMR')