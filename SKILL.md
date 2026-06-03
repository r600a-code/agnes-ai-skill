---
name: "agnes-ai"
description: "Agnes AI API 全功能接入：文生图、图生视频、多图参考视频、图片编辑。当用户需要使用 Agnes AI 生成图片、视频、或进行 AI 创意内容制作时调用。"
---

# Agnes AI 全功能 Skill

Agnes AI API 提供文生图、文生视频（含参考图）、图片编辑等能力，适用于营销素材、短视频创意、产品展示等场景。

---

## ⚠️ 当前能力边界提醒

> **重要：Agnes Video 模型切分场景能力很弱**，无法像专业剪辑工具那样自动分镜。它本质上是一个"动态图"生成器——基于一张或多张参考图，根据 prompt 描述让画面动起来。
>
> **够用了！** 适用场景：
> - 产品展示的动态特写（轻微运镜、光影变化）
> - 人物微笑、眨眼、微表情等简单动作
> - 物体旋转、光影扫过等氛围动画
> - 博主手持产品、轻微晃动等短视频风格
>
> **不适用场景：**
> - 复杂多镜头分镜叙事
> - 大幅度肢体动作（跑步、跳舞等）
> - 需要精确口型同步的视频

---

## 一、API 基础信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://apihub.agnes-ai.com/v1` |
| 认证方式 | Bearer Token |
| Header | `Authorization: Bearer <API_KEY>`, `Content-Type: application/json` |
| 图片模型 | `agnes-image-2.0-flash` |
| 视频模型 | `agnes-video-v2.0` |

---

## 二、文生图（Text-to-Image）

### 接口

```
POST /v1/images/generations
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | string | 固定 `"agnes-image-2.0-flash"` |
| `prompt` | string | 图片描述（英文效果最佳） |
| `n` | int | 生成数量，建议 1 |
| `size` | string | 尺寸，如 `"1024x1024"`, `"1152x768"` |
| `extra_body.tags` | array | 可选，如 `["img2img"]` 启用图生图模式 |
| `extra_body.image` | array | 可选，图生图时传入参考图 URL 数组 |

### 返回

```json
{
  "data": [
    {
      "url": "https://storage.googleapis.com/agnes-aigc-test/images/..."
    }
  ]
}
```

### Python 示例：批量生成图片

```python
import requests
import os

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://apihub.agnes-ai.com/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

prompts = [
    {"name": "fashion_woman", "prompt": "A fashionable young woman standing on a Parisian street at golden hour, wearing an elegant black dress, cinematic lighting, Vogue editorial style"},
    {"name": "perfume", "prompt": "A luxury glass perfume bottle on a reflective black surface, golden amber liquid, dramatic lighting, commercial photography"},
]

for item in prompts:
    resp = requests.post(
        f"{BASE_URL}/images/generations",
        headers=HEADERS,
        json={"model": "agnes-image-2.0-flash", "prompt": item["prompt"], "n": 1, "size": "1024x1024"},
        timeout=120,
    )
    if resp.status_code == 200:
        url = resp.json()["data"][0]["url"]
        img = requests.get(url, timeout=60)
        with open(f"{item['name']}.png", "wb") as f:
            f.write(img.content)
        print(f"Saved {item['name']}.png")
```

---

## 三、图生视频 / 多图参考视频（Image-to-Video）

### 接口

```
POST /v1/videos
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `model` | string | 固定 `"agnes-video-v2.0"` |
| `prompt` | string | 视频描述，支持中文，可用 `@图片1` `@图片2` 引用参考图 |
| `extra_body.image` | array | 参考图 URL 数组，按顺序对应 `@图片1` `@图片2` |
| `width` | int | 输出宽度，如 `1024`, `1152`, `832` |
| `height` | int | 输出高度，如 `1024`, `768`, `512` |
| `num_frames` | int | 总帧数，24fps 下：81帧≈3.4s, 121帧≈5s, 241帧≈10s, 361帧≈15s |
| `frame_rate` | int | 帧率，固定 `24` |

### 关键发现

1. **单图参考**：`extra_body.image` 传一个 URL，prompt 中用 `@图片1` 引用
2. **多图参考**：`extra_body.image` 传多个 URL，prompt 中用 `@图片1` `@图片2` 分别引用
3. **分辨率匹配**：视频 width×height 与参考图分辨率一致时参考效果最佳
4. **图片 URL**：必须使用可公开访问的 URL（Google Cloud Storage 的 URL 最稳定），第三方图床（如 catbox）可能被 API 拒绝
5. **中文 prompt**：视频模型支持中文 prompt，可直接包含台词内容

### Python 示例：多图参考生成视频（带轮询）

