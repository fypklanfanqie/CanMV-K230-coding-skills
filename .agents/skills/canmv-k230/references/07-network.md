# 07 · 网络通信（WiFi / LAN / TCP / UDP / HTTP）

> 来源：教程《6.网络基础课程》8 个实验。
> 硬件：板载 WiFi TL8189（**仅 2.4GHz**，陶瓷天线）；有线需 USB 转网口（RTL8152B 免驱百兆网卡）插 USB-A 口。

---

## 1. WiFi 连接（STA 模式）——所有网络程序的公共函数

```python
import network
import time

def connect_wifi(ssid, password, timeout=15):
    wlan = network.WLAN(network.STA_IF)      # STA = 客户端模式
    wlan.active(True)
    if not wlan.isconnected():
        print(f"正在连接: {ssid} ...")
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                print("WiFi 超时！请检查账号密码或信号")
                return False
            time.sleep(1)
    print("WiFi 已连接:", wlan.ifconfig())    # (ip, mask, gateway, dns)
    return True
```

**要点**
- 只能连 **2.4GHz** 热点（5G 连不上）。
- `wlan.ifconfig()` 返回四元组；`wlan.config("mac")` 取 MAC。
- 每次开机都要重连（WiFi 不记忆）。

---

## 2. 有线网络（USB 网卡）

```python
import network
a = network.LAN()
print(a.active())                     # 是否启用
print(a.ifconfig())                   # 查看 ip/掩码/网关/dns
a.ifconfig(('192.168.0.4', '255.255.255.0', '192.168.0.1', '8.8.8.8'))  # 静态
a.ifconfig("dhcp")                    # DHCP 自动获取
print(a.config("mac"))
```

---

## 3. TCP

### 3.1 TCP Client（连 PC 的服务器）

```python
import socket, network, time

# ...connect_wifi...
SERVER_IP = "192.168.x.x"      # PC 的 IP
SERVER_PORT = 8080

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
addr = socket.getaddrinfo(SERVER_IP, SERVER_PORT)[0][-1]
try:
    s.connect(addr)
except OSError as e:
    s.close()
    raise
for i in range(10):
    s.write("hiwonder k230 tcp {}\r\n".format(i).encode('utf-8'))
    time.sleep(0.2)
s.close()
```

### 3.2 TCP Server（板子监听，PC 连板子）

```python
CONTENT = b"Hello #%d from k230 canmv MicroPython!\n"

ip = wlan.ifconfig()[0]
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # 端口复用（重启不报占用）
s.bind(socket.getaddrinfo(ip, 8080)[0][-1])
s.listen(5)
print("TCP服务器已启动", ip, 8080)

counter = 1
while counter <= 10:
    client_sock, client_addr = s.accept()
    print("客户端:", client_addr)
    client_sock.setblocking(False)                 # 非阻塞
    client_sock.write(CONTENT % counter)
    while True:
        try:
            h = client_sock.read()
        except OSError as e:
            if e.args[0] != 11:                    # 11 = EAGAIN（暂时无数据）
                break
        if h and h != b"":
            print("收到:", h)
            client_sock.write("recv :%s" % h)
            if b"end" in h:
                break
        time.sleep_ms(100)
    counter += 1
```

---

## 4. UDP

### 4.1 UDP Client

```python
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SERVER_IP = "192.168.x.x"; SERVER_PORT = 8080
addr = socket.getaddrinfo(SERVER_IP, SERVER_PORT)[0][-1]
for i in range(10):
    s.sendto("hiwonder K230 UDP {}\r\n".format(i).encode('utf-8'), addr)
    time.sleep(0.2)
s.close()
```

### 4.2 UDP Server

```python
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(socket.getaddrinfo(ip, 8080)[0][-1])
s.settimeout(10.0)                       # recvfrom 超时，防卡死
count = 0
while count < 10:
    try:
        data, client_addr = s.recvfrom(1024)
        print("来自", client_addr, ":", data.decode('utf-8').strip())
        s.sendto(("已收到的消息: " + data.decode('utf-8').strip()).encode(), client_addr)
        count += 1
    except OSError:
        print("等待超时...")
s.close()
```

