# -*- coding: utf-8 -*-
{
    'name': 'Demo Account',
    'version': '0.1',
    'summary': 'Odoo 模块开发示例- Link Module',
    'description': 'Odoo 模块开发示例',
    'author': 'AaronZZH',
    'website': 'https://www.xuejiai.com',
    'category': 'XUEJI/demo',
    # 依赖的其他模块
    'depends': ['demo', 'account'],
    'data': [
        # 'security/ir.model.access.csv',
        "report/estate_property_templates.xml",
    ],
    'auto_install': False,
    'application': False,
    'installable': True,
    'license': 'LGPL-3',
}
