"""Agnes AI 图片编辑（img2img）示例"""
import requests
import os

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://apihub.agnes-ai.com/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

# 源图片 URL
IMG_URL = "https://storage.googleapis.com/agnes-aigc-test/images/text-to-image/2026/06/827767df1cd74805a4bc3013d1779035.png"

prompt = (
    "Change the text on the perfume bottle label from 'Agnes' to '不是哥们', "
    "keep everything else exactly the same: same bottle shape, same liquid color, "
    "same lighting, same white background, same composition, same angle"
)

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

# 方法一：extra_body + tags
print("Method 1: extra_body with tags img2img", flush=True)
resp1 = requests.post(
    f"{BASE_URL}/images/generations",
    headers=HEADERS,
    json={
        "model": "agnes-image-2.0-flash",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "extra_body": {"tags": ["img2img"], "image": [IMG_URL]},
    },
    timeout=120,
)
if resp1.status_code == 200:
    url1 = resp1.json().get("data", [{}])[0].get("url")
    if url1:
        ir = requests.get(url1, timeout=60)
        if ir.status_code == 200:
            with open(os.path.join(SAVE_DIR, "result_v1.png"), "wb") as f:
                f.write(ir.content)
            print(f"  Saved: result_v1.png ({len(ir.content)/1024:.0f} KB)")

# 方法二：reference_images 参数
print("\nMethod 2: reference_images parameter", flush=True)
resp2 = requests.post(
    f"{BASE_URL}/images/generations",
    headers=HEADERS,
    json={
        "model": "agnes-image-2.0-flash",
        "prompt": prompt,
        "reference_images": [IMG_URL],
        "n": 1,
        "size": "1024x1024",
    },
    timeout=120,
)
if resp2.status_code == 200:
    url2 = resp2.json().get("data", [{}])[0].get("url")
    if url2:
        ir = requests.get(url2, timeout=60)
        if ir.status_code == 200:
            with open(os.path.join(SAVE_DIR, "result_v2.png"), "wb") as f:
                f.write(ir.content)
            print(f"  Saved: result_v2.png ({len(ir.content)/1024:.0f} KB)")

print("\nDone")