```python
import requests
import time
import json

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://apihub.agnes-ai.com/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# 参考图 URL
WOMAN_URL = "https://storage.googleapis.com/agnes-aigc-test/images/xxx.png"
CREAM_URL = "https://storage.googleapis.com/agnes-aigc-test/images/yyy.png"

# 中文提示词（含台词）
prompt = (
    "@图片1中美妆博主用中文进行介绍，妆容改为明艳大气，去掉脸部反光，笑容甜美，近景镜头，"
    "手持@图片2的面霜面向镜头展示，清新简约背景，元气甜美风格。"
    "博主台词：挖到本命面霜了！质地像云朵一样软糯，一抹就吸收，熬夜急救、补水保湿全搞定，素颜都自带柔光感。"
)

# 创建任务
payload = {
    "model": "agnes-video-v2.0",
    "prompt": prompt,
    "extra_body": {
        "image": [WOMAN_URL, CREAM_URL]
    },
    "width": 1024,
    "height": 1024,
    "num_frames": 121,
    "frame_rate": 24,
}

resp = requests.post(f"{BASE_URL}/videos", headers=HEADERS, json=payload, timeout=300)
task_id = resp.json()["id"]
print(f"Task created: {task_id}")

# 轮询结果（最长等 15 分钟）
start = time.time()
while time.time() - start < 900:
    r = requests.get(f"{BASE_URL}/videos/{task_id}", headers=HEADERS, timeout=30)
    d = r.json()
    status = d.get("status")
    progress = d.get("progress", 0)
    print(f"[{int(time.time()-start)}s] {status} {progress}%")
    
    if status == "completed":
        video_url = d.get("video_url")
        if video_url:
            vr = requests.get(video_url, timeout=180)
            with open("output.mp4", "wb") as f:
                f.write(vr.content)
            print(f"Saved: output.mp4 ({len(vr.content)/1024/1024:.1f} MB)")
        break
    elif status == "failed":
        print(f"Failed: {json.dumps(d, ensure_ascii=False, indent=2)}")
        break
    time.sleep(20)
```

### Python 示例：单图参考生成 15s 视频

```python
payload = {
    "model": "agnes-video-v2.0",
    "prompt": "A cinematic scene: a woman slowly turns to face the camera, golden hour lighting, soft bokeh, slow push-in camera movement, hair gently blowing in the wind",
    "extra_body": {
        "image": ["https://your-image-url.png"]
    },
    "width": 1152,
    "height": 768,
    "num_frames": 361,  # 15秒
    "frame_rate": 24,
}
```

---

## 四、图片编辑（img2img）

### 方式一：extra_body + tags

```python
payload = {
    "model": "agnes-image-2.0-flash",
    "prompt": "Change the text on the label, keep everything else exactly the same",
    "n": 1,
    "size": "1024x1024",
    "extra_body": {
        "tags": ["img2img"],
        "image": ["https://your-source-image.png"],
    },
}
resp = requests.post(f"{BASE_URL}/images/generations", headers=HEADERS, json=payload, timeout=120)
```

### 方式二：reference_images 参数

```python
payload = {
    "model": "agnes-image-2.0-flash",
    "prompt": "Change the text on the label, keep everything else exactly the same",
    "reference_images": ["https://your-source-image.png"],
    "n": 1,
    "size": "1024x1024",
}
resp = requests.post(f"{BASE_URL}/images/generations", headers=HEADERS, json=payload, timeout=120)
```

---

## 五、分辨率与帧数速查表

| 时长 | num_frames (24fps) | 推荐分辨率 |
|------|---------------------|-----------|
| ~3.4s | 81 | 832×512, 1152×768 |
| ~5s | 121 | 1024×1024, 1152×768 |
| ~10s | 241 | 1152×768 |
| ~15s | 361 | 1152×768 |

**分辨率选择建议：**
- 与参考图一致时参考效果最好（如参考图是 1024×1024，视频也设 1024×1024）
- 16:9 横屏：1152×768
- 1:1 方形：1024×1024
- 16:9 竖屏：512×832

---

## 六、常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 参考图未生效 | 分辨率不匹配 | 视频 width×height 与参考图保持一致 |
| Invalid image | 图片 URL 不可访问 | 使用 GCS 或 Agnes 自己生成的图片 URL |
| Request timeout | base64 图片过大 | 上传图片获取 URL，不要用 base64 |
| 生成失败 status=failed | prompt 过于复杂 | 简化 prompt，减少场景描述 |
| 轮询超时 | 生成时间长 | 视频生成通常需要 3-10 分钟，耐心等待 |
| 第三方图床 URL 被拒绝 | API 白名单限制 | 使用 `storage.googleapis.com/agnes-aigc-test/` 域名的 URL |

---

## 七、图片 URL 获取方式

图片 URL 必须是公网可访问的。推荐方式：
1. **用 Agnes 自己生成图片**：调用 `/v1/images/generations` 生成后，返回的 URL 直接可用
2. **使用 GCS URL**：`https://storage.googleapis.com/agnes-aigc-test/images/...` 格式
3. **避免使用**：catbox、sm.ms 等第三方图床（API 可能拒绝）

---

## 八、最佳实践

1. **图片先于视频**：先用文生图生成参考图，再用参考图生成视频
2. **prompt 写法**：中文 prompt 中用 `@图片1` `@图片2` 引用参考图数组中的对应图片
3. **台词集成**：视频模型支持在 prompt 中直接写台词，不需要额外的 TTS
4. **批量生成**：多个任务可以同时提交，然后分别轮询
5. **错误重试**：网络请求建议加 3 次重试，间隔 5 秒
6. **帧数公式**：`num_frames = 秒数 × 24 + 1`
