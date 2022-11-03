# -*- coding: utf-8 -*-

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = '房产'
    _order = 'id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', '期望价格必须大于0')
        # ('check_selling_price', 'CHECK(selling_price > 0)', '销售价格必须大于0'),
    ]

    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)

    company_id = fields.Many2one('res.company', string='所属公司', required=True, default=lambda self: self.env.company)
    name = fields.Char('名称', required=True, default='未知', help='这是名称字段')

    description = fields.Text('描述')
    postcode = fields.Char('邮编')
    date_availability = fields.Date('有效期', copy=False, default=lambda self: self._default_date_availability)
    expected_price = fields.Float('期望价格', required=True)
    selling_price = fields.Float('销售价格', readonly=True, copy=False)
    bedrooms = fields.Integer('卧室数量')
    living_area = fields.Integer('面积')
    facades = fields.Integer('门窗')
    garage = fields.Boolean('车库')
    garden = fields.Boolean('花园')
    garden_area = fields.Integer('花园面积')
    garden_orientation = fields.Selection([
        ('north', '北向'),
        ('south', '南向'),
        ('east', '东向'),
        ('west', '西向')], string='朝向', default='north')
    active = fields.Boolean('有效', default=True)
    state = fields.Selection([
        ('new', '新建'),
        ('receive', '收到'),
        ('accept', '确认'),
        ('sold', '已售出'),
        ('canceled', '已废弃')], string='状态', default='new')

    # 关联字段
    type_id = fields.Many2one('estate.property.type', string='类型')
    tag_ids = fields.Many2many('estate.property.tag', string='标签')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='报价')
    salesman_id = fields.Many2one('res.users', string='经纪人', default=lambda self: self.env.user, tracking=True)
    buyer_id = fields.Many2one('res.partner', string='客户', readonly=True, copy=False, tracking=True)

    # 计算字段
    best_price = fields.Float('最高报价', compute='_compute_best_price')
    total_area = fields.Integer('总面积', compute='_compute_total_area')

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for r in self:
            r.total_area = r.living_area + r.garden_area

    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for r in self:
            r.best_price = max(r.offer_ids.mapped('price')) if r.offer_ids else False

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False
            # return {'warning': {
            #     'title': '提醒',
            #     'message': ('onchange 后端提示')}}

    # ---------------------------------------- Action Methods -------------------------------------
    # def action_sold(self):
    #     for r in self:
    #         if r.state == 'canceled':
    #             raise UserError('已废弃，无法销售！')
    #         else:
    #             r.state = 'sold'

    def action_sold(self):
        if 'canceled' in self.mapped('state'):
            raise UserError('已废弃，无法销售！')
        return self.write({'state': 'sold'})

    def action_cancel(self):
        if 'sold' in self.mapped('state'):
            raise UserError('已销售，无法废弃！')
        return self.write({'state': 'canceled'})

    def action_property_list(self):
        return {
            'name': '房产列表',
            'view_mode': 'tree,form',
            'domain': [('postcode', '=', self.postcode)],
            'res_model': 'estate.property',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False},
        }

    def action_set_salesman(self, salesman_id):
        return self.write({'salesman_id': salesman_id})

    # ------------------------------------------ CRUD Methods -------------------------------------
    # @api.ondelete(at_uninstall=False)
    # def _unlink_check(self):
    #     for r in self:
    #         if r.state not in ['new', 'canceled']:
    #             raise UserError('仅可删除状态为'新建'或'废弃'的房产')
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_canceled(self):
        if not set(self.mapped('state')) <= {'new', 'canceled'}:
            raise UserError('Only new and canceled properties can be deleted.')
