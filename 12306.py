#auther:blank
import re
import requests
import time
from PIL import Image
from django.utils.http import urlunquote
request=requests.session()
global_Token=''
head = {
    'Origin':'https://kyfw.12306.cn',
    'User-Agent': 'Chrome/64.0.3282.140',
    'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',
    'Connection':'keep-alive'
}
leftticket=''
keyischang=''
car_all=[]
user=[]
oldStr=''
newStr=''
default_user={}


def configure():
    while True:
        if open('config.txt','a'):
            f1=open('config.txt','r')
            if f1.readline()=='':
                print('未检查到配置信息')
                f1.close()
                print('请输入配置信息，配置文件自动保存')
                f1=open('config.txt','w')
                username=input('Please input username:')
                password=input('Please input password')
                seat_choose=input('理想座位ABC |过道| DE:')
                f1.write('%s\n%s\n1%s'%(username,password,seat_choose))
                print('模版文件已经产生请自行查看')
                f1.close()
            else:
                print('配置文件已导入，可以进行下一步')
                f1.seek(0)
                user1=f1.readlines()
                global user
                for m in user1:
                    user.append(m.strip())
                break
        else:
            print('创建配置文件失败')


def ticket_check(func,time_go,from_station,to_station):
    while True:
        try:
            url='https://kyfw.12306.cn/otn/leftTicket/queryZ?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT'%(time_go,from_station,to_station)
            for i in range(1):
                time.sleep(1)
                r=func.get(url,headers=head)
            print(r.url)
            result=r.json()
            return result['data']['result']
        except:
            print('http false ')


def login():
    while True:
        r1=request.get('https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand',headers=head)
        with open('yzm.png','wb') as f1:
            f1.write(r1.content)
        f1.close()
        yzm=Image.open('./yzm.png')
        yzm.show()
        identifdic={
            '1':'46,57',
            '2':'115,55',
            '3':'185,51',
            '4':'259,59',
            '5':'50,121',
            '6':'122,121',
            '7':'187,123',
            '8':'256,127'
        }
        iden_code=input('please input identifycode:')
        iden_code1=iden_code.split(',')
        if len(iden_code1)>1:
            iden_code=''
            n=0
            for i in iden_code1:
                if i in identifdic:
                    n+=1
                    if n==1:
                        iden_code += identifdic.get(i)
                    else:
                        iden_code += ',' + identifdic.get(i)
        else:
            iden_code=identifdic.get(iden_code1[0])
        date={
                'answer':iden_code,
                'login_site': 'E',
                'rand': 'sjrand'
        }
        r=request.post('https://kyfw.12306.cn/passport/captcha/captcha-check',data=date,headers=head)
        print(r.json())
        if r.status_code==200:
                user1={
                    'username':user[0],
                    'password':user[1],
                    'appid':'otn'
                }
                print(user1)
                r2=request.post('https://kyfw.12306.cn/passport/web/login',headers=head,data=user1)
                if r2.status_code==200:
                    print('登陆状态',r2.text)
                    r2_stat=re.findall('"result_message":"(.+?)"',r2.text)
                    if r2_stat[0]!='登录成功':continue
                    try:
                        while True:
                            data = {
                                "appid": "otn"
                            }
                            url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
                            response = request.post(url, headers=head, data=data)
                            if response.status_code == 200:
                                result = response.json()
                                print(result.get("result_message"))
                                newapptk = result.get("newapptk")
                            data = {
                                "tk": newapptk
                            }
                            url = "https://kyfw.12306.cn/otn/uamauthclient"
                            response = request.post(url, headers=head, data=data)
                            if response.status_code == 200 and response.url!='http://www.12306.cn/mormhweb/logFiles/error.html':
                                print(response.text)
                                url = "https://kyfw.12306.cn/otn/index/initMy12306"
                                response = request.get(url, headers=head)
                                if response.status_code == 200 and response.text.find("用户名") != -1:
                                    print(response.text.find("用户名"))
                                if r2.json()['result_message']!='登录成功':continue
                                time.sleep(1)
                                return r2.content

                    except:
                        print('登陆失败')



#模拟购票信息页面
def buy_ticket(secretStr,train_date,back_train_date,query_from_station_name,query_to_station_name):
    while True:
        try:
            secretStr = urlunquote(secretStr)
            buy_data={
                'secretStr': secretStr,
                'train_date': train_date,
                'back_train_date': back_train_date,
                'tour_flag': 'dc',
                'purpose_codes': 'ADULT',
                'query_from_station_name': query_from_station_name,
                'query_to_station_name': query_to_station_name,
                'undefined': '',
            }
            r1=request.post('https://kyfw.12306.cn/otn/login/checkUser',data={'_json_att':''},headers=head)
            r=request.post('https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest',headers=head,data=buy_data)
            if r1.url == 'http://www.12306.cn/mormhweb/logFiles/error.html' and r.url=='http://www.12306.cn/mormhweb/logFiles/error.html': continue
            if r.status_code==200 and r.url!='http://www.12306.cn/mormhweb/logFiles/error.html':
                r.encoding=r.apparent_encoding
                time.sleep(0.5)
                break
        except:
            print('获取购票页面error网络错误,尝试重新提交')
    OSDT()