---

## 5. HTTP

### 5.1 HTTP Client（GET 请求）

```python
s = socket.socket()
addr = socket.getaddrinfo("www.baidu.com", 80)[0][-1]   # 可重试 3 次
s.connect(addr)

# 方式 A：流模式
s_file = s.makefile("rwb", 0)
s_file.write(b"GET /index.html HTTP/1.0\r\n\r\n")
print(s_file.read())
s_file.close()

# 方式 B：收发模式
# s.send(b"GET /index.html HTTP/1.0\r\n\r\n")
# print(s.recv(4096))
s.close()
```

### 5.2 HTTP Server（板子当网站）

```python
CONTENT_TEMPLATE = b"""HTTP/1.0 200 OK
Hello Hiwonder k230 canmv! Request number: %d
"""
addr = ('0.0.0.0', 8081)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(5)
s.setblocking(True)
print("访问地址: http://%s:8081" % ip)

counter = 0
while True:
    client_sock, client_addr = s.accept()
    client_sock.settimeout(5)
    request = b""
    while True:
        try:
            chunk = client_sock.recv(1024)
            if not chunk: break
            request += chunk
            if b"\r\n\r\n" in request: break      # 请求头结束
        except OSError as e:
            if e.args[0] == 11: time.sleep(0.1); continue
            raise
    client_sock.send(CONTENT_TEMPLATE % counter)
    counter += 1
    client_sock.close()
```
> 运行后把打印的 `http://IP:8081` 在浏览器打开即可看到响应。

### 5.3 HTTPS（ussl）

```python
import ussl
sock = socket.socket()
sock.connect(socket.getaddrinfo(host, 443)[0][-1])
ssl_sock = ussl.wrap_socket(sock, server_hostname=host)
ssl_sock.write(b"GET / HTTP/1.1\r\nHost: %s\r\nConnection: close\r\n\r\n" % host.encode())
resp = b""
while True:
    chunk = ssl_sock.read(1024)
    if not chunk: break
    resp += chunk
```
⚠️ 板载 ussl 是**极简 TLS 实现**，部分云服务（如阿里云 DashScope 新接口）无法握手 → 见 ref/09 的中转方案。

---

## 6. 与 PC 联调（NetAssist 网络调试助手）

路径：`CanMV K230/2.软件工具/2.6 网络调试助手/NetAssist.exe`

| 场景 | NetAssist 设置 |
|---|---|
| 板子作 TCP Client | 协议 TCP Server；本地端口 8080；等板子连入 |
| 板子作 TCP Server | 协议 TCP Client；远程地址=板子 IP:8080 |
| UDP | 协议 UDP；本地端口 8080（双方约定同一端口） |

**通用准备**：
1. PC 与板子连同一路由器（同一网段）；
2. 查 PC 的 IP：`Win+R → cmd → ipconfig`（填进板子代码的 SERVER_IP）；
3. **临时关闭 PC 防火墙**（否则 TCP/UDP 常见被拦）。

---

## 7. 综合应用配方（agent 常用组合）

| 需求 | 组合 |
|---|---|
| 视觉结果上报服务器 | OpenMV/AI 检测 → 组 JSON → TCP Client / HTTP POST |
| PC 远程遥控板子 | 板子 TCP Server 收指令 → 解析 → 控制 GPIO/PWM |
| 图传（低帧率） | 板子 snapshot → jpg 编码 → TCP/UDP 分包发送（注意带宽） |
| 连接云平台 | HTTPS/WebSocket + 鉴权（见 ref/09 大模型章节的 socket/ssl 写法） |
| MQTT | 资料包附通讯猫 MQTT 助手；板端可基于 socket 手写或移植 umqtt |

**网络程序调试三件套**：`print(ip)` 确认连上 → NetAssist 确认对端通 → 再查应用层协议格式。
