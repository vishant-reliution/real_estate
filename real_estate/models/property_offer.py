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


class PropertyOffer(models.Model):
    _name = 'property.offer'
    _description = 'List of offers'
    _order = "price desc"

    price = fields.Float(string="Price")
    status = fields.Selection([
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], copy=False, string="Status")
    partner_id = fields.Many2one("res.partner", string="Partner")
    property_id = fields.Many2one("estate.property")
    validity = fields.Integer(string="Validity", compute="_compute_validity", inverse="_inverse_validity", store=True)
    date_deadline = fields.Date(string="Deadline")
    create_date = fields.Date(string='Creation Date', readonly=True, default=fields.Date.today())

    def date_exception(self):
        raise ValidationError(_("You can't enter past dates."))

    @api.depends('date_deadline')
    def _compute_validity(self):
        for rec in self:
            if rec.date_deadline:
                days = rec.date_deadline.day - rec.create_date.day
                months = (rec.date_deadline.month - rec.create_date.month) * 30
                years = (rec.date_deadline.year - rec.create_date.year) * 365
                if rec.date_deadline.year > rec.create_date.year:
                    rec.validity = (days + months + years)
                elif rec.date_deadline.year == rec.create_date.year:
                    if rec.date_deadline.month > rec.create_date.month:
                        rec.validity = (days + months + years)
                    elif rec.date_deadline.month == rec.create_date.month:
                        if rec.date_deadline.day >= rec.create_date.day:
                            rec.validity = (days + months + years)
                        else:
                            rec.date_exception()
                    else:
                        rec.date_exception()
                else:
                    rec.date_exception()
            else:
                rec.validity = '0'

    def _inverse_validity(self):
        for rec in self:
            rec.date_deadline = rec.create_date + timedelta(days=rec.validity)

    def action_accept(self):
        self.status = 'accepted'
        if self.price:
            self.property_id.selling_price = self.price
            self.property_id.buyer_id = self.partner_id
            self.property_id.state = 'offer_accepted'

    def action_refused(self):
        self.status = 'refused'

    # _sql_constraints = [
    #     ('price_check', 'CHECK (price>0)', 'Offer price must be positive.')
    # ]

    @api.constrains('price')
    def _check_price(self):
        for rec in self:
            if rec.price <= 0:
                raise ValidationError(_('Offer price must be strictly positive.'))

    def check_offer_price(self):
        for rec in self.property_id.offer_ids:
            for i in range(len(self.property_id.offer_ids)):
                if str(rec.price)[i + 1] <= str(rec.price)[i]:
                    raise ValidationError(_('offer must be greater than {}'.format(self.property_id.best_price)))

    @api.model
    def create(self, vals):
        res = super(PropertyOffer, self).create(vals)
        offer_record = self.env['estate.property'].browse(vals['property_id'])
        if vals['price'] < offer_record.best_price:
            raise ValidationError(_('offer must be greater than {}'.format(offer_record.best_price)))
        return res
