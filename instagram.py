import os
import re
import sys
import json
import time
import random
import requests
from hashlib import md5
from pyquery import PyQuery as pq
import socket
import socks




# https://wallpaper.mob.org/image/downloadImage?id=40703&l=240&t=0&r=468&b=415&s=0.5932475884244373

"""
id: 40703
l: 137
t: 0
r: 365
b: 415
s: 0.5928571428571429

id: 47437
l: 132
t: 0
r: 360
b: 415
s: 0.5937834941050375


# 壁纸爬虫网站 分类有
    
    ABSTRACT 475张 ANIMALS 633张 ART 464张 CARS 451张 FOOD & DRINK 285张 GAMES 267张 MOVIES 356张
    
    MUSIC 116张 NATURE 1993张 PHOTOS 829张 PLACES 411张 QUOTES 66张 SPORTS 127张
    

http://www.mobileswall.com/#

http://www.mobileswall.com/wallpaper/swan-2/
http://www.mobileswall.com/wp-content/uploads/2015/12/901-Swan-l.jpg
http://www.mobileswall.com/wallpaper/good-scenery-come-out-to-find-something-to-eat/
http://www.mobileswall.com/wp-content/uploads/2015/12/901-Good-Scenery-Come-Out-to-Find-Something-to-Eat-l.jpg

http://www.mobileswall.com/wallpaper/want-to-eat-something/
http://www.mobileswall.com/wp-content/uploads/2015/12/901-Want-to-Eat-Something-l.jpg

http://www.mobileswall.com/wp-content/uploads/2015/07/901-Red-whiskered-Bulbuls-l.jpg


http://www.mobileswall.com/wp-content/uploads/2015/07/300-Ripples-l.jpg
http://www.mobileswall.com/wp-content/uploads/2015/07/901-Ripples-l.jpg
"""

# 境外连接socks
ip='127.0.0.1' # change your proxy's ip
port = 10801 # change your proxy's port
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, port)
socket.socket = socks.socksocket

url_base = u'https://www.instagram.com/'
uri = u'https://www.instagram.com/graphql/query/?query_hash=a5164aed103f24b03e7b7747a2d94e3c&variables=%7B%22id%22%3A%22{user_id}%22%2C%22first%22%3A12%2C%22after%22%3A%22{cursor}%22%7D'


BASE_PATH = 'C:\\videos\\instagram\\'

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'cookie': 'csrftoken=BoPC7agZgyLblrQxYtHWl2hKte0FApDI; ds_user_id=10147571424; fbm_124024574287414=base_domain=.instagram.com; mcd=2; mid=XDSttwALAAFV17Ay-mMBg9iDtO_8; rur=PRN; sessionid=10147571424%3AROjFKgQrAqP2lG%3A14; shbid=9207; shbts=1551788462.055799; urlgen="{\"45.77.128.242\": 20473}:1h1Gwv:Ije7VWOZYGJb4mp9kGs_aODfoxE"'
}


def get_html(url):
    try:
        response = requests.get(url, headers=headers)
        print(response.text)
        if response.status_code == 200:
            return response.text
        else:
            print('请求网页源代码错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        return None


def get_json(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print('请求网页json错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        time.sleep(5 + float(random.randint(1, 4000))/100)
        return get_json(url)


def get_content(url):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            print('请求照片二进制流错误, 错误状态码：', response.status_code)
    except Exception as e:
        print(e)
        return None


def get_urls(html):
    urls = []
    user_id = re.findall('"profilePage_([0-9]+)"', html, re.S)[0]
    print('user_id：' + user_id)
    doc = pq(html)
    items = doc('script[type="text/javascript"]').items()
    for item in items:
        if item.text().strip().startswith('window._sharedData'):
            js_data = json.loads(item.text()[21:-1], encoding='utf-8')
            edges = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]["edges"]
            page_info = js_data["entry_data"]["ProfilePage"][0]["graphql"]["user"]["edge_owner_to_timeline_media"]['page_info']
            cursor = page_info['end_cursor']
            flag = page_info['has_next_page']
            for edge in edges:
                if edge['node']['display_url']:
                    display_url = edge['node']['display_url']
                    print(display_url)
                    urls.append(display_url)
            print(cursor, flag)
    while flag:
        url = uri.format(user_id=user_id, cursor=cursor)
        js_data = get_json(url)
        infos = js_data['data']['user']['edge_owner_to_timeline_media']['edges']
        cursor = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
        flag = js_data['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
        for info in infos:
            if info['node']['is_video']:
                video_url = info['node']['video_url']
                if video_url:
                    print(video_url)
                    urls.append(video_url)
            else:
                if info['node']['display_url']:
                    display_url = info['node']['display_url']
                    print(display_url)
                    urls.append(display_url)
        print(cursor, flag)
        # time.sleep(4 + float(random.randint(1, 800))/200)    # if count > 2000, turn on
    return urls


def main(user):
    url = url_base + user + '/'
    html = get_html(url)
    urls = get_urls(html)
    dirpath = BASE_PATH+'{0}'.format(user)
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)
    for i in range(len(urls)):
        print('\n正在下载第{0}张： '.format(i) + urls[i], ' 还剩{0}张'.format(len(urls)-i-1))
        try:
            content = get_content(urls[i])
            file_path = BASE_PATH+'{0}\\{1}.{2}'.format(user, '高质量-韩国-模特-生活-'+str(i), urls[i][-43:-40]) #md5(content).hexdigest()
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    print('第{0}张下载完成： '.format(i) + urls[i])
                    f.write(content)
                    f.close()
            else:
                print('第{0}张照片已下载'.format(i))
        except Exception as e:
            print(e)
            print('这张图片or视频下载失败')


if __name__ == '__main__':
    user_name = sys.argv[1]
    start = time.time()
    main(user_name)
    print('Complete!!!!!!!!!!')
    end = time.time()
    spend = end - start
    hour = spend // 3600
    minu = (spend - 3600 * hour) // 60
    sec = spend - 3600 * hour - 60 * minu
    print(f'一共花费了{hour}小时{minu}分钟{sec}秒')
