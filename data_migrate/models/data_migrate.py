# coding:utf-8
import psycopg2
import psycopg2.extras
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class data_migrate(models.Model):
    _name = 'data.migrate'
    _description = u'升级入口'

    name = fields.Char()

    @api.multi
    def btn_res_company_base(self):
        datas = execute_sql('''SELECT id, name, partner_id, currency_id, rml_footer, create_date, rml_header,
            rml_paper_format, write_uid, logo_web, font, account_no,
            parent_id, email, create_uid, custom_footer, phone, rml_header2,
            rml_header3, write_date, rml_header1, company_registry, paperformat_id
        FROM public.res_company;''')

        for data in datas:
            vals = {
                'name': data[1],
                # 'partner_id': data[2],
                # 'currency_id': data[3],
                'rml_footer': data[4],
                # 'create_date': data[5],
                'rml_header': data[6],
                'rml_paper_format': data[7],
                # 'write_uid': data[8],
                'logo_web': data[9],
                'font': data[10],
                'account_no': data[11],
                # 'parent_id': data[12],
                'email': data[13],
                # 'create_uid': data[14],
                'custom_footer': data[15],
                'phone': data[16],
                'rml_header2': data[17],
                'rml_header3': data[18],
                # 'write_date': data[19],
                'rml_header1': data[20],
                'company_registry': data[21],
                # 'paperformat_id': data[22],
            }

            # 通过id_dict判断是否已导入
            ys = self.env['id.dict'].search([('old_model', '=', 'res.company'), ('old_id', '=', data[0])])
            if not ys:
                if data[0] == 1:
                    self.env['res.company'].browse(1).write(vals)
                    new_id = 1
                else:
                    new_id = self.env['res.company'].create(vals).id

                self.env['id.dict'].create({
                    'old_model': 'res.company',
                    'old_id': data[0],
                    'now_model': 'res.company',
                    'now_id': new_id
                })

        print 233

    @api.multi
    def btn_res_users_base(self):
        datas = execute_sql(
            'select a.id,b.name,a.active,a.login,a.password,a.signature,a.password_crypt from res_users a,res_partner b where b.id = a.partner_id')

        for data in datas:
            if data[3] in ['portaltemplate', "public"]:
                print 'continue', data
                continue

            vals = {
                'name': data[1],
                'active': data[2],
                'login': data[3],
                'password': data[4],
                'signature': data[5],
                'password_crypt': data[6],
                'tz': 'Asia/Shanghai',

            }
            ys = self.env['id.dict'].search([('old_model', '=', 'res.users'), ('old_id', '=', data[0])])
            if not ys:
                if data[0] == 1:
                    del vals['password_crypt']
                    del vals['password']
                    self.env['res.users'].browse(1).write(vals)
                    new_id = 1
                else:
                    print vals
                    new_id = self.env['res.users'].create(vals).id

                self.env['id.dict'].create({
                    'old_model': 'res.users',
                    'old_id': data[0],
                    'now_model': 'res.users',
                    'now_id': new_id
                })

    @api.multi
    def btn_hr_employee_base(self):
        datas = execute_sql('''SELECT a.id,a.marital, a.identification_id, a.work_phone, a.mobile_phone,
                        a.birthday,a.work_email, a.work_location, a.gender, b.name,b.company_id,b.active,b.user_id
                        FROM hr_employee a,resource_resource b where a.resource_id = b.id;''')

        for data in datas:
            if data[0] == 1:
                self.env['id.dict'].create({
                    'old_model': 'hr.employee',
                    'old_id': 1,
                    'now_model': 'hr.employee',
                    'now_id': 1
                })
                continue

            # 通过id_dict判断是否已导入
            ys = self.env['id.dict'].search([('old_model', '=', 'hr.employee'), ('old_id', '=', data[0])])
            if not ys:
                vals = {
                    'marital': data[1],
                    'identification_id': data[2],
                    'work_phone': data[3],
                    'mobile_phone': data[4],
                    'birthday': data[5],
                    'work_email': data[6],
                    'work_location': data[7],
                    'gender': data[8],
                    'name': data[9],
                    'company_id': self.env['id.dict'].get_now_id('res.company', data[10]),
                    'active': data[11],
                    'user_id': self.env['id.dict'].get_now_id('res.users', data[12])
                }
                new_id = self.env['hr.employee'].create(vals).id
                self.env['id.dict'].create({
                    'old_model': 'hr.employee',
                    'old_id': data[0],
                    'now_model': 'hr.employee',
                    'now_id': new_id
                })

    @api.multi
    def btn_res_partner(self):
        self._cr.execute("select old_id from id_dict where old_model = 'res.partner'")
        already = [i for (i,) in self._cr.fetchall()]

        datas = execute_sql("select id,name from res_partner where is_company ='t'")
        for id, name in datas:
            if id not in already:
                already.append(id)
                self.env['id.dict'].create({
                    'old_model': 'res.partner',
                    'old_id': id,
                    'now_model': 'res.partner',
                    'now_id': self.env['res.partner'].create({'name': name, 'is_company': True}).id
                })

    @api.multi
    def btn_tb_res_partner(self):
        id_dict = {}
        for pid, uid in execute_sql("select a.id,b.id from res_partner a,res_users b where a.id = b.partner_id"):
            id_dict[self.env['id.dict'].get_now_id('res.users', uid)] = {'opid': pid}
        if False in id_dict: del id_dict[False]

        self._cr.execute("select a.id,b.id from res_partner a,res_users b where a.id = b.partner_id")
        for pid, uid in self._cr.fetchall():
            if uid in id_dict:
                id_dict[uid]['npid'] = pid

        for pid, cid in execute_sql('select a.id,b.id from res_partner a,res_company b where a.id = b.partner_id'):
            id_dict[self.env['id.dict'].get_now_id('res.company', cid)] = {'opid': pid}
        self._cr.execute("select a.id,b.id from res_partner a,res_company b where a.id = b.partner_id")
        for pid, cid in self._cr.fetchall():
            id_dict[cid]['npid'] = pid

        for i in id_dict:
            if not self.env['id.dict'].get_now_id('res.partner', id_dict[i]['opid']):
                self.env['id.dict'].create({
                    'old_model': 'res.partner',
                    'old_id': id_dict[i]['opid'],
                    'now_model': 'res.partner',
                    'now_id': id_dict[i]['npid']
                })

        print id_dict

    @api.multi
    def btn_hr_attendance(self):
        gl_partner_dict = {}
        datas = execute_sql('select employee_id from hr_attendance group by employee_id order by employee_id')
        res = {}
        for [i] in datas:
            print 'begin: ', i
            res[i] = get_hr_attendance_datas(i)

        for oeid in res:
            eid = self.env['id.dict'].get_now_id('hr.employee', oeid)
            uid = self.env['hr.employee'].browse(eid).user_id.id
            print uid
            for i in res[oeid]:
                data = res[oeid][i]
                data['employee_id'] = eid

                oid1 = data['in_id']
                del data['in_id']

                oid2 = False
                if 'out_id' in data:
                    oid2 = data['out_id']
                    del data['out_id']

                if data['check_in_address'] not in gl_partner_dict:
                    gl_partner_dict[data['check_in_address']] = self.env['id.dict'].get_now_id('res.partner',
                                                                                               data['check_in_address'])
                data['check_in_address'] = gl_partner_dict[data['check_in_address']]

                if 'check_out_address' in data:
                    if data['check_out_address'] not in gl_partner_dict:
                        gl_partner_dict[data['check_out_address']] = self.env['id.dict'].get_now_id('res.partner',
                                                                                                    data[
                                                                                                        'check_out_address'])
                    data['check_out_address'] = gl_partner_dict[data['check_out_address']]

                now_id = self.env['hr.attendance'].sudo(uid).create(data).id
                self.env['id.dict'].create({
                    'old_model': 'hr.attendance',
                    'old_id': oid1,
                    'now_model': 'hr.attendance',
                    'now_id': now_id
                })
                if oid2:
                    self.env['id.dict'].create({
                        'old_model': 'hr.attendance',
                        'old_id': oid2,
                        'now_model': 'hr.attendance',
                        'now_id': now_id
                    })
        print 'end'


def execute_sql(sql_str):
    conn = psycopg2.connect(database="sw", user="coc", password="admin")
    # cur = conn.cursor()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute(sql_str)
    datas = cur.fetchall()

    cur.close()
    conn.close()
    return datas


def get_hr_attendance_datas(eid):
    datas = execute_sql(
        'select name,action,sign_flag,address,id from hr_attendance where employee_id = %s order by name' % eid)
    gl, i, tag = {}, 0, 'in'

    for data in datas:
        if data[1] == 'sign_in':
            if tag == 'in':
                gl[i] = {
                    'check_in': data[0],
                    'check_in_way': data[2],
                    'check_in_address': data[3],
                    'in_id': data[4]
                }
                tag = 'out'
        elif data[1] == 'sign_out':
            if tag == 'out':
                gl[i].update({
                    'check_out': data[0],
                    'check_out_way': data[2],
                    'check_out_address': data[3],
                    'out_id': data[4]
                })
                i += 1
                tag = 'in'

    return gl
