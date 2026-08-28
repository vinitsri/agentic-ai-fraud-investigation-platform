#!/usr/bin/env python3
"""Generate a 3D-style README GIF: payment through final fraud decision."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "architecture" / "assets" / "data-flow-animation.gif"

WIDTH, HEIGHT = 920, 450
NODE_W, NODE_H = 112, 50
DEPTH_X, DEPTH_Y = 9, 7

BG = (6, 11, 24)
BG2 = (12, 20, 38)
TEXT = (241, 245, 249)
MUTED = (148, 163, 184)
DETECT = (56, 189, 248)
INVESTIGATE = (167, 139, 250)
DECIDE = (52, 211, 153)
WARN = (251, 191, 36)
EDGE = (58, 71, 92)
SHADOW = (4, 8, 18)

NODES: list[dict[str, Any]] = [
    {"id": "payment", "label": "Payment", "sub": "transaction", "x": 18, "y": 118, "z": 0, "color": MUTED},
    {"id": "kafka", "label": "Kafka", "sub": "event stream", "x": 142, "y": 118, "z": 1, "color": DETECT},
    {"id": "fds", "label": "fraud-service", "sub": "consumer", "x": 266, "y": 118, "z": 2, "color": DETECT},
    {"id": "ml", "label": "Rules + ML", "sub": "fraud score", "x": 390, "y": 118, "z": 3, "color": DETECT},
    {"id": "alert", "label": "Fraud Alert", "sub": "suspicious", "x": 514, "y": 118, "z": 4, "color": WARN},
    {"id": "db", "label": "PostgreSQL", "sub": "persist alert", "x": 638, "y": 118, "z": 3, "color": MUTED},
    {"id": "ai", "label": "ai-service", "sub": "agents + tools", "x": 266, "y": 248, "z": 2, "color": INVESTIGATE},
    {"id": "report", "label": "Evidence", "sub": "explainable", "x": 390, "y": 248, "z": 3, "color": INVESTIGATE},
    {"id": "policy", "label": "Policy Engine", "sub": "deterministic", "x": 514, "y": 248, "z": 4, "color": DECIDE},
    {"id": "outcome", "label": "Decision", "sub": "approve/block", "x": 638, "y": 248, "z": 5, "color": DECIDE},
    {"id": "analyst", "label": "Analyst", "sub": "manual review", "x": 762, "y": 248, "z": 4, "color": DECIDE},
]

EDGES = [
    ("payment", "kafka"),
    ("kafka", "fds"),
    ("fds", "ml"),
    ("ml", "alert"),
    ("alert", "db"),
    ("alert", "ai"),
    ("ai", "report"),
    ("report", "policy"),
    ("policy", "outcome"),
    ("policy", "analyst"),
]

STEPS = [
    {"active": "payment", "edge": None, "caption": "Payment system publishes a new transaction event", "tone": DETECT},
    {"active": "kafka", "edge": ("payment", "kafka"), "caption": "Kafka streams the event in real time", "tone": DETECT},
    {"active": "fds", "edge": ("kafka", "fds"), "caption": "fraud-service consumes and builds evaluation context", "tone": DETECT},
    {"active": "ml", "edge": ("fds", "ml"), "caption": "Rules engine and ML model compute fraud score", "tone": DETECT},
    {"active": "alert", "edge": ("ml", "alert"), "caption": "Suspicious activity raises a structured fraud alert", "tone": DETECT},
    {"active": "db", "edge": ("alert", "db"), "caption": "Alert and evidence are stored in PostgreSQL", "tone": DETECT},
    {"active": "ai", "edge": ("alert", "ai"), "caption": "ai-service agents investigate using read-only tools", "tone": INVESTIGATE},
    {"active": "report", "edge": ("ai", "report"), "caption": "Agents produce an evidence report — no invented facts", "tone": INVESTIGATE},
    {"active": "policy", "edge": ("report", "policy"), "caption": "Policy engine maps recommendation to business action", "tone": DECIDE},
    {"active": "outcome", "edge": ("policy", "outcome"), "caption": "Auto outcome: APPROVE or BLOCK the payment", "tone": DECIDE},
    {"active": "analyst", "edge": ("policy", "analyst"), "caption": "Edge cases go to MANUAL_REVIEW — analyst decides", "tone": DECIDE},
]

LAYER_BANDS = [
    {"label": "1 · Detect", "y": 96, "h": 96, "accent": DETECT},
    {"label": "2 · Investigate", "y": 226, "h": 96, "accent": INVESTIGATE, "x2": 510},
    {"label": "3 · Decide", "y": 226, "h": 96, "accent": DECIDE, "x1": 510},
]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def darken(c: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(max(0, int(v * (1 - amount))) for v in c)


def lighten(c: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return blend(c, (255, 255, 255), amount)


def ease(t: float) -> float:
    return t * t * (3 - 2 * t)


def node_lift(node: dict[str, Any], active: bool, pulse: float) -> int:
    base = -node.get("z", 0) * 2
    if active:
        base -= int(4 + 3 * math.sin(pulse * math.pi * 2))
    return base


def node_box(node: dict[str, Any], lift: int = 0) -> tuple[int, int, int, int]:
    y = node["y"] + lift
    return node["x"], y, node["x"] + NODE_W, y + NODE_H


def node_center(node: dict[str, Any], lift: int = 0) -> tuple[int, int]:
    x1, y1, x2, y2 = node_box(node, lift)
    return (x1 + x2) // 2, (y1 + y2) // 2


def anchor_point(node: dict[str, Any], toward: dict[str, Any], lift: int) -> tuple[int, int]:
    cx, cy = node_center(node, lift)
    tx, ty = node_center(toward, lift)
    x1, y1, x2, y2 = node_box(node, lift)
    if abs(tx - cx) > abs(ty - cy):
        return (x2 + DEPTH_X // 2 if tx > cx else x1, cy - DEPTH_Y // 2)
    return (cx + DEPTH_X // 2, y2 if ty > cy else y1 - DEPTH_Y // 2)


def edge_points(a_id: str, b_id: str, node_map: dict[str, dict[str, Any]], lifts: dict[str, int]) -> list[tuple[float, float]]:
    a, b = node_map[a_id], node_map[b_id]
    start = anchor_point(a, b, lifts[a_id])
    end = anchor_point(b, a, lifts[b_id])

    if a_id == "alert" and b_id == "ai":
        ctrl = ((start[0] + end[0]) // 2 + 20, (start[1] + end[1]) // 2 + 40)
        return [
            (
                (1 - t) ** 2 * start[0] + 2 * (1 - t) * t * ctrl[0] + t**2 * end[0],
                (1 - t) ** 2 * start[1] + 2 * (1 - t) * t * ctrl[1] + t**2 * end[1],
            )
            for t in (i / 24 for i in range(25))
        ]

    return [
        (start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t)
        for t in (i / 24 for i in range(25))
    ]


def point_at_progress(points: list[tuple[float, float]], progress: float) -> tuple[int, int]:
    idx = min(int(progress * (len(points) - 1)), len(points) - 1)
    return int(points[idx][0]), int(points[idx][1])


def draw_perspective_floor(draw: ImageDraw.ImageDraw) -> None:
    horizon_y = 350
    for i in range(8):
        t = i / 7
        y = int(horizon_y + t * 70)
        width = int(120 + t * 360)
        x1 = WIDTH // 2 - width
        x2 = WIDTH // 2 + width
        color = blend(BG, DETECT, 0.04 + t * 0.06)
        draw.line((x1, y, x2, y), fill=color, width=1)

    for i in range(-4, 5):
        x = WIDTH // 2 + i * 70
        draw.line((x, horizon_y, WIDTH // 2 + i * 18, HEIGHT - 20), fill=blend(BG, INVESTIGATE, 0.05), width=1)


def draw_background() -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    for cx, cy, radius, color in [(140, 70, 130, DETECT), (520, 50, 150, INVESTIGATE), (780, 100, 110, DECIDE)]:
        for r in range(radius, 0, -26):
            fill = blend(BG, color, 0.028 * (1 - r / radius))
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=fill)

    draw_perspective_floor(draw)

    draw.rounded_rectangle((14, 12, WIDTH - 14, 80), radius=16, fill=BG2, outline=(45, 55, 72))
    draw.polygon([(18, 78), (28, 68), (36, 68), (26, 78)], fill=DETECT)
    draw.polygon([(36, 78), (46, 68), (54, 68), (44, 78)], fill=INVESTIGATE)
    draw.polygon([(54, 78), (64, 68), (72, 68), (62, 78)], fill=DECIDE)
    return img


def draw_layers(draw: ImageDraw.ImageDraw) -> None:
    font = load_font(10, bold=True)
    for band in LAYER_BANDS:
        x1 = band.get("x1", 16)
        x2 = band.get("x2", WIDTH - 16)
        fill = blend(BG, band["accent"], 0.07)
        draw.rounded_rectangle((x1, band["y"], x2, band["y"] + band["h"]), radius=14, fill=fill, outline=blend(BG, band["accent"], 0.22))
        draw.polygon([(x1, band["y"] + 10), (x1 + 8, band["y"] + 4), (x1 + 8, band["y"] + 16)], fill=band["accent"])
        draw.text((x1 + 16, band["y"] + 10), band["label"].upper(), fill=blend(TEXT, band["accent"], 0.35), font=font)


def draw_progress(draw: ImageDraw.ImageDraw, step_index: int, edge_progress: float) -> None:
    total = len(STEPS)
    progress = (step_index + edge_progress) / total
    bar_x, bar_y, bar_w, bar_h = 24, HEIGHT - 36, WIDTH - 48, 10
    draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), radius=5, fill=(18, 28, 46), outline=(45, 55, 72))
    fill_w = max(10, int(bar_w * progress))
    for i in range(20):
        t = i / 19
        color = blend(DETECT, DECIDE, t)
        sx = bar_x + int((fill_w - 10) * i / 20)
        draw.rectangle((sx, bar_y + 2, min(bar_x + fill_w, sx + fill_w // 20 + 2), bar_y + bar_h - 2), fill=color)

    font = load_font(10, bold=True)
    draw.rounded_rectangle((WIDTH - 92, 26, WIDTH - 24, 54), radius=12, fill=blend(BG2, DETECT, 0.18), outline=DETECT)
    draw.text((WIDTH - 58, 40), f"{step_index + 1}/{total}", fill=TEXT, font=font, anchor="mm")


def draw_shadow(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], strength: float = 1.0) -> None:
    x1, y1, x2, y2 = box
    cy = y2 + 8
    cx = (x1 + x2) // 2 + DEPTH_X // 2
    w = int((x2 - x1) * 0.55 * strength)
    h = 8
    draw.ellipse((cx - w, cy - h, cx + w, cy + h), fill=blend(SHADOW, BG, 0.15))


def draw_3d_node(
    draw: ImageDraw.ImageDraw,
    node: dict[str, Any],
    *,
    active: bool,
    visited: bool,
    pulse: float,
    fonts: dict[str, ImageFont.ImageFont | ImageFont.FreeTypeFont],
) -> None:
    lift = node_lift(node, active, pulse)
    box = node_box(node, lift)
    x1, y1, x2, y2 = box
    color = node["color"]

    if active:
        front = blend(BG2, color, 0.28 + 0.06 * math.sin(pulse * math.pi * 2))
        top = lighten(front, 0.18)
        side = darken(front, 0.28)
        outline = lighten(color, 0.1)
    elif visited:
        front = blend(BG2, color, 0.14)
        top = lighten(front, 0.12)
        side = darken(front, 0.22)
        outline = blend(color, EDGE, 0.4)
    else:
        front = BG2
        top = lighten(front, 0.08)
        side = darken(front, 0.18)
        outline = EDGE

    draw_shadow(draw, box, 1.3 if active else 0.9)

    side_poly = [(x2, y1), (x2 + DEPTH_X, y1 + DEPTH_Y), (x2 + DEPTH_X, y2 + DEPTH_Y), (x2, y2)]
    top_poly = [(x1, y1), (x1 + DEPTH_X, y1 - DEPTH_Y), (x2 + DEPTH_X, y1 - DEPTH_Y), (x2, y1)]
    draw.polygon(side_poly, fill=side, outline=outline)
    draw.polygon(top_poly, fill=top, outline=outline)
    draw.rounded_rectangle(box, radius=10, fill=front, outline=outline, width=2 if active else 1)

    if active or visited:
        draw.rounded_rectangle((x1 + 2, y1 + 2, x2 - 2, y1 + 6), radius=6, fill=color)

    cx = (x1 + x2) // 2
    draw.text((cx, y1 + 15), node["label"], fill=TEXT, font=fonts["label"], anchor="mm")
    draw.text((cx, y1 + 31), node["sub"], fill=MUTED, font=fonts["sub"], anchor="mm")

    if active:
        for expand, alpha in [(12, 0.06), (8, 0.1), (4, 0.14)]:
            glow = blend(BG, color, alpha * (0.8 + 0.2 * math.sin(pulse * math.pi * 2)))
            draw.rounded_rectangle((x1 - expand, y1 - expand, x2 + expand, y2 + expand), radius=14, outline=glow, width=2)


def draw_3d_edge(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    *,
    active: bool,
    tone: tuple[int, int, int],
    progress: float,
) -> None:
    if len(points) < 2:
        return

    offset = 3
    shadow_pts = [(p[0] + offset, p[1] + offset) for p in points]
    for i in range(len(shadow_pts) - 1):
        draw.line((*shadow_pts[i], *shadow_pts[i + 1]), fill=SHADOW, width=4)

    for i in range(len(points) - 1):
        draw.line((*points[i], *points[i + 1]), fill=EDGE if not active else darken(tone, 0.35), width=3)

    if active:
        for i in range(len(points) - 1):
            draw.line((*points[i], *points[i + 1]), fill=tone, width=2)

        eased = ease(progress)
        for offset, size, alpha in [(0.0, 8, 1.0), (0.1, 6, 0.6), (0.2, 4, 0.35)]:
            p = max(0.0, eased - offset)
            x, y = point_at_progress(points, p)
            draw.ellipse((x - size, y - size - 2, x + size, y + size - 2), fill=blend(BG, (255, 255, 255), alpha))
            draw.ellipse((x - size + 2, y - size, x + size - 2, y + size - 4), fill=blend(tone, (255, 255, 255), 0.45))


def visited_nodes(step_index: int) -> set[str]:
    seen: set[str] = set()
    for i in range(step_index):
        seen.add(STEPS[i]["active"])
        edge = STEPS[i]["edge"]
        if edge:
            seen.add(edge[1])
    return seen


def render_frame(step_index: int, step: dict[str, Any], edge_progress: float, pulse: float) -> Image.Image:
    img = draw_background()
    draw = ImageDraw.Draw(img)
    fonts = {
        "title": load_font(18, bold=True),
        "caption": load_font(13),
        "label": load_font(10, bold=True),
        "sub": load_font(9),
        "footer": load_font(10),
    }

    draw_layers(draw)
    draw.text((32, 28), "Fraud Investigation Platform", fill=TEXT, font=fonts["title"])
    draw.text((32, 54), step["caption"], fill=step["tone"], font=fonts["caption"])
    draw_progress(draw, step_index, edge_progress)

    node_map = {n["id"]: n for n in NODES}
    visited = visited_nodes(step_index)
    lifts = {
        n["id"]: node_lift(n, step["active"] == n["id"], pulse if step["active"] == n["id"] else 0)
        for n in NODES
    }

    sorted_nodes = sorted(NODES, key=lambda n: n["y"] + lifts[n["id"]], reverse=True)

    for a_id, b_id in EDGES:
        points = edge_points(a_id, b_id, node_map, lifts)
        draw_3d_edge(draw, points, active=step["edge"] == (a_id, b_id), tone=step["tone"], progress=edge_progress)

    for node in sorted_nodes:
        draw_3d_node(
            draw,
            node,
            active=step["active"] == node["id"],
            visited=node["id"] in visited,
            pulse=pulse,
            fonts=fonts,
        )

    draw.text(
        (32, HEIGHT - 16),
        "Payment  →  Detect  →  Investigate  →  Policy  →  APPROVE | BLOCK | MANUAL_REVIEW",
        fill=MUTED,
        font=fonts["footer"],
    )
    return img


def main() -> None:
    frames: list[Image.Image] = []
    frames_per_step = 9

    for step_index, step in enumerate(STEPS):
        for i in range(frames_per_step):
            progress = ease(i / (frames_per_step - 1)) if step["edge"] else 0.0
            pulse = i / frames_per_step
            frames.append(render_frame(step_index, step, progress, pulse))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    palette = frames[0].quantize(colors=96, method=Image.Quantize.MEDIANCUT)
    quantized = [palette if i == 0 else f.quantize(palette=palette, dither=Image.Dither.FLOYDSTEINBERG) for i, f in enumerate(frames)]

    quantized[0].save(
        OUTPUT,
        save_all=True,
        append_images=quantized[1:],
        duration=300,
        loop=0,
        optimize=True,
    )
    print(f"Wrote {OUTPUT} ({len(frames)} frames, {OUTPUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
