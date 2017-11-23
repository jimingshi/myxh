# -*- coding: utf-8 -*-
{
    'name': "import_account_move_csv",

    'summary': """
        Imports some account move and account move line from a csv
       """,

    'description': """
        This modules allows to import account move lines from a csv file 
        (the separator has to be the comma, and the delimiter has to be the double quote)
        There must be no blank field.
        Each line of the csv represent and account.move.line
        the first line must be:
        DATE	JAL	COMPTE	PCE	LIBELLE	DEBIT	CREDIT
        For each line:
        DATE is the date in DD/MM/YYYY format
        JAL is the code of the journal
        COMPTE is the account.account number
        PCE is a key per account move, to identify to which account move and account move line belongs
        LIBELLE is the name of the line
        DEBIT is the amount of debit 
        CREDIT is the amount of credi
    """,

    'author': "Auneor Conseil",
    'website': "http://www.auneor-conseil.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}
