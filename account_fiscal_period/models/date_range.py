# -*- coding: utf-8 -*-

from odoo import models, fields, api

from datetime import datetime
from dateutil.relativedelta import relativedelta


class DateRange(models.Model):
    _inherit = "date.range"

    period_ids = fields.One2many(comodel_name="date.range",
                                 inverse_name="fiscal_year_id",
                                 string="Périodes", required=False)
    fiscal_year_id = fields.Many2one(comodel_name="date.range",
                                     string="Exercice fiscal", required=False)
    fiscal_period = fields.Boolean(related='type_id.fiscal_period', store=True)

    def create_period3(self, context):
        return self.create_period(context, 3)

    def create_period(self, context, interval=1):

        period_obj = self.env['date.range']
        for fy in self:
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            date_stop = datetime.strptime(fy.date_end, '%Y-%m-%d')

            while ds.strftime('%Y-%m-%d') < fy.date_end:
                de = ds + relativedelta(months=interval, days=-1)
                if date_stop < de:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')
                period_obj.create({
                    'name': ds.strftime('%m/%Y'),
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_end': de.strftime('%Y-%m-%d'),
                    'type_id': self.env.ref('account_fiscal_period\
                                .fiscalperiod').id,
                    'fiscal_year_id': fy.id,
                })
                ds = ds + relativedelta(months=interval)
        return True
