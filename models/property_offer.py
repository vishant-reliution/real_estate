# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime, timedelta
from itertools import groupby
import json

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.osv import expression
from odoo.tools import float_is_zero, html_keep_url, is_html_empty

from odoo.addons.payment import utils as payment_utils
from datetime import date
from dateutil import relativedelta
class PropertOffer(models.Model):
    _name = 'property.offer'
    _description = 'List of offers'

    price = fields.Float(string="Price")
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], copy=False, string="Status")
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property")
    validity = fields.Integer(string="Validity", compute="_compute_validity", store=True)
    date_deadline = fields.Date(string="Deadline")

    @api.depends('date_deadline')
    def _compute_validity(self):
        for rec in self:
            create_date = date.today()
            # rec.validity = rec.date_deadline.day - create_date.day
            rec.validity = create_date - relativedelta.relativedelta(days=rec.date_deadline)