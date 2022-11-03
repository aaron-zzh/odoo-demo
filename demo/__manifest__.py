# -*- coding: utf-8 -*-
{
    'name': 'Demo',
    'version': '0.1',
    'summary': 'Odoo 模块开发示例',
    'description': 'Odoo 模块开发示例',
    'author': 'AaronZZH',
    'website': 'https://www.xuejiai.com',
    'category': 'XUEJI/demo',
    # 依赖的其他模块
    'depends': ['base', 'mail'],
    # 主数据-安装或升级时加载
    'data': [
        'security/ir.model.access.csv',
        'security/demo_security.xml',

        'data/estate_property_data.xml',

        'wizard/change_salesman_wizard_views.xml',

        'views/estate_property_offer_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_views.xml',
        'views/res_users_views.xml',
        'views/menu_actions.xml',

        "report/estate_property_reports.xml",
        "report/estate_property_templates.xml",
    ],
    # 演示数据
    'demo': [
        'demo/demo_data.xml',
    ],
    'auto_install': False,
    'application': True,
    'installable': True,
    'license': 'LGPL-3',
}
