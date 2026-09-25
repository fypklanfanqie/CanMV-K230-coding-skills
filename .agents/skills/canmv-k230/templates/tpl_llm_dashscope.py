# -*- coding: utf-8 -*-
# =============================================================================
# K230 阿里云百炼（DashScope）大模型调用模板
# 包含：通用 HTTPS POST（可复用于任意 REST 云服务）+ qwen-plus 文字对话
# 获取 API Key：https://www.aliyun.com/product/tongyi → 密钥管理 → 创建
# 扩展：语音识别见 8.3 asr.py；语音合成（WebSocket）见 8.4 tts.py；
#      图片理解需 PC 中转，见 references/09-ai-llm.md §6
# =============================================================================
import network
import time
import json
import usocket
import ussl

# ------------------------------ 配置区 ---------------------------------------
WIFI_SSID = "your_ssid_name"
WIFI_PASSWORD = "your_ssid_password"
API_KEY = "your_api_key"                      # 阿里云百炼 API Key
QUESTION = "用一句话介绍你自己"
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
                print("WiFi 连接超时")
                return False
            time.sleep(1)
    print("WiFi 已连接:", wlan.ifconfig())
    return True


def https_post(host, url, api_key, data, timeout=10):
    """通用 HTTPS POST：发送 JSON，返回响应体文本（或 None）"""
    addr = usocket.getaddrinfo(host, 443)[0][-1]
    sock = usocket.socket()
    sock.settimeout(timeout)
    try:
        sock.connect(addr)
        ssl_sock = ussl.wrap_socket(sock, server_hostname=host)

        payload = json.dumps(data)
        payload_bytes = payload.encode('utf-8')

        headers = (
            "POST {} HTTP/1.1\r\n"
            "Host: {}\r\n"
            "Authorization: Bearer {}\r\n"
            "Content-Type: application/json\r\n"
            "Connection: close\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
        ).format(url, host, api_key, len(payload_bytes))

        ssl_sock.write(headers.encode() + payload_bytes)

        resp = b""
        while True:
            chunk = ssl_sock.read(1024)
            if not chunk:
                break
            resp += chunk

        ssl_sock.close()
        sock.close()
    except Exception as e:
        print("请求错误:", e)
        try:
            sock.close()
        except Exception:
            pass
        return None

    header_end = resp.find(b"\r\n\r\n")
    if header_end == -1:
        print("响应格式异常")
        return None
    body = resp[header_end + 4:]
    try:
        return body.decode('utf-8')
    except Exception:
        return body.decode('utf-8', 'ignore')


def ask_qwen(question):
    """调用 qwen-plus 文字大模型"""
    host = "dashscope.aliyuncs.com"
    url = "/api/v1/services/aigc/text-generation/generation"
    data = {
        "model": "qwen-plus",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一个运行在 K230 开发板上的 AI 助手，回答简洁。"},
                {"role": "user", "content": question}
            ]
        },
        "parameters": {
            "result_format": "message",
            "top_p": 0.8,
            "temperature": 0.7,
            "enable_search": False
        }
    }
    print("发送请求中...")
    result = https_post(host, url, API_KEY, data)
    if not result:
        print("请求失败或无响应")
        return None
    try:
        obj = json.loads(result)
        answer = obj["output"]["choices"][0]["message"]["content"]
        print("====== 大模型回答 ======")
        print(answer)
        return answer
    except Exception as e:
        print("解析失败:", e)
        print("原始响应:", result)
        return None


# ================================ 入口 =======================================
if __name__ == "__main__":
    if connect_wifi(WIFI_SSID, WIFI_PASSWORD):
        ask_qwen(QUESTION)

# =============================================================================
# 【其它能力调用速查】
# 语音识别（录音上传）：参考 8.3 asr.py（键 21 录音 → paraformer-v2 识别）
# 语音合成（WebSocket）：参考 8.4 tts.py（cosyvoice-v2 → /sdcard/output_0001.mp3）
# 图片理解（需 PC 中转）：
#   PC:  python VLLM_demo.py（Flask, 5000 端口, 填 DASHSCOPE_API_KEY）
#   板子: 修改 vllm_understand.py 中 PC_IP → 运行
# =============================================================================
