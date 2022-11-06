# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare
from odoo.exceptions import ValidationError, UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = '报价'
    _order = 'price desc'

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The price must be strictly positive'),
    ]

    price = fields.Float('出价', required=True)
    validity = fields.Integer(string='有效期（天）', default=7)
    status = fields.Selection([
        ('accepted', '已接受'),
        ('refused', '已拒绝')], string='状态')
    partner_id = fields.Many2one('res.partner', string='客户')
    property_id = fields.Many2one('estate.property', string='房产')
    user_id = fields.Many2one('res.users', string='经纪人',
                              compute='_compute_user_id',
                              store=True, readonly=False,
                              precompute=True, index=True)
    property_type_id = fields.Many2one(related='property_id.type_id', store=True)

    # Computed
    date_deadline = fields.Date(string='截止日期', compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    # ---------------------------------------- Compute methods ------------------------------------
    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.date_deadline = date + relativedelta(days=offer.validity)

    def _inverse_date_deadline(self):
        for offer in self:
            date = offer.create_date.date() if offer.create_date else fields.Date.today()
            offer.validity = (offer.date_deadline - date).days

    # ----------------------------------- Constrains and Onchanges --------------------------------
    @api.constrains('price')
    def _check_price(self):
        for record in self:
            if float_compare(record.price, record.property_id.expected_price*0.9, 2) < 0:
                raise ValidationError('报价不能低于期望价格的90%')

    @api.depends('partner_id')
    def _compute_user_id(self):
        for order in self:
            if not order.user_id:
                order.user_id = order.partner_id.user_id or order.partner_id.commercial_partner_id.user_id or self.env.user

    def action_accept(self):
        if 'accepted' in self.mapped('property_id.offer_ids.status'):
            raise UserError('An offer as already been accepted.')
        self.write({
            'status': 'accepted',
        })
        return self.mapped('property_id').write({
            'state': 'accept',
            'selling_price': self.price,
            'buyer_id': self.partner_id.id,
        })

    # def action_refuse(self):
    #     for r in self:
    #         r.status = 'refused'

    def action_refuse(self):
        return self.write({
            'status': 'refused',
        })

    # @api.model 注解是必须的，其他CRUD方法可以没有
    @api.model
    def create(self, vals):
        # Do some business logic, modify vals...
        if vals.get('property_id'):
            property = self.env['estate.property'].browse(vals['property_id'])

            if property and property.best_price and vals['price'] < property.best_price:
                raise ValidationError('报价不能低于%0.2f' % property.best_price)

        # Then call super to execute the parent method，在 python3 中等同 super(TestModel, self).
        return super().create(vals)
