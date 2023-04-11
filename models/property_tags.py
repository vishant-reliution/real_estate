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

class PropertyTags(models.Model):
    _name = "property.tags"
    _description = "List of property tags"

    name = fields.Char(string="Name", required=True)

    _sql_constraints = [
        ('tag_unique', 'UNIQUE(name)', 'Property Tag must be Unique.')
    ]