import pymysql
import settings
import hashlib
import re


def register():
    print("******************开始注册***************")
    username = (input("请输入用户名：")).strip()

    sql0 = "select username from user"
    cursor.execute(sql0)
    usernames = cursor.fetchall()
    if usernames:
        for user in usernames:
            if username == user["username"]:
                print("用户名重复")
                return False

    password = input("请输入密码：")
    email = input("请输入邮箱：")
    user_type = input("请选择用户类型0or1：")
    if not username or not password or not user_type or len(username) < 2:
        print("参数有误")
        return False
    if not username.strip():
        print("用户名格式错误")
        return False

    if user_type not in ("0", "1"):
        print("用户类型错误")
        return False

    if email:
        pa = r"\w[-\w.+]*@([A-Za-z0-9][-A-Za-z0-9]+\.)+[A-Za-z]"
        if not re.match(pa, email):
            print("邮箱格式错误")
            return False

    sql = """INSERT INTO USER(username, password, email,usertype) VALUES ('%s',sha1('%s'),'%s', '%s')""" % (username, password, email, user_type)
    try:
        res = cursor.execute(sql)
        if res:
            conn.commit()
        else:
            conn.rollback()
            return False
    except Exception as e:
        print(e)
        conn.rollback()
        return False
    return True


def login():
    print("*****************开始登录***************")
    username = input("请输入用户名：")
    password = input("请输入密码：")
    password = hashlib.sha1(password.encode('utf8')).hexdigest()
    sql = "select username,password from user where username=%s and password=%s"
    res = cursor.execute(sql, [username, password])

    if res:
        return True
    else:
        return False


def search():
    print("****************展示所有信息*****************")
    sql = "select username,usertype,password,regtime,email from user"
    res = cursor.execute(sql)
    f1 = "{:19}{:19}{:50}{:20}{:20}"
    f2 = "{:20}{:20}{:50}{:25}{:20}"
    if res:
        datas = cursor.fetchall()
        print(f1.format("用户名", "用户类型", "密码", "注册日期", "email"))
        for data in datas:
            user_type = "管理员" if data["usertype"] == "1" else "普通用户"
            print(f2.format(data["username"], user_type, data["password"], data["regtime"].strftime("%Y-%m-%d %H:%M:%S"), data["email"]))
        return True
    else:
        return False


def init_database():
    sql_init = """drop database if exists bbs;"""

    cursor.execute(sql_init)

    sql_ct_db = """create database bbs """

    cursor.execute(sql_ct_db)

    conn.select_db("bbs")

    sql_ct_tb = """create table if not exists user(uid int primary key auto_increment,username varchar(40) not null UNIQUE,
    usertype enum("0","1") default "0",password char(48) not null, regtime datetime default now(), email varchar(40))"""

    cursor.execute(sql_ct_tb)


if __name__ == "__main__":
    conn = pymysql.Connect(**settings.parameters)
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    init_database()

    while 1:

        option = input("请选择操作(1:注册;2:登录;3:显示用户信息;q:退出)：")
        print(option)
        if len(option) > 1:
            print("选择错误，请重新选择！")
        if option == "q":
            break
        elif option == "1":
            if register():
                print("注册成功")
            else:
                print("请重新选择要进行的操作")
        elif option == "2":
            if login():
                print("登录成功，请进行其他操作")
            else:
                print("登录失败，请选择要进行的操作")
        elif option == "3":
            if search():
                print("显示成功，请进行其他操作")
            else:
                print("显示失败，请选择要进行的操作")
        else:
            print("选择错误，请重新选择！")

    cursor.close()
    conn.close()
