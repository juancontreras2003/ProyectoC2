"""
Módulo base para simulaciones.
Contiene la clase base Simulation y PlaceholderSim para temas sin implementar.
"""
import pygame
import constants as K


class Simulation:
    """Clase base abstracta para todas las simulaciones."""
    
    def __init__(self, topic_id: str, title: str):
        self.topic_id = topic_id
        self.title = title

    def on_select(self):
        """Se llama al activarse la simulación."""
        pass

    def on_deselect(self):
        """Se llama al desactivarse la simulación."""
        pass

    def handle_event(self, event, viewport_rect: pygame.Rect, window_offset: tuple[int, int]):
        """Delegar eventos (ratón/teclado)."""
        pass

    def update(self, dt: float):
        """Actualiza la animación (si hay)."""
        pass

    def get_content_height(self, sim_rect: pygame.Rect) -> int:
        """
        Retorna la altura total del contenido a renderizar.
        Override en subclases si el contenido excede sim_rect.height
        """
        return sim_rect.height

    def render(self, surface: pygame.Surface, sim_rect: pygame.Rect):
        """Dibujar contenido de la simulación."""
        label = K.FONT_B.render("Simulación", True, K.ACCENT)
        surface.blit(label, (sim_rect.x + 16, sim_rect.y + 12))
        pygame.draw.line(surface, K.DIVIDER, (sim_rect.x + 12, sim_rect.y + 48), 
                        (sim_rect.right - 12, sim_rect.y + 48), 1)
        help_txt = "Simulación en preparación…"
        surface.blit(K.FONT.render(help_txt, True, K.SUBTEXT), (sim_rect.x + 16, sim_rect.y + 56))


class PlaceholderSim(Simulation):
    """Simulación placeholder para temas sin implementar."""
    
    def __init__(self, topic_id: str, title: str, message: str = "Próximamente"):
        super().__init__(topic_id, title)
        self.message = message

    def render(self, surface: pygame.Surface, sim_rect: pygame.Rect):
        # Marco base
        pygame.draw.rect(surface, (255, 248, 227), sim_rect, border_radius=10)
        pygame.draw.rect(surface, K.DIVIDER, sim_rect, 1, border_radius=10)
        # Título de la simulación
        label = K.FONT_B.render(self.title, True, K.ACCENT)
        surface.blit(label, (sim_rect.x + 16, sim_rect.y + 12))
        pygame.draw.line(surface, K.DIVIDER, (sim_rect.x + 12, sim_rect.y + 48), 
                        (sim_rect.right - 12, sim_rect.y + 48), 1)
        # Mensaje
        surface.blit(K.FONT.render(self.message, True, K.SUBTEXT), (sim_rect.x + 16, sim_rect.y + 60))
