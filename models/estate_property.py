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

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Details of estate property"

    name = fields.Char(string="Name", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(string="Available From", copy=False)
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", copy=False, readonly=True)
    bedrooms = fields.Integer(string="Bedrooms", default="2")
    living_area = fields.Integer(string="Living Area(sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area(sqm)")
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string='Garden Orientation')
    property_type_id = fields.Integer(string="Property ID")
    salesman_id = fields.Many2one("res.partner", "Salesman")
    buyer_id = fields.Many2one("res.partner", "Buyer")
    tag_ids = fields.Many2many("property.tags")
    offer_ids = fields.One2many("property.offer", "property_id")
    total_area = fields.Integer(string="Total Area(sqm)", compute="_compute_area")
    best_price = fields.Float(string="Best Price", compute="_compute_best_price", store=True)

    @api.onchange('garden')
    def _onchange_garden(self):
        for rec in self:
            if rec.garden:
                rec.garden_area = '10'
                rec.garden_orientation = 'north'
            else:
                rec.garden_area = ''
                rec.garden_orientation = ''

    @api.depends('living_area', 'garden_area')
    def _compute_area(self):
        for rec in self:
            rec.total_area = rec.garden_area + rec.living_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for rec in self:
            if rec.offer_ids.price:
                print("before list")
                # price_list = list(rec.offer_ids.price)
                print("after list")
                rec.best_price = rec.offer_ids.price
                print("after 1st price assign as a best price")
                rec.best_price = max(rec.offer_ids.price)
                print("after max function")