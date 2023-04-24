# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty, float_utils, float_compare

from odoo.addons.payment import utils as payment_utils


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        res = super(EstateProperty, self).action_sold()
        selling_price = self.selling_price
        admin_fee = 100.00
        line_1_name = 'Sale Commission'
        line_2_name = 'Administrative Fees'
        line_1_qty = line_2_qty = 1.0
        line_1_price = selling_price * 0.06
        line_2_price = admin_fee
        values = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': line_1_name,
                    'quantity': line_1_qty,
                    'price_unit': line_1_price,
                }),
                (0, 0, {
                    'name': line_2_name,
                    'quantity': line_2_qty,
                    'price_unit': line_2_price,
                })
            ],
        }
        self.env['account.move'].create(values)
        return res