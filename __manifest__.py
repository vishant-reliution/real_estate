# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Real Estate',
    'version': '1.0.0.0',
    'category': '',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_view.xml',
        'views/property_types_view.xml',
        'views/property_tags_view.xml',
        'views/property_offer_views.xml',
    ],
    'installable': True,
    'auto_install': False,

    'license': 'LGPL-3',
}