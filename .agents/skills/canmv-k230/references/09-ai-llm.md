# 09 · AI 大模型（语音唤醒 / ASR / TTS / LLM / 图片理解）

> 来源：教程《8.AI大模型课程》5 个实验 + 对应源码。
> 平台：阿里云百炼（DashScope，通义千问系列），需要 **API Key**（教程 8.1）。
> 网络：所有功能都要求板子先连上 2.4G WiFi。

---

## 1. 准备：API Key 获取（8.1）

1. 打开 https://www.aliyun.com/product/tongyi → 注册/登录 → 实名认证（个人支付宝认证即可）。
2. 进入大模型控制台 → 开通服务（领取免费额度）→ 先用网页对话测试"你好"。
3. 密钥管理 → 创建我的 API-KEY（归属"默认业务空间"）→ **复制并保存**（只显示一次）。
4. 各例程中把 `API_KEY = "your_api_key"` 替换成它。

---

## 2. 语音唤醒（8.2 keyword_spotting.py）—— 全部离线

- 模型：`/sdcard/examples/kmodel/kws.kmodel`；回复音频：`/sdcard/examples/utils/wozai.wav`
- 唤醒词：**"小南小南"** → 播报"我在"
- 参数：`THRESH = 0.05`、`SAMPLE_RATE = 16000`、单声道、`CHUNK = 0.3*16000`（4800 点）
- 结构：PyAudio 采集 → `aidemo.kws_preprocess(fp, pcm_list)` 特征 → KWSApp.run（含 cache 状态）→ 命中播 wav

```python
# 关键片段（完整见例程）
fp = aidemo.kws_fp_create()                     # 关键词预处理句柄
pcm_data = input_stream.read()                  # 实时音频
res = kws.run(pcm_data)                         # 1=命中
if res:
    wf = wave.open(reply_wav_file, "rb")
    wav_data = wf.read_frames(CHUNK)
    while wav_data:
        output_stream.write(wav_data)
        wav_data = wf.read_frames(CHUNK)
    wf.close()
```
> 预处理的 `struct.unpack("<h", ...)` 把 PCM 字节流转 float 采样点，是音频类程序的通用套路。

---

## 3. 语音识别 ASR（8.3 asr.py）

**交互协议**：按下板载 KEY(GPIO21) 开始录音 → 松开停止 → 上传阿里云 → 终端打印识别文本。

**两条实现路线**（资料包两个版本源码）：

| 路线 | 源码 | 说明 |
|---|---|---|
| A. 录音上传（推荐学习） | `1.教程资料/8.AI大模型课程/02 源码/8.3 语音识别/asr.py`（完整版，~300 行，含 Response 类/HTTP 封装/按键录音） | 真实录音→HTTP 上传→识别 |
| B. 音频 URL 识别（最简） | `5.程序源码/asr.py`（用现成音频 URL + qwen-audio-asr） | 验证链路用 |

关键常量与结构（A 路线）：
```python
API_KEY = "your_api_key"
MODEL = "paraformer-v2"                  # 语音识别模型
SAVE_PATH = "/sdcard/asr_demo.wav"
CHUNK = 1764; RATE = 44100               # 44.1k 采样

key = Button(21)                         # 板载按键
ok, result = connect_wifi(WIFI_SSID, WIFI_KEY)
# 主循环：record_and_recognize(SAVE_PATH, key, API_KEY)
```

要点：
- 录音用 `media.pyaudio`（见 ref/03 §4），WAV 先存 `/sdcard`；
- HTTP 上传用 usocket + ussl 手写（分块传输/Content-Length 都要处理，完整版里有 `_read_response` 兼容 chunked）；
- 识别结果从 JSON 里取（例程 Response 类提供 `.json` 属性）；
- ⚠️ 额度用尽时接口返回错误，注意打印排查。

---

## 4. 语音合成 TTS（8.4 tts.py）

**实现的协议**：DashScope WebSocket 流式 TTS（cosyvoice-v2）→ 合成 mp3 存 `/sdcard/output_0001.mp3`。

```python
HOST = "dashscope.aliyuncs.com"; PORT = 443
PATH = "/api-ws/v1/inference/"
OUTPUT_FILE = "/sdcard/output_0001.mp3"
texts = ["床前明月光，疑是地上霜", "举头望明月，低头思故乡"]
```

