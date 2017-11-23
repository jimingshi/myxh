# coding:utf-8
import psycopg2
import psycopg2.extras


def execute_sql(sql_str):
    conn = psycopg2.connect(database="sw", user="coc", password="admin")
    cur = conn.cursor()
    # cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(sql_str)
    datas = cur.fetchall()

    cur.close()
    conn.close()
    return datas


def start():
    datas = execute_sql('select employee_id from hr_attendance group by employee_id order by employee_id')
    res = {}
    for [i] in datas:
        print 'begin: ', i
        res[i] = get_a(i)

    print 'end'


def get_a(eid):
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


if __name__ == '__main__':
    datas = start()

'''
1、获取某个用户的所有考勤
2、按签入签出时间排序
3、两两组合
4、输出不规范考勤
'''
