from textwrap import wrap
import pygame

def draw_wrapped_text(surface, text, font, color, rect, line_h):
    if not text:
        return
    max_chars = max(8, rect.w // 8)
    lines = []
    for p in text.split("\n"):
        lines.extend(wrap(p, width=max_chars))
    y = rect.y
    for ln in lines:
        img = font.render(ln, True, color)
        surface.blit(img, (rect.x, y))
        y += line_h
