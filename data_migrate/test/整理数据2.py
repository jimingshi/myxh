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
    datas = execute_sql('select name,action from hr_attendance where employee_id = %s order by name' % eid)
    gl = {}
    i = 0
    tag = 'in'
    action = None
    for data in datas:
        if data[1] == 'sign_in':
            if tag == 'in':
                gl[i] = {}
                gl[i]['in'] = data[0]
                tag = 'out'
            else:
                print '1111', data
        elif data[1] == 'sign_out':
            if tag == 'out':
                gl[i]['out'] = data[0]
                i += 1
                tag = 'in'
            else:
                print '2222', data
        elif data[1] == 'action':
            action = data
            print '2333', data
        else:
            print '99999999999', data

    for i in gl:
        if 'out' in gl[i]:
            sec = (gl[i]['out'] - gl[i]['in']).seconds
            if sec > 72000:
                print 'err2', gl[i]  # 签入签出间隔超过一天
        else:
            gl[i]['out'] = False

    return gl


if __name__ == '__main__':
    # print execute_sql('select * from res_company')
    datas = start()

'''
1、获取某个用户的所有考勤
2、按签入签出时间排序
3、两两组合
4、输出不规范考勤
'''
