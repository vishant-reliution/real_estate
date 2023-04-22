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


class PropertyTypes(models.Model):
    _name = "property_types"
    _description = "List of property types"
    _order = "name"

    name = fields.Char(required=True)
    property_ids = fields.One2many("estate.property", "property_type_id")
    sequence = fields.Integer(string="Sequence")
    offer_count = fields.Integer(compute="_compute_offer_count")

    @api.depends('name')
    def _compute_offer_count(self):
        for rec in self:
            rec.offer_count = self.env['property.offer'].search_count([('property_id.property_type_id', '=', rec.name)])

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'Property type must be Unique.')
    ]

    def action_view_offers(self):
        return {
            'name': 'Offers',
            'res_model': 'property.offer',
            'view_mode': 'list,form',
            'domain': [("property_id.property_type_id", "=", self.name)],
            'target': 'current',
            'type': 'ir.actions.act_window',
                }
