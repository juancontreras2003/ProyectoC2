import pygame

def draw_input_box(surface, x, y, width, height, text, font, color_text, color_border, active=True):
    rect = pygame.Rect(x, y, width, height)
    box_color = (255,255,255) if active else (245,245,245)
    pygame.draw.rect(surface, box_color, rect, 0)
    pygame.draw.rect(surface, color_border, rect, 2)
    text_surface = font.render(text, True, color_text)
    surface.blit(text_surface, (x+6, y+(height-text_surface.get_height())//2))
    return rect

class VerticalScrollbar:
    def __init__(self, x, y, height, content_height):
        self.rect = pygame.Rect(x, y, 18, height)
        self.content_height = content_height
        self.view_height = height
        self.handle_height = max(30, height * height / content_height)
        self.handle_rect = pygame.Rect(x, y, 18, self.handle_height)
        self.dragging = False
        self.drag_offset = 0

    def update_content_height(self, content_height):
        self.content_height = content_height
        self.handle_height = max(30, self.view_height * self.view_height / content_height)
        self.handle_rect.height = self.handle_height

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                self.drag_offset = event.pos[1] - self.handle_rect.y
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            return True
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            new_y = event.pos[1] - self.drag_offset
            min_y = self.rect.y
            max_y = self.rect.y + self.view_height - self.handle_height
            self.handle_rect.y = max(min_y, min(max_y, new_y))
            return True
        elif event.type == pygame.MOUSEWHEEL:
            scroll_amount = -event.y * 20
            new_y = self.handle_rect.y + scroll_amount
            min_y = self.rect.y
            max_y = self.rect.y + self.view_height - self.handle_height
            self.handle_rect.y = max(min_y, min(max_y, new_y))
            return True
        return False

    def get_scroll(self):
        max_scroll = self.content_height - self.view_height
        if max_scroll <= 0:
            return 0
        rel = (self.handle_rect.y - self.rect.y) / (self.view_height - self.handle_height)
        return rel * max_scroll

    def draw(self, surface):
        pygame.draw.rect(surface, (220,220,220), self.rect, border_radius=8)
        pygame.draw.rect(surface, (120,120,120), self.handle_rect, border_radius=7)