#获取已保存的用户信息
def OSDT():
    head1 = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Host': 'kyfw.12306.cn',
        'Origin': 'https://kyfw.12306.cn',
        'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Chrome/64.0.3282.140'
    }
    i=1
    while i==1:
            data={'_json_att':''}
            time.sleep(1)
            r2 = request.post('https://kyfw.12306.cn/otn/confirmPassenger/initDc',data=data,headers=head1)
            r3=request.get('https://kyfw.12306.cn/otn/resources/merged/common_js.js?scriptVersion=1.9076',headers=head)
            if r2.status_code == 200:
                r2.encoding = r2.apparent_encoding
                print(r2.url)
                if r2.url=='http://www.12306.cn/mormhweb/logFiles/error.html':
                    buy_ticket(car_all[who_go - 1][0], time_go,
                               '%s-%s-%s' % (tm.tm_year, str(tm.tm_mon).zfill(2), str(tm.tm_mday).zfill(2)), from_code,
                               go_code)
                    continue
                # print(r2.text)
                global global_Token, leftTicket, keyischang
                global_Token = re.findall('globalRepeatSubmitToken = (.+?);', r2.text)[0].replace('\'', '')
                print(global_Token)
                if re.findall("'leftTicketStr':'(.+?)'",r2.text)==[]:
                    print('获取失败')
                leftTicket=leftTicket=re.findall("'leftTicketStr':'(.+?)'",r2.text)[0]
                print(leftTicket)
                keyischang=re.findall("'key_check_isChange':'(.+?)'",r2.text)[0]
                print(keyischang)
                data={
                    '_json_att':'',
                    'REPEAT_SUBMIT_TOKEN':global_Token
                }
                while i==1:
                    try:
                        time.sleep(0.6)
                        DTOS = request.post('https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs',data=data,headers=head)
                        if DTOS.status_code == 200 and DTOS.url!='http://www.12306.cn/mormhweb/logFiles/error.html':
                            DTOS.encoding=DTOS.apparent_encoding
                            print('获取信息成功')
                            global default_user
                            default_user=DTOS.json().get('data').get('normal_passengers')[0]#设置默认第几个乘客默认0第一个
                            i=0
                    except:
                        print('OSDT error')
    check_info()


#检查信息有无错误
def check_info():
    fix_str()
    while True:
        try:
            data={
                    'cancel_flag':'2',
                    'bed_level_order_num': '000000000000000000000000000000',
                    'passengerTicketStr':newStr,
                    'oldPassengerStr': oldStr,
                    'tour_flag': 'dc',
                    'randCode':'',
                    'whatsSelect':'1',
                    '_json_att':'',
                    'REPEAT_SUBMIT_TOKEN':global_Token
            }
            r=request.post('https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo',data=data,headers=head)
            if r.status_code==200:
                print('检查信息成功！开始下一步')
                break
        except:
            print('chekinfo error')
    getCount(car_all,int(who_go-1))


#获取票数
def getCount(car_all,who_go):
    tran_date = '%s %s %s %s 00:00:00 GMT+0800 (CST)' % (
    time.strftime('%a', formattime), time.strftime('%b', formattime), str(formattime.tm_mday).zfill(2),
    formattime.tm_year)
    print(tran_date)
    time.sleep(0.5)
    while True:
        try:
            data={
                'train_date': tran_date,
                'train_no': car_all[who_go][2],
                'stationTrainCode': car_all[who_go][3],
                'seatType': 'O',
                'fromStationTelecode': car_all[who_go][6],
                'toStationTelecode': car_all[who_go][7],
                'leftTicket':leftTicket,
                'purpose_codes': '00',
                'train_location': car_all[who_go][15],
                '_json_att':'',
                'REPEAT_SUBMIT_TOKEN':global_Token
            }
            print(data)
            r=request.post('https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount',data=data,headers=head)
            print(r.json())
            if r.status_code==200:
                if r.json()['status']=='False':
                    time.sleep(1)
                    continue
                print('剩余票数\033[43m%s\033[0m' % r.json()['data']['ticket'])
                break
        except:
            print('get Count erro')
    confirm()


