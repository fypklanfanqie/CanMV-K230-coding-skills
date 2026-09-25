# -*- coding: utf-8 -*-
# =============================================================================
# K230 网络通信模板（WiFi 连接 + TCP/UDP/HTTP 四种模式任选）
# 说明：把 PC 与板子连到同一路由器；PC 端可用资料包自带 NetAssist 调试
#      （CanMV K230/2.软件工具/2.6 网络调试助手/NetAssist.exe）
# =============================================================================
import network
import socket
import time

# ------------------------------ 配置区 ---------------------------------------
WIFI_SSID = "your_ssid_name"        # 仅支持 2.4G 热点！
WIFI_PASSWORD = "your_ssid_password"

MODE = "tcp_client"                 # 可选: tcp_client / tcp_server / udp_client / udp_server / http_client / http_server
SERVER_IP = "192.168.1.100"         # PC 的 IP（ipconfig 查询）
PORT = 8080
# -----------------------------------------------------------------------------


def connect_wifi(ssid, password, timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("正在连接 WiFi:", ssid)
        wlan.connect(ssid, password)
        start = time.time()
        while not wlan.isconnected():
            if time.time() - start > timeout:
                print("WiFi 连接超时！检查账号密码/2.4G")
                return None
            time.sleep(1)
    print("WiFi 已连接:", wlan.ifconfig())
    return wlan.ifconfig()[0]


# ------------------------------ TCP Client -----------------------------------
def tcp_client(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    addr = socket.getaddrinfo(SERVER_IP, PORT)[0][-1]
    try:
        s.connect(addr)
        print("已连接服务器")
    except OSError as e:
        s.close()
        print("连接失败:", e)
        return
    for i in range(10):
        msg = "hiwonder k230 tcp {}\r\n".format(i)
        print("发送:", msg.strip())
        s.write(msg.encode('utf-8'))
        time.sleep(0.2)
    s.close()
    print("发送完毕")


# ------------------------------ TCP Server -----------------------------------
def tcp_server(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(socket.getaddrinfo(ip, PORT)[0][-1])
    s.listen(5)
    print("TCP 服务器 %s:%d 已启动，等待连接..." % (ip, PORT))

    while True:
        client_sock, client_addr = s.accept()
        print("客户端:", client_addr)
        client_sock.write(b"Hello from k230!\n")
        client_sock.setblocking(False)
        while True:
            try:
                h = client_sock.read()
            except OSError as e:
                if e.args[0] != 11:      # 11 = EAGAIN
                    break
                h = None
            if h:
                print("收到:", h)
                client_sock.write("recv :%s" % h)
                if b"end" in h:
                    break
            time.sleep_ms(100)
        print("客户端断开")


# ------------------------------ UDP Client -----------------------------------
def udp_client(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = socket.getaddrinfo(SERVER_IP, PORT)[0][-1]
    for i in range(10):
        msg = "hiwonder K230 UDP {}\r\n".format(i)
        print("发送:", msg.strip())
        s.sendto(msg.encode('utf-8'), addr)
        time.sleep(0.2)
    s.close()
    print("UDP 发送完毕")


# ------------------------------ UDP Server -----------------------------------
def udp_server(ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(socket.getaddrinfo(ip, PORT)[0][-1])
    s.settimeout(10.0)
    print("UDP 服务器 %s:%d 已启动..." % (ip, PORT))
    while True:
        try:
            data, client_addr = s.recvfrom(1024)
            print("来自", client_addr, ":", data.decode('utf-8').strip())
            s.sendto(("已收到: " + data.decode('utf-8').strip()).encode(), client_addr)
        except OSError:
            print("等待超时...继续")
        except Exception as e:
            print("错误:", e)
            break


# ------------------------------ HTTP Client（GET） ---------------------------
def http_client():
    s = socket.socket()
    addr = socket.getaddrinfo("www.baidu.com", 80)[0][-1]
    s.connect(addr)
    s.send(b"GET /index.html HTTP/1.0\r\n\r\n")
    resp = s.recv(4096)
    print(resp[:500])                    # 打印前 500 字节
    s.close()
    print("HTTP 请求完成")


# ------------------------------ HTTP Server ----------------------------------
def http_server(ip):
    CONTENT = b"HTTP/1.0 200 OK\n\nHello from K230! count=%d\n"
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', 8081))
    s.listen(5)
    print("浏览器访问: http://%s:8081" % ip)
    counter = 0
    while True:
        client_sock, _ = s.accept()
        client_sock.settimeout(5)
        try:
            client_sock.recv(1024)       # 忽略请求内容
            client_sock.send(CONTENT % counter)
            counter += 1
        except Exception as e:
            print("请求处理错误:", e)
        finally:
            client_sock.close()


# ================================ 入口 =======================================
if __name__ == "__main__":
    ip = connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    if ip:
        print("本机 IP:", ip)
        if MODE == "tcp_client":
            tcp_client(ip)
        elif MODE == "tcp_server":
            tcp_server(ip)
        elif MODE == "udp_client":
            udp_client(ip)
        elif MODE == "udp_server":
            udp_server(ip)
        elif MODE == "http_client":
            http_client()
        elif MODE == "http_server":
            http_server(ip)
        else:
            print("MODE 配置错误")
