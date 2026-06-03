"""Agnes AI 首尾帧视频生成示例

使用两张图片（首帧 + 尾帧），模型自动生成中间的平滑过渡视频。
适合：变妆效果、表情变化、产品展示动画等。
"""
import requests
import time
import json

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://apihub.agnes-ai.com/v1"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
SAVE_DIR = "."

# 首帧（起始状态）和尾帧（结束状态）
FIRST_FRAME = "https://storage.googleapis.com/agnes-aigc-test/images/text-to-image/2026/06/xxx_start.png"
LAST_FRAME = "https://storage.googleapis.com/agnes-aigc-test/images/text-to-image/2026/06/xxx_end.png"

# 中文提示词（@图片1 = 首帧，@图片2 = 尾帧）
prompt = (
    "@图片1中的人物逐渐转变为@图片2的样子，妆容从淡雅变为明艳大气，笑容甜美，"
    "近景镜头，清新简约背景，元气甜美风格。"
    "博主台词：挖到本命面霜了！质地像云朵一样软糯，一抹就吸收，熬夜急救、补水保湿全搞定，素颜都自带柔光感。"
)


def create_task(prompt, first_frame, last_frame, width=1024, height=1024, num_frames=121, frame_rate=24):
    """创建首尾帧视频生成任务"""
    payload = {
        "model": "agnes-video-v2.0",
        "prompt": prompt,
        "extra_body": {"image": [first_frame, last_frame]},
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "frame_rate": frame_rate,
    }
    resp = requests.post(f"{BASE_URL}/videos", headers=HEADERS, json=payload, timeout=300)
    if resp.status_code == 200:
        data = resp.json()
        return data.get("id")
    else:
        print(f"  创建失败: {resp.text[:500]}")
        return None


def poll_task(task_id, save_path, timeout=900, interval=20):
    """轮询任务状态并下载视频"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE_URL}/videos/{task_id}", headers=HEADERS, timeout=30)
            if r.status_code == 200:
                d = r.json()
                status = d.get("status")
                progress = d.get("progress", 0)
                elapsed = int(time.time() - start)
                print(f"  [{elapsed}s] {status} {progress}%", flush=True)

                if status == "completed":
                    video_url = d.get("video_url")
                    if video_url:
                        vr = requests.get(video_url, timeout=180)
                        if vr.status_code == 200:
                            with open(save_path, "wb") as f:
                                f.write(vr.content)
                            print(f"  Saved: {save_path} ({len(vr.content)/1024/1024:.1f} MB)")
                            return save_path
                    return None
                elif status == "failed":
                    print(f"  FAILED: {json.dumps(d, ensure_ascii=False, indent=2)}")
                    return None
        except Exception as e:
            print(f"  exception: {e}")
        time.sleep(interval)
    print("  TIMEOUT")
    return None


if __name__ == "__main__":
    print("=" * 60)
    print("Agnes Video - First-Last Frame Generation")
    print("=" * 60)

    task_id = create_task(
        prompt=prompt,
        first_frame=FIRST_FRAME,
        last_frame=LAST_FRAME,
        width=1024,
        height=1024,
        num_frames=121,
        frame_rate=24,
    )

    if task_id:
        print(f"\nTask ID: {task_id}")
        poll_task(task_id, f"{SAVE_DIR}/output.mp4")
    else:
        print("Task creation failed")

    print("\nDone")
