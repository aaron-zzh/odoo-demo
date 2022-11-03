# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = '房产类型'
    _order = 'sequence, id'
    _sql_constraints = [
        ('check_name', 'UNIQUE(name)', 'The name must be unique'),
    ]

    name = fields.Char('名称', required=True)
    property_ids = fields.One2many('estate.property', 'type_id', string='房屋')
    offer_ids = fields.One2many('estate.property.offer', 'property_type_id', string='报价单')
    offer_count = fields.Integer('报价数量', compute='_compute_offer_count')
    property_count = fields.Integer('房屋数量', compute='_compute_property_count')

    # 排序
    sequence = fields.Integer()

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for r in self:
            r.offer_count = len(r.offer_ids)

    # ========优化=========
    def _compute_property_count(self):
        '''仅演示, 更推荐通过反向o2m字段计算 len(property_ids)'''
        if self.ids:
            domain = [('type_id', 'in', self.ids)]
            counts_data = self.env['estate.property'].read_group(domain, ['type_id'], ['type_id'])
            mapped_data = {
                count['type_id'][0]: count['type_id_count'] for count in counts_data
            }
        else:
            mapped_data = {}
        for record in self:
            record.property_count = mapped_data.get(record.id, 0)

    def action_offer_list(self):
        return {
            'name': '报价单列表',
            'view_mode': 'tree,form',
            'domain': [('property_type_id', '=', self.id)],
            'res_model': 'estate.property.offer',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False},
        }
