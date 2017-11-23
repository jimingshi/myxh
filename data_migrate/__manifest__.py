# -*- coding: utf-8 -*-
{
    'name': 'data migrate',
    'version': '1.0',
    'category': 'tools',
    'sequence': 200,
    'summary': '从odoo8中迁移数据',
    'description': """
    从odoo8中迁移数据
    """,
    'website': 'http://zwg.store:8072',
    'depends': ['base'],
    'data': [
        'views/data_migrate_view.xml',
        # 'views/hr_employee_view.xml',
    ],
    'demo': [

    ],
    'css': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
