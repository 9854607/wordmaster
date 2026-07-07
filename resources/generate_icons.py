"""
WordMaster App Icon Generator
生成 Android 所有密度的图标 PNG（含自适应图标前后景）
"""

from PIL import Image, ImageDraw, ImageFont
import os
import math

# --- 配置 ---
BG_COLOR = (8, 8, 15)  # #08080f
ACCENT_START = (123, 147, 255)  # #7b93ff
ACCENT_END = (176, 149, 249)    # #b095f9
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'android', 'app', 'src', 'main', 'res')

DENSITIES = {
    'mdpi': 48,
    'hdpi': 72,
    'xhdpi': 96,
    'xxhdpi': 144,
    'xxxhdpi': 192,
}

FOREGROUND_SCALE = 0.6  # 前景图标占背景的比例（自适应图标规范: 72/108 = 2/3）
SAFE_ZONE = 108  # 自适应图标安全区基准


def lerp_color(c1, c2, t):
    """线性插值两个 RGB 颜色"""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def gradient_fill(draw, size, c1, c2, angle=135):
    """用渐变填充矩形"""
    w, h = size
    # 计算渐变方向的单位向量
    rad = math.radians(angle)
    dx, dy = math.cos(rad), math.sin(rad)
    # 投影范围
    corners = [(0, 0), (w, 0), (0, h), (w, h)]
    proj = [x * dx + y * dy for x, y in corners]
    p_min, p_max = min(proj), max(proj)

    for y in range(h):
        for x in range(w):
            t = ((x * dx + y * dy) - p_min) / (p_max - p_min) if p_max != p_min else 0
            t = max(0, min(1, t))
            draw.point((x, y), fill=lerp_color(c1, c2, t))


def draw_wm_letter(draw, size, scale=1.0):
    """绘制 'W' 字母作为图标主体，带渐变"""
    w, h = size
    center_x, center_y = w / 2, h / 2

    # 画布尺寸作为基准
    base = min(w, h)
    margin = base * 0.15
    letter_w = base * 0.7 * scale
    letter_h = base * 0.55 * scale

    # W 字母的四个顶点
    left = center_x - letter_w / 2
    right = center_x + letter_w / 2
    top = center_y - letter_h / 2
    bot = center_y + letter_h / 2

    # W 的路径：左底 → 左中顶 → 中间谷 → 右中顶 → 右底
    mid_left = left + letter_w * 0.25
    mid_right = right - letter_w * 0.25
    mid_bot = center_y + letter_h * 0.15

    stroke = max(3, int(base * 0.08 * scale))

    # 画 W 的每一条线段（用渐变上色）
    segments = [
        (left, bot, mid_left, mid_bot),      # 左下到中谷
        (mid_left, mid_bot, center_x, top),   # 中谷到顶部
        (center_x, top, mid_right, mid_bot),  # 顶部到中谷
        (mid_right, mid_bot, right, bot),     # 中谷到右下
    ]

    for i, (x1, y1, x2, y2) in enumerate(segments):
        t = i / (len(segments) - 1)
        color = lerp_color(ACCENT_START, ACCENT_END, t)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=stroke)


def draw_regular_icon(size, as_foreground=False):
    """绘制常规图标（填满整个画布）"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if as_foreground:
        # 前景层：透明底 + 字母
        draw_wm_letter(draw, (size, size), scale=1.0)
    else:
        # 完整图标：暗色底 + 渐变 + 字母
        # 圆角矩形背景
        r = size * 0.18
        draw.rounded_rectangle(
            [(0, 0), (size - 1, size - 1)],
            radius=int(r),
            fill=BG_COLOR
        )
        # 微妙的渐变叠加
        center = size / 2
        for y in range(size):
            for x in range(size):
                dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)
                max_dist = center * 1.2
                t = min(1, dist / max_dist)
                original = BG_COLOR
                glow = lerp_color(ACCENT_START, ACCENT_END, 0.3)
                r_val = int(original[0] + (glow[0] - original[0]) * t * 0.15)
                g_val = int(original[1] + (glow[1] - original[1]) * t * 0.15)
                b_val = int(original[2] + (glow[2] - original[2]) * t * 0.15)
                draw.point((x, y), fill=(r_val, g_val, b_val, 255))

        # 字母
        draw_wm_letter(draw, (size, size), scale=1.0)

    return img


def draw_background_layer(size):
    """自适应图标背景层：纯暗色底 + 径向渐变微光"""
    img = Image.new('RGBA', (size, size), BG_COLOR + (255,))
    draw = ImageDraw.Draw(img)

    center = size / 2
    for y in range(size):
        for x in range(size):
            dist = math.sqrt((x - center) ** 2 + (y - center) ** 2)
            max_dist = center * 1.3
            t = min(1, dist / max_dist)
            # 中心微亮
            r_val = int(BG_COLOR[0] + (30 - BG_COLOR[0]) * (1 - t) * 0.4)
            g_val = int(BG_COLOR[1] + (25 - BG_COLOR[1]) * (1 - t) * 0.4)
            b_val = int(BG_COLOR[2] + (50 - BG_COLOR[2]) * (1 - t) * 0.4)
            draw.point((x, y), fill=(r_val, g_val, b_val, 255))

    return img


def generate_all():
    """生成所有图标"""
    print("Generating WordMaster app icons...")

    # ========== 1. 常规启动图标 ==========
    for density, size in DENSITIES.items():
        dir_path = os.path.join(OUTPUT_DIR, f'mipmap-{density}')
        os.makedirs(dir_path, exist_ok=True)

        img = draw_regular_icon(size)
        out = os.path.join(dir_path, 'ic_launcher.png')
        img.save(out, 'PNG')
        print(f"  {out} ({size}x{size})")

        # 圆标
        round_out = os.path.join(dir_path, 'ic_launcher_round.png')
        img.save(round_out, 'PNG')
        print(f"  {round_out} ({size}x{size})")

    # ========== 2. 自适应图标（Android 8+）==========
    for density, size in DENSITIES.items():
        dir_path = os.path.join(OUTPUT_DIR, f'mipmap-{density}')
        os.makedirs(dir_path, exist_ok=True)

        # 前景层（安全区内，缩小到 66%）
        fg_size = int(size * FOREGROUND_SCALE)
        fg_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        inner = draw_regular_icon(fg_size, as_foreground=True)
        offset = (size - fg_size) // 2
        fg_img.paste(inner, (offset, offset), inner)

        fg_out = os.path.join(dir_path, 'ic_launcher_foreground.png')
        fg_img.save(fg_out, 'PNG')
        print(f"  {fg_out} ({size}x{size})")

        # 背景层
        bg_img = draw_background_layer(size)
        bg_out = os.path.join(dir_path, 'ic_launcher_background.png')
        bg_img.save(bg_out, 'PNG')
        print(f"  {bg_out} ({size}x{size})")

    # ========== 3. 512px 高清图标（存档用）==========
    hd = draw_regular_icon(512)
    hd_out = os.path.join(os.path.dirname(__file__), 'icon-512.png')
    hd.save(hd_out, 'PNG')
    print(f"  {hd_out} (512x512)")

    print("\nDone! All icons generated.")


if __name__ == '__main__':
    generate_all()
