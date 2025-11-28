import pygame
import sys

import constants as K
from assets import background_img, logo_img, initial_title, rescale_background
from topics import TOPICS
from layout import render_sidebar, recalc_layout, find_by_id
from widgets import VerticalScrollbar
from simulations import SIM_REGISTRY

pygame.init()

# Crear ventana
screen = pygame.display.set_mode((K.WIDTH, K.HEIGHT), pygame.RESIZABLE | pygame.DOUBLEBUF)
pygame.display.set_caption("Tematica: Ciencias de la Computación II")

def main():
    global screen
    clock = pygame.time.Clock()
    running = True

    selected_id = None
    scroll_y = 0
    sidebar_visible = True
    current_sim = None

    # Sidebar inicial
    sidebar, hitboxes, content_h = render_sidebar(scroll_y, selected_id)
    scrollbar = VerticalScrollbar(max(0, K.SIDEBAR_W - 12), 0, K.HEIGHT, content_h) if sidebar_visible else None

    while running:
        dt = clock.tick(60) / 1000.0
        if current_sim:
            current_sim.update(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                # Recalcular layout y redimensionar ventana
                recalc_layout(event.w, event.h)
                screen = pygame.display.set_mode((K.WIDTH, K.HEIGHT), pygame.RESIZABLE | pygame.DOUBLEBUF)

                # Re-render sidebar y scrollbar según nuevo tamaño
                sidebar, hitboxes, content_h = render_sidebar(scroll_y, selected_id)
                scrollbar = VerticalScrollbar(max(0, K.SIDEBAR_W - 12), 0, K.HEIGHT, content_h) if sidebar_visible else None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Coordenadas locales del panel derecho
                sidebar_width = K.SIDEBAR_W if sidebar_visible else 0
                local_x = mx - sidebar_width
                local_y = my

                # Botón de toggle sidebar (en panel derecho)
                if 0 <= local_x <= 30 and 0 <= local_y <= 30:
                    sidebar_visible = not sidebar_visible
                    # Re-render tras toggle
                    sidebar, hitboxes, content_h = render_sidebar(scroll_y, selected_id)
                    scrollbar = VerticalScrollbar(max(0, (K.SIDEBAR_W if sidebar_visible else 0) - 12), 0, K.HEIGHT, content_h) if sidebar_visible else None
                    continue

                # Clicks en el sidebar (solo si visible)
                if sidebar_visible and mx < K.SIDEBAR_W:
                    for rect, nid in hitboxes:
                        if rect.collidepoint(mx, my):
                            node = find_by_id(TOPICS, nid)
                            if node and node.get("children"):
                                node["expanded"] = not node.get("expanded", False)
                            else:
                                # Cambio de simulación
                                if current_sim:
                                    current_sim.on_deselect()
                                selected_id = nid
                                current_sim = SIM_REGISTRY.get(selected_id, None)
                                if current_sim:
                                    current_sim.on_select()
                            sidebar, hitboxes, content_h = render_sidebar(scroll_y, selected_id)
                            scrollbar = VerticalScrollbar(max(0, K.SIDEBAR_W - 12), 0, K.HEIGHT, content_h) if sidebar_visible else None
                            break
                else:
                    # Click fuera del sidebar -> delegar a simulación activa
                    if current_sim:
                        current_sim.handle_event(event, None, (sidebar_width, 0))

            elif sidebar_visible and scrollbar and scrollbar.handle_event(event):
                scroll_y = scrollbar.get_scroll()
                sidebar, hitboxes, content_h = render_sidebar(scroll_y, selected_id)
                scrollbar.update_content_height(content_h)

            elif event.type == pygame.KEYDOWN:
                if current_sim:
                    current_sim.handle_event(event, None, (sidebar_width if sidebar_visible else 0, 0))

        # Dimensiones actuales
        sidebar_width = K.SIDEBAR_W if sidebar_visible else 0
        right_w = K.WIDTH - sidebar_width

        # Fondo
        screen.fill(K.BG)

        # Sidebar
        if sidebar_visible:
            screen.blit(sidebar, (0, 0))
            if scrollbar:
                scrollbar.rect.x = max(0, sidebar_width - 12)
                scrollbar.draw(screen)

        # Panel derecho
        right = pygame.Surface((right_w, K.HEIGHT))
        node = find_by_id(TOPICS, selected_id) if selected_id else None

        if node is None:
            right.fill((255, 255, 255))
            logo_x = (right_w - logo_img.get_width()) // 2
            logo_y = 30
            right.blit(logo_img, (logo_x, logo_y))

            title_img = K.FONT_T.render(initial_title, True, K.TEXT)
            title_x = (right_w - title_img.get_width()) // 2
            title_y = logo_y + logo_img.get_height() + 20
            right.blit(title_img, (title_x, title_y))
        else:
            right.fill((255, 255, 255))
            title_img = K.FONT_T.render(node["title"], True, K.TEXT)
            right.blit(title_img, (20, 20))

            # Área de simulación
            sim_rect = pygame.Rect(16, K.HEADER_H, right_w - 32, K.HEIGHT - K.HEADER_H - 16)
            
            if current_sim:
                current_sim.render(right, sim_rect)
            else:
                # Placeholder cuando no hay simulación
                pygame.draw.rect(right, (255, 248, 227), sim_rect, border_radius=10)
                pygame.draw.rect(right, K.DIVIDER, sim_rect, 1, border_radius=10)
                label = K.FONT_B.render("Simulación", True, K.ACCENT)
                right.blit(label, (sim_rect.x + 16, sim_rect.y + 12))
                pygame.draw.line(right, K.DIVIDER, (sim_rect.x + 12, sim_rect.y + 48), 
                                (sim_rect.right - 12, sim_rect.y + 48), 1)
                help_txt = "Seleccione una temática para ver su simulación"
                right.blit(K.FONT.render(help_txt, True, K.SUBTEXT), (sim_rect.x + 16, sim_rect.y + 56))

        # Botón de toggle sidebar (panel derecho)
        toggle_btn = pygame.Rect(0, 0, 30, 30)
        pygame.draw.rect(right, (230, 230, 230), toggle_btn, border_radius=6)
        arrow = "«" if sidebar_visible else "»"
        arrow_img = K.FONT_B.render(arrow, True, K.TEXT)
        right.blit(arrow_img, (7, 5))

        # Pintar panel derecho
        screen.blit(right, (sidebar_width, 0))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
