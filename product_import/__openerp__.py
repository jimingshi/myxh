# -*- coding: utf-8 -*-
{
    'name': 'product_import',  # 模块名
    'description': '产品导入',  # 注释
    'author': 'Gala',  # 作者
    'website': '',  # 网站
    'category': 'other',  # 分类
    'version': '1.0',  # 版本号
    'depends': [
        'sale',
        'product',
    ],  # 依赖
    'data': [

        'models/product_import.xml',
        'models/product_product_import.xml',
        'models/product_template_import.xml',
        'models/stock_inventory_import.xml',

    ],
    'qweb': [
        # 'static/src/xml/*.xml',
    ],
    'auto_install': False,  # 是否自动安装
    'installable': True,  # 是否可安装
}
