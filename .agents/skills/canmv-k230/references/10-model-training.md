# 10 · 模型训练与部署（在线平台 + 本地 YOLOv8）

> 来源：教程《9.在线模型训练》《10.本地模型训练（YOLOv8）》+ 配套脚本。
> 目标：训练自己的 kmodel（检测/分类/分割等），部署到 K230。
> 两条路线：**在线（零环境，快）** 与 **本地（可定制，离线）**。

---

## 1. 路线 A：在线训练平台（勘智 Kendryte）

**平台**：https://www.kendryte.com/zh/training/dataset （注册/登录）

### 1.1 数据集准备
- 用触摸拍照例程（ref/08 §2.2）或其它方式采集图片（几百张起步）；
- 放到电脑，稍后上传平台。

### 1.2 平台流程
1. "创建数据集" → 填名称 + 选择**识别/标注类型**（图像检测/分类/分割）；
2. 配置 → 上传图片；
3. 标注：新建标签（如 red/green/yellow）→ 逐图框选目标；
4. 训练：运行芯片选 **K230**，nncase 选最新版；参数建议：
   - 迭代次数：~200（连续 30–50 epoch loss 变化 <0.05 自动停）
   - batch size：8
   - 最大学习率：0.001
   - 标注框限制：5（每图最多目标数）
5. 云端训练（可关网页），结束邮件通知。

### 1.3 下载与部署
解压得到的部署包结构：
```
├── xxx_image_1_2_2.py    # 1.2.2 固件：图片推理脚本（完整代码）
├── xxx_video_1_2_2.py    # 1.2.2 固件：视频推理脚本（完整代码）
├── xxx_image_1_3.py      # 1.3 固件：图片推理（高度封装）
├── xxx_video_1_3.py      # 1.3 固件：视频推理（高度封装）
├── README.pdf
├── det_results/
└── mp_deployment_source/
    ├── *.kmodel
    └── deploy_config.json      # 模型路径/标签/阈值/锚框等配置
```

**部署步骤**：
1. 把 `mp_deployment_source/` 整个复制到 `CanMV/sdcard/`；
2. 把推理脚本拖入 CanMV IDE；
3. **修改脚本路径**（关键，官方包里的路径可能是旧的）：
```python
root_path = "/sdcard/mp_deployment_source/"
config_path = "/sdcard/mp_deployment_source/deploy_config.json"   # 改成绝对路径
display_mode = "lcd"     # 或 "hdmi"
DISPLAY_WIDTH  = ALIGN_UP(800, 16); DISPLAY_HEIGHT = 480            # lcd
OUT_RGB888P_WIDTH = ALIGN_UP(640, 16); OUT_RGB888P_HEIGH = 360      # AI 输入
```
4. 运行验证。

> 部署脚本模板同时保存在：`1.教程资料/9.在线模型训练/02 源码/01 程序案例代码/det_video_1_2_2.py`，
> 它展示了**低层写法**（nn.kpu + nn.ai2d 手写全流程），也是理解 AI 底层的极好材料。

---

## 2. 路线 B：本地训练（YOLOv8 → ONNX → kmodel）

> 环境：Windows + Miniconda；有 NVIDIA 显卡优先（无显卡可用 CPU 版 PyTorch，仅训练慢）。
> 资料位置：`1.教程资料/10.本地模型训练（YOLOv8）/`（含 miniconda 安装包、YOLOv8 环境包、数据集、脚本）。

### 2.1 环境搭建
```powershell
# ① 确认显卡驱动（有 N 卡时）
nvidia-smi

# ② 安装 Miniconda（安装包在同目录 04 miniconda 安装包/）

# ③ 配置清华源（可选，加速）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
conda config --set show_channel_urls yes

# ④ 创建环境
conda create -n yolov8 python=3.9 -y
conda activate yolov8

# ⑤ 克隆 YOLOv8 并安装
git clone https://github.com/ultralytics/ultralytics.git
cd ultralytics
pip install -e .

# ⑥ 有 N 卡：换 GPU 版 PyTorch
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
# 验证：python -c "import torch; print(torch.cuda.is_available())"   # 必须 True
```

### 2.2 数据集（以 Oxford-IIIT Pet 猫狗为例）
```powershell
mkdir pet_data && cd pet_data        # 例：E:\dog_and_cat_detection\pet_data
curl -L -O https://www.robots.ox.ac.uk/~vgg/data/pets/data/images.tar.gz
curl -L -O https://www.robots.ox.ac.uk/~vgg/data/pets/data/annotations.tar.gz
tar -xf images.tar.gz
tar -xf annotations.tar.gz
# 把资料包里的 dataset.py 放进来：pip install tqdm && python dataset.py
# 生成 dataset_formatted/ + data.yaml（打开确认路径正确）
```

