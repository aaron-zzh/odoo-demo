# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = '房产标签'
    _order = 'name'
    _sql_constraints = [
        ('check_name', 'UNIQUE(name)', 'The name must be unique'),
    ]

    name = fields.Char('名称', required=True)
    color = fields.Integer(string='颜色')
