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
    _name = "estate.property"
    _description = "Details of estate property"
    _order = "id desc"

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
    property_type_id = fields.Many2one("property_types", string="Property Type")
    salesman_id = fields.Many2one("res.partner", "Salesman")
    buyer_id = fields.Many2one("res.partner", "Buyer")
    tag_ids = fields.Many2many("property.tags")
    offer_ids = fields.One2many("property.offer", "property_id")
    total_area = fields.Integer(string="Total Area(sqm)", compute="_compute_area")
    best_price = fields.Float(string="Best Price", compute="_compute_best_price", store=True)
    status = fields.Char(string="Status", readonly=True, default='New')
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancel', 'Canceled')
    ], default='new', string="State")

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
            if rec.offer_ids:
                rec.best_price = max(rec.offer_ids.mapped("price"))

    def cancel_status_exception(self):
        raise UserError(_("Canceled properties cannot be sold."))

    def sold_status_exception(self):
        raise UserError(_("Sold properties cannot be canceled"))

    def action_sold(self):
        if self.status == 'New' or self.status == 'Sold' or self.status == 0:
            self.status = 'Sold'
            self.state = 'sold'
        else:
            self.cancel_status_exception()

    def action_cancel(self):
        if self.status == 'New' or self.status == 'Canceled' or self.status == 0:
            self.status = 'Canceled'
            self.state = 'cancel'
        else:
            self.sold_status_exception()

    _sql_constraints = [
        ('expected_price_check', 'CHECK (expected_price>0)', 'Expected price must be strictly positive'),
        ('selling_price_check', 'CHECK (selling_price>=0)', 'Selling price must be positive'),
    ]

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self.offer_ids:
            if record.status == 'accepted':
                if self.selling_price < (0.90 * self.expected_price):
                    raise ValidationError(_('The selling price must be at least of 90% of the expected price if you '
                                            'want to accept the offer.'))

    @api.onchange('offer_ids')
    def _offer_receive(self):
        for rec in self.offer_ids:
            if rec.price:
                self.state = 'offer_received'
            else:
                self.state = 'new'
