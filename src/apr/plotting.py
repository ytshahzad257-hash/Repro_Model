"""Small dependency-free SVG and PNG line-plot renderer.

The artifact uses this renderer so figure generation works in a clean Python
installation. It produces vector SVG plus a raster preview without embedding
any manually maintained data points.
"""

from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Series:
    label: str
    values: tuple[float, ...]
    color: str
    errors: tuple[float, ...] = ()


def _scale(value: float, low: float, high: float, start: float, length: float) -> float:
    if high == low:
        return start + length / 2
    return start + (value - low) / (high - low) * length


def _png_chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


def _write_png(path: Path, width: int, height: int, segments: list[tuple[int, int, int, int, str]]) -> None:
    pixels = bytearray([255, 255, 255] * width * height)
    palette = {"#1f77b4": (31, 119, 180), "#d62728": (214, 39, 40), "#2ca02c": (44, 160, 44), "#9467bd": (148, 103, 189), "#ff7f0e": (255, 127, 14)}

    def put(x: int, y: int, color: tuple[int, int, int]) -> None:
        if 0 <= x < width and 0 <= y < height:
            offset = (y * width + x) * 3
            pixels[offset:offset + 3] = bytes(color)

    def line(x0: int, y0: int, x1: int, y1: int, color: tuple[int, int, int]) -> None:
        dx, sx = abs(x1 - x0), 1 if x0 < x1 else -1
        dy, sy = -abs(y1 - y0), 1 if y0 < y1 else -1
        error = dx + dy
        while True:
            put(x0, y0, color)
            if x0 == x1 and y0 == y1:
                return
            twice = 2 * error
            if twice >= dy:
                error += dy
                x0 += sx
            if twice <= dx:
                error += dx
                y0 += sy

    for x0, y0, x1, y1, color_name in segments:
        line(x0, y0, x1, y1, palette.get(color_name, (31, 31, 31)))
    raw = b"".join(b"\x00" + bytes(pixels[row * width * 3:(row + 1) * width * 3]) for row in range(height))
    png = b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) + _png_chunk(b"IDAT", zlib.compress(raw, 9)) + _png_chunk(b"IEND", b"")
    path.write_bytes(png)


def line_plot(
    svg_path: Path,
    png_path: Path,
    *,
    title: str,
    x_label: str,
    y_label: str,
    x_values: tuple[float, ...],
    series: tuple[Series, ...],
    y_max: float | None = None,
) -> None:
    width, height = 900, 520
    left, top, right, bottom = 90, 55, 30, 70
    plot_width, plot_height = width - left - right, height - top - bottom
    all_values = [value + error for item in series for value, error in zip(item.values, item.errors or (0.0,) * len(item.values))]
    maximum = y_max if y_max is not None else max(all_values or [1.0]) * 1.12
    minimum = 0.0
    x_low, x_high = min(x_values), max(x_values)
    grid = []
    for step in range(6):
        value = maximum * step / 5
        y = _scale(value, minimum, maximum, top + plot_height, -plot_height)
        grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_width}" y2="{y:.1f}" stroke="#dddddd"/>')
        grid.append(f'<text x="{left - 12}" y="{y + 5:.1f}" text-anchor="end" font-size="13" fill="#333">{value:.2g}</text>')
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', f'<text x="{width / 2}" y="28" text-anchor="middle" font-size="19" font-family="Arial">{title}</text>', *grid, f'<line x1="{left}" y1="{top + plot_height}" x2="{left + plot_width}" y2="{top + plot_height}" stroke="#222"/>', f'<line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_height}" stroke="#222"/>']
    segments: list[tuple[int, int, int, int, str]] = []
    for item_index, item in enumerate(series):
        points = []
        for x_value, y_value in zip(x_values, item.values):
            x = _scale(x_value, x_low, x_high, left, plot_width)
            y = _scale(y_value, minimum, maximum, top + plot_height, -plot_height)
            points.append((x, y))
        content.append(f'<polyline fill="none" stroke="{item.color}" stroke-width="3" points="{" ".join(f"{x:.1f},{y:.1f}" for x,y in points)}"/>')
        for x, y in points:
            content.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{item.color}"/>')
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            segments.append((round(x0), round(y0), round(x1), round(y1), item.color))
    legend_x = left + 15
    for item_index, item in enumerate(series):
        x = legend_x + item_index * 170
        content.append(f'<line x1="{x}" y1="{height - 33}" x2="{x + 22}" y2="{height - 33}" stroke="{item.color}" stroke-width="3"/>')
        content.append(f'<text x="{x + 28}" y="{height - 28}" font-size="13" font-family="Arial">{item.label}</text>')
    content.append(f'<text x="{width / 2}" y="{height - 7}" text-anchor="middle" font-size="14" font-family="Arial">{x_label}</text>')
    content.append(f'<text transform="translate(17 {height / 2}) rotate(-90)" text-anchor="middle" font-size="14" font-family="Arial">{y_label}</text>')
    content.append('</svg>')
    svg_path.write_text("\n".join(content), encoding="utf-8")
    _write_png(png_path, width, height, segments)
