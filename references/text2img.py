"""Agnes AI 文生图示例"""
import requests
import os

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://apihub.agnes-ai.com/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

prompts = [
    {
        "name": "fashion_woman",
        "prompt": (
            "A fashionable young woman standing on a Parisian street at golden hour, "
            "wearing an elegant black dress and high heels, holding a designer handbag, "
            "wind gently blowing her hair, cinematic lighting, shallow depth of field, "
            "Vogue magazine editorial style, high fashion photography, 35mm film look"
        ),
    },
    {
        "name": "perfume",
        "prompt": (
            "A luxury glass perfume bottle on a reflective black surface, "
            "golden amber liquid inside, soft dramatic lighting from the side, "
            "dark moody background with bokeh, cinematic product photography, "
            "high-end commercial advertising style, sharp focus on bottle details"
        ),
    },
]

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

for item in prompts:
    print(f"\nGenerating: {item['name']}", flush=True)
    try:
        resp = requests.post(
            f"{BASE_URL}/images/generations",
            headers=HEADERS,
            json={
                "model": "agnes-image-2.0-flash",
                "prompt": item["prompt"],
                "n": 1,
                "size": "1024x1024",
            },
            timeout=120,
        )
        if resp.status_code == 200:
            url = resp.json().get("data", [{}])[0].get("url")
            if url:
                img = requests.get(url, timeout=60)
                if img.status_code == 200:
                    save = os.path.join(SAVE_DIR, f"{item['name']}.png")
                    with open(save, "wb") as f:
                        f.write(img.content)
                    print(f"  saved: {save} ({len(img.content)/1024:.0f} KB)", flush=True)
        else:
            print(f"  error: {resp.text[:300]}", flush=True)
    except Exception as e:
        print(f"  failed: {e}", flush=True)

print("\nDone", flush=True)
