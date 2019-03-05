import socket
import socks
import requests

ip='127.0.0.1' # change your proxy's ip
port = 10801 # change your proxy's port
socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, ip, port)
socket.socket = socks.socksocket
url = u'https://www.instagram.com/'
r = requests.get(url)
print(r.text)