# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _
from odoo.tools.mail import is_html_empty
from odoo.tools import (
    format_date,
)


class ChangeSalesman(models.TransientModel):
    _name = 'estate.property.change'
    _description = '修改经纪人'

    salesman_id = fields.Many2one('res.users', '经纪人')
    reason = fields.Html('变更原因', sanitize=True)

    def action_change(self):
        self.ensure_one()
        properties = self.env['estate.property'].browse(self.env.context.get('active_ids'))
        if not is_html_empty(self.reason):
            # 跟踪字段变更日志
            properties._track_set_log_message(
                '<div style="margin-bottom: 4px;"><p>%s:</p>%s<br /></div>' % ('变更原因', self.reason)
            )
            # 测试发送消息
            msg = '房产经纪人变更日期：%s' % format_date(self.env, fields.Date.today())
            properties.message_post(body=msg)
        res = properties.action_set_salesman(salesman_id=self.salesman_id.id)
        return res
