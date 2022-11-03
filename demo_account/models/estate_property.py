# -*- coding: utf-8 -*-

from odoo import api, fields, models, Command
from odoo.exceptions import AccessError, UserError, ValidationError


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    def action_sold(self):
        for r in self:
            journal_type = self.env.context.get('journal_type', 'sale')
            journal = self.env['account.journal'].sudo().search([
                ('type', '=', journal_type),
                ('company_id', '=', self.env.company.id)
            ], limit=1)
            print(" reached ".center(100, '='))
            # 以编程方式进行安全检查，防止无相关权限人员误操作
            if not self.env['account.move'].check_access_rights('create', False):
                try:
                    print("account.move create right error".center(100, '='))
                    self.check_access_rights('write')
                    self.check_access_rule('write')
                except AccessError:
                    return False

            self.env['account.move'].sudo().with_context(default_move_type='out_invoice').create({
                'partner_id': r.buyer_id.id,
                'journal_id': journal.id,
                'invoice_line_ids': [
                    Command.create({
                        'name': r.name,
                        'quantity': 1,
                        'price_unit': r.selling_price,
                    })
                ],
            })
        return super().action_sold()
