import pygame
import constants as K
import assets
from topics import TOPICS

ROW_H = 36
INDENT = 20

def recalc_layout(w, h):
    K.WIDTH  = max(K.MIN_W, w)
    K.HEIGHT = max(K.MIN_H, h)
    K.SIDEBAR_W = max(260, min(480, int(K.WIDTH * 0.29)))
    assets.rescale_background(K.WIDTH, K.HEIGHT)

def render_sidebar(scroll_y, selected_id):
    sidebar = pygame.Surface((K.SIDEBAR_W, K.HEIGHT))
    sidebar.fill((255, 250, 230))

    hitboxes = []
    y = -scroll_y + 10

    def draw_node(node, depth):
        nonlocal y
        x = 10 + depth * INDENT

        is_selected = node["id"] == selected_id
        has_children = bool(node.get("children"))
        expanded = node.get("expanded", False)

        # Fondo si está seleccionado
        if is_selected:
            pygame.draw.rect(sidebar, (255, 220, 180), pygame.Rect(0, y, K.SIDEBAR_W, ROW_H))

        # Flecha si tiene hijos
        if has_children:
            arrow = "▼" if expanded else "-"
            arrow_img = K.FONT_B.render(arrow, True, K.TEXT)
            sidebar.blit(arrow_img, (x, y + 8))
            x += 20

        # Título del nodo
        title_img = K.FONT_B.render(node["title"], True, K.TEXT)
        sidebar.blit(title_img, (x, y + 8))

        # Hitbox para clic
        hitboxes.append((pygame.Rect(0, y, K.SIDEBAR_W, ROW_H), node["id"]))
        y += ROW_H

        # Dibujar hijos si está expandido
        if expanded and has_children:
            for child in node["children"]:
                draw_node(child, depth + 1)

    for node in TOPICS:
        draw_node(node, depth=0)

    content_h = y + scroll_y
    return sidebar, hitboxes, content_h

def find_by_id(tree, nid):
    for node in tree:
        if node["id"] == nid:
            return node
        if node.get("children"):
            found = find_by_id(node["children"], nid)
            if found:
                return found
    return None
