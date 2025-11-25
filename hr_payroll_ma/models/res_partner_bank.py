# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class ResPartnerBank(models.Model):

    _inherit = 'res.partner.bank'

    is_bank_for_payroll = fields.Boolean(string="Compte paie")