### 2.3 训练与验证
```powershell
cd E:\dog_and_cat_detection\ultralytics
yolo detect train data=E:\dog_and_cat_detection\pet_data\dataset_formatted\data.yaml ^
     model=yolov8n.pt epochs=50 imgsz=320 batch=16 device=0 ^
     project=runs/train name=pet_k230_v8

# 推理验证（结果在 runs/detect/predict）
yolo predict model="...\runs\train\pet_k230_v8\weights\best.pt" ^
     source="...\Abyssinian_1.jpg" imgsz=320
```
**参数含义**：`imgsz=320`（**必须与将来 K230 输入一致**）、`yolov8n.pt`（Nano 预训练权重）。

### 2.4 导出 ONNX
```powershell
yolo export model="...\weights\best.pt" format=onnx imgsz=320 opset=11 simplify=True
```

### 2.5 ONNX → kmodel（nncase）
```powershell
pip install nncase
pip show nncase        # 版本核对
# 下载 K230 驱动 wheel 并安装（资料脚本中给的示例版本 v2.10.0）：
curl -L -O https://github.com/kendryte/nncase/releases/download/v2.10.0/nncase_kpu-2.10.0-py2.py3-none-win_amd64.whl
pip install nncase_kpu-2.10.0-py2.py3-none-win_amd64.whl
python convert_to_kmodel.py     # 编辑脚本顶部的 ONNX 路径/校准目录/输入尺寸
```

转换脚本（`10.本地模型训练（YOLOv8）/02 源码/02 ONNX转kmodel/convert_to_kmodel.py`）核心配置：
```python
compile_options.target = "k230"
compile_options.input_type = "uint8"
compile_options.input_layout = "NCHW"
compile_options.preprocess = True           # 使能归一化
compile_options.input_shape = [1, 3, 320, 320]
compile_options.input_range = [0, 255]
compile_options.mean = [0, 0, 0]
compile_options.std  = [255, 255, 255]      # uint8 → 0~1
# 量化
ptq_options.quant_type = "uint8"; w_quant_type = "uint8"; calibrate_method = "Kld"
# 校准数据：50 张 val 图片，uint8、RGB、resize 到 320、NCHW（不要 float/255！）
compiler.use_ptq(ptq_options); compiler.compile()
kmodel = compiler.gencode_tobytes()         # 写文件
```

### 2.6 部署
1. 把 kmodel 拷到 `CanMV/sdcard/`（或 examples/kmodel）；
2. 用部署例程（`03 K230部署/Cat_and_dog_detection.py`）改：
```python
kmodel_path = "/sdcard/pet_cat_dog_norm.kmodel"
labels = ["cat", "dog"]
model_input_size = [320, 320]     # 与训练一致
confidence_threshold = 0.7; nms_threshold = 0.7
# 使用 libs.YOLO 封装（见 ref/06 §8）
```

---

## 3. 两条路线怎么选

| 维度 | 在线平台 | 本地训练 |
|---|---|---|
| 环境要求 | 只要浏览器 | Windows/GPU + conda（资料已给全） |
| 上手速度 | 最快 | 首次 1–2 小时 |
| 定制能力 | 平台支持的类型/参数 | 完全自由（改结构/损失/超参） |
| 数据隐私 | 上传云端 | 全本地 |
| 产出 | 部署包（含配置） | 自己转 kmodel，自己写代码 |
| 适合 | 快速验证、常规检测 | 无人/离线/特殊任务 |

---

## 4. 模型与固件版本兼容（重要）

- 本资料**镜像 = CanMV K230 Hiwonder，local nncase v2.9.0**；
- kmodel 由 nncase 编译器产出，**转换版本需与固件 runtime 匹配**；
- 部署包出现"1.2.2 / 1.3"两套脚本 = 对应不同固件版本，先跑与镜像匹配的那套；
- 若模型加载即崩/报错：先怀疑版本不匹配 → 换平台推荐的 nncase 版本重转。

---

## 5. 相关资料文件索引

| 内容 | 路径 |
|---|---|
| 在线训练教程 | `1.教程资料/9.在线模型训练/01 在线模型训练.pdf`（+ `02 源码/`） |
| 部署脚本模板 | `9.在线模型训练/02 源码/01 程序案例代码/det_video_1_2_2.py` |
| 示例模型包 | `9.在线模型训练/02 源码/02 模型文件/Hiwonder_Traffic_ight_recogni.zip` |
| 本地训练教程 | `1.教程资料/10.本地模型训练（YOLOv8）/01 本地模型训练（YOLOv8）.pdf` |
| 数据集处理脚本 | `10.../02 源码/01 数据集处理/dataset.py` |
| 转换脚本 | `10.../02 源码/02 ONNX转kmodel/convert_to_kmodel.py` |
| 部署例程 | `10.../02 源码/03 K230部署/Cat_and_dog_detection.py` |
| miniconda/环境包/数据集 | `10.../04 miniconda 安装包/`、`05 YOLOv8环境包/`、`03 数据集/` |