def confirm():
    while True:
        try:
            data={
                    'passengerTicketStr':newStr,
                    'oldPassengerStr': oldStr,
                    'randCode':'',
                    'purpose_codes':'00',
                    'key_check_isChange':keyischang,
                    'leftTicketStr': leftTicket,
                    'train_location': car_all[who_go-1][15],
                    'choose_seats': user[2],
                    'seatDetailType': '000',
                    'whatsSelect': '1',
                    'roomType': '00',
                    'dwAll': 'N',
                    '_json_att':'',
                    'REPEAT_SUBMIT_TOKEN':global_Token
            }
            r=request.post('https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue',data=data,headers=head)
            if r.url!='http://www.12306.cn/mormhweb/logFiles/error.html' and r.status_code==200:
                print(r.json())
                break
        except:
            print('购票失败，尝试重试试')
    print('\033[42m购票成功，做完了该做的，下面快去下单吧\033[0m\n正在查询')
    check_tick()


def check_tick():
    while True:
        try:
            data = {'_json_att': ''}
            r1=request.get('https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=1518584637&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=%s'%global_Token)
            r = request.post('https://kyfw.12306.cn/otn/queryOrder/queryMyOrderNoComplete', data=data, headers=head)
            if r.url!='http://www.12306.cn/mormhweb/logFiles/error.html' and r.status_code==200:
                print(r.json())
                break
        except:
            print('查询失败')


def fix_str():
    global oldStr,newStr
    oldStr = default_user.get('passenger_name') + ',' + default_user.get(
        'passenger_id_type_code') + ',' + default_user.get('passenger_id_no') + ',' + default_user.get('passenger_type')
    oldStr = oldStr + '_'
    if default_user.get('mobile_no')!='':
        newStr = seat_type + ',0,' + default_user.get('passenger_type') + ',' + default_user.get(
            'passenger_name') + ',' + default_user.get('passenger_id_type_code') + ',' + default_user.get(
            'passenger_id_no') + ',' + default_user.get('mobile_no') + ',N'
    else:
        phone=input('your phone number:')
        newStr = seat_type + ',0,' + default_user.get('passenger_type') + ',' + default_user.get(
            'passenger_name') + ',' + default_user.get('passenger_id_type_code') + ',' + default_user.get(
            'passenger_id_no') +','+ default_user.get('mobile_no') + ',N'


def check_ti(func):
    result = ticket_check(func, time_go, from_station, go_station)
    text_data = []
    n = 1
    global car_all
    for i in result:
        car = i.split('|')
        car_all.append(car)
        text_data.append(car[0])
        car_text = car[3:10]
        del car_text[1:3]
        car_z = car[20:-3]
        if car_z[12] and car_z[12] != '无': car_z[12] = '\033[43m特等:\033[0m：' + car_z[12]
        if car_z[6] and car_z[6] != '无': car_z[6] = '\033[45m无座:\033[0m' + car_z[6]
        if car_z[11] and car_z[11] != '无': car_z[11] = '\033[42m一等:\033[0m' + car_z[11]
        if car_z[10] and car_z[10] != '无': car_z[10] = '\033[41m二等:\033[0m' + car_z[10]
        car_z = list(filter(lambda x: x != '' and x != '无', car_z))
        print(n, ' \t '.join(car_text), '\t\t\t'.join(car_z), sep='\t\t')
        n = n + 1
    return text_data


def city_station():
    r=requests.get('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js',headers=head)
    text=r.text
    text=text.split('|')
    global from_station, go_station,go_code,from_code
    a=text.index(from_station)
    from_code=from_station
    from_station=text[a+1]
    b=text.index(go_station)
    go_code=from_code
    go_station=text[b+1]


if __name__=='__main__':
    configure()
    tm = time.localtime()

    if tm.tm_hour>=23 or tm.tm_hour<=6:
        print('现在是休息时间',tm.tm_hour,'点')
        exit('bye!!!!')
    time_go=input('please in put time:(格式2018-03-03)中文---:>>').strip()
    formattime = time.strptime(time_go, "%Y-%m-%d")
    from_station=input('from station:---:>>')
    go_station=input('go station:--:>>')
    from_code=''
    go_code=''
    city_station()
                #查询模块
                # result=ticket_check(request,time_go,from_station,go_station)
    text_data=[]
    text_data=check_ti(request)
    text_data=list(zip(text_data,list(range(1,30))))
    a=login()
    print(a)
    who_go=int(input('what are you want to read:'))
    print('商务座(9),特等座(P),一等座(M),二等座(O),高级软卧(6),软卧(4),硬卧(3),软座(2),硬座(1),无座(1)')
    seat_type=input('what do you want to seat:')
    for i in text_data:
        if who_go == i[1]:
            secretStr=i[0]
            break
    buy_ticket(car_all[who_go-1][0],time_go,'%s-%s-%s'%(tm.tm_year,str(tm.tm_mon).zfill(2),str(tm.tm_mday).zfill(2)),from_code,go_code)