流程：
1. `usocket` 连 443 → `ussl.wrap_socket`；
2. **WebSocket 握手**（手写 HTTP Upgrade + Sec-WebSocket-Key + Authorization）；
3. 发 `run-task`（task=tts, function=SpeechSynthesizer, model=cosyvoice-v2, voice=longxiaochun_v2, format=mp3）；
4. 逐条发 `continue-task`（input.text）；
5. 发 `finish-task`；
6. 循环 `recv_ws_message`：文本帧=事件 JSON，二进制帧=音频数据 → 写入 mp3 文件。

> WebSocket 帧的手写编解码（FIN/opcode/掩码/长度）在 `5.程序源码/tts.py` 完整实现（`send_ws_text` / `recv_ws_message` / `safe_read`），**这是可复用的基础设施**，做其它 WebSocket 云服务（如 ASR 实时流）直接改参数即可。

---

## 5. 文字理解 LLM（8.5 llm.py）

最简单的 HTTP POST：

```python
host = "dashscope.aliyuncs.com"
url  = "/api/v1/services/aigc/text-generation/generation"
data = {
    "model": "qwen-plus",
    "input": {
        "messages": [
            {"role": "system", "content": "你是一个AI助手"},
            {"role": "user",   "content": "联网查询深圳今天天气怎么样?"}
        ]
    },
    "parameters": {
        "result_format": "message",
        "top_p": 0.8, "temperature": 0.7,
        "enable_search": False,
        "enable_thinking": False,
        "thinking_budget": 4000
    }
}
result = https_post(host, url, API_KEY, data)
print(result)
```

`https_post` 通用函数（POST + JSON + Bearer 鉴权 + 读全响应）在例程里有完整实现，**可直接复用做任意 REST 云服务调用**。

---

## 6. 图片理解 VLM（8.6 vllm_understand.py + VLLM_demo.py）

**特殊限制**：K230 无法直连 DashScope 的图片理解接口 —— 板载 ussl 的 TLS 版本/加密套件不满足要求。
**官方方案：PC 中转**：

```
K230（vllm_understand.py） --HTTP--> PC（VLLM_demo.py, Flask:5000） --HTTPS--> 阿里云
```

### PC 端（Flask 代理）
```bash
pip install flask requests
# VLLM_demo.py 中修改 DASHSCOPE_API_KEY="your_api_key"
# 运行后监听 5000 端口
```

### K230 端
```python
PC_IP = "电脑局域网IP"     # ipconfig 查（Win+R → cmd）
PORT = 5000
image_url = "https://..."   # 或本地图片
question = "请用中文描述这张图片,在120个字以内"
send_to_pc(PC_IP, PORT, image_url, question)
```
**运行顺序**：先跑 K230 程序，再在 PC 跑 Flask，然后板子发请求。

---

## 7. 语音闭环配方（做一个智能语音助手）

```
唤醒(kws) → 倾听(按键/唤醒后录音) → ASR(paraformer) → LLM(qwen-plus) → TTS(cosyvoice) → 播放
```
各环节源码都在资料包：
| 环节 | 源码 |
|---|---|
| 唤醒 | `8.AI大模型课程/02 源码/8.2 语音唤醒/keyword_spotting.py` |
| 录音+ASR | `8.3 语音识别/asr.py` |
| LLM | `8.5 文字理解/llm.py` |
| TTS | `8.4 语音合成/tts.py` |
| 播放 | ref/03 §4.2（PyAudio，wav）或 mp3 转码后播放 |

组合时注意：音频设备（PyAudio/MediaManager）在同一进程里**串行初始化与释放**，不要同时开录音与播放流后忘记关闭。

---

## 8. 常见问题

| 现象 | 处理 |
|---|---|
| 返回 401/403 | API Key 错误/未开通服务 |
| 返回额度类错误 | 免费额度耗尽，官网查询 |
| TLS 握手失败 | 该服务不支持直连 → 中转（§6）或换接口 |
| 录音全静音 | 麦克风被占用/PyAudio 没 initialize/音量 0 |
| TTS 保存的 mp3 播不了 | K230 端直接播放 mp3 受限 → 用 wav（转码）或仅作保存 |
| WebSocket 卡住 | 检查握手 Authorization 大小写（`bearer`）、任务顺序（run→continue→finish） |
