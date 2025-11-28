"""
Simulación de Búsqueda Secuencial.
Implementa búsqueda secuencial con animación paso a paso.
"""
import pygame
import bisect
import pickle

import constants as K
from widgets import draw_input_box, VerticalScrollbar
from simulations.base import Simulation
from simulations.dialogs import save_file_dialog, open_file_dialog


class SequentialSearchSim(Simulation):
    """Simulación de búsqueda secuencial con animación."""
    
    def __init__(self):
        super().__init__("1.1.A", "Búsqueda Secuencial")
        # Estado de inputs
        self.N_text = ""
        self.count_text = ""    # "Tamaño de clave"
        self.k_text = ""
        self.N = None
        self.max_keys = None  # longitud exigida de la clave
        # Datos ORDENADOS
        self.keys = []
        self.status = ""
        # Foco e interacciones
        self.active_field = None  # "N" | "COUNT" | "K" | None
        self._rect_N = None
        self._rect_COUNT = None
        self._rect_K = None
        self._button_rects = []   # [(rect, action)]
        # Layout
        self.max_cols = 10
        self.box_size = 50
        self.spacing = 10
        # Scrollbar para grilla grande
        self.scrollbar = None
        self.scroll_y = 0
        # Historial para undo (máximo 10 estados)
        self.history = []
        # Simulación búsqueda secuencial
        self.search = {
            "active": False, "target": None,
            "idx": 0,
            "timer": 0.0, "pause": 0.55, "result": None
        }

    def on_select(self):
        self.N_text = self.count_text = self.k_text = ""
        self.N = self.max_keys = None
        self.keys = []
        self.status = ""
        self.active_field = None
        self._rect_N = self._rect_COUNT = self._rect_K = None
        self._button_rects = []
        self.scrollbar = None
        self.scroll_y = 0
        self.history = []
        self.search.update({"active": False, "target": None, "idx": 0, "timer": 0.0, "result": None})

    # Animación de la búsqueda secuencial
    def update(self, dt: float):
        if not self.search["active"]:
            return
        self.search["timer"] += dt
        if self.search["timer"] < self.search["pause"]:
            return
        self.search["timer"] = 0.0

        l, r = self.search["left"], self.search["right"]
        k = self.search["target"]
        if l > r:
            self.search.update({"active": False, "idx": 0, "result": None})
            self.status = "No encontrada"
            return

        mid = (l + r) // 2
        self.search["mid"] = mid
        if self.keys[mid] == k:
            self.search.update({"active": False, "result": mid})
            self.status = f"Encontrada en índice {mid}"
        elif self.keys[mid] < k:
            self.search["left"] = mid + 1
        else:
            self.search["right"] = mid - 1

    # ---------------- Eventos ----------------
    def handle_event(self, event, viewport_rect, window_offset):
        # Manejar scroll primero
        if self.scrollbar and event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION, pygame.MOUSEWHEEL):
            if self.scrollbar.handle_event(event, window_offset):
                self.scroll_y = self.scrollbar.get_scroll()
                return
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            offx, offy = window_offset
            local_x = mx - offx
            local_y = my - offy

            self.active_field = None
            if self._rect_N and self._rect_N.collidepoint(local_x, local_y):
                self.active_field = "N"
            elif self._rect_COUNT and self._rect_COUNT.collidepoint(local_x, local_y):
                self.active_field = "COUNT"
            elif self._rect_K and self._rect_K.collidepoint(local_x, local_y):
                self.active_field = "K"

            for rect, action in self._button_rects:
                if rect.collidepoint(local_x, local_y):
                    self._on_button(action)
                    break

        elif event.type == pygame.KEYDOWN:
            if self.active_field is None:
                return
            if event.key == pygame.K_BACKSPACE:
                if self.active_field == "N":
                    self.N_text = self.N_text[:-1]
                elif self.active_field == "COUNT":
                    self.count_text = self.count_text[:-1]
                elif self.active_field == "K":
                    self.k_text = self.k_text[:-1]
                return
            if event.key == pygame.K_RETURN:
                self._commit_active_field()
                return
            if event.unicode.isdigit():
                if self.active_field == "N":
                    self.N_text += event.unicode
                elif self.active_field == "COUNT":
                    self.count_text += event.unicode
                elif self.active_field == "K":
                    self.k_text += event.unicode

    def _commit_active_field(self):
        if self.active_field == "N" and self.N_text.isdigit() and int(self.N_text) > 0:
            self.N = int(self.N_text)
            self.status = f"Tamaño del arreglo fijado en {self.N}"
        elif self.active_field == "COUNT" and self.count_text.isdigit() and int(self.count_text) > 0:
            self.max_keys = int(self.count_text)
            self.status = f"Tamaño de clave: {self.max_keys}"
        elif self.active_field == "K" and self.k_text.isdigit():
            self.status = f"Clave lista: {self.k_text}"

    def _save_snapshot(self):
        """Guarda un snapshot del estado actual para undo."""
        if len(self.history) >= 10:  # Límite de 10 undos
            self.history.pop(0)
        self.history.append({
            'keys': self.keys.copy(),
            'status': self.status
        })

    def _undo(self):
        """Deshace la última operación."""
        if not self.history:
            self.status = "No hay cambios para deshacer"
            return
        snapshot = self.history.pop()
        self.keys = snapshot['keys']
        self.status = "Cambio deshecho"
        self.search.update({"active": False, "idx": 0, "result": None})

    def guardar_estado(self, filepath=None):
        """Guarda el estado en un archivo binario."""
        data = {
            "N": self.N,
            "max_keys": self.max_keys,
            "keys": self.keys.copy(),
            "N_text": self.N_text,
            "count_text": self.count_text,
            "status": self.status
        }
        
        if filepath is None:
            default_name = f"sequential_search_{self.topic_id.replace('.', '_')}.bin"
            filepath = save_file_dialog(default_name, surface=pygame.display.get_surface())
            if filepath is None:
                self.status = "Guardado cancelado"
                return False
        
        try:
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
            self.status = f"Guardado en: {filepath}"
            return True
        except Exception as e:
            self.status = f"Error al guardar: {e}"
            return False

    def cargar_estado(self, filepath=None):
        """Carga el estado desde un archivo binario."""
        if filepath is None:
            filepath = open_file_dialog(surface=pygame.display.get_surface())
            if filepath is None:
                self.status = "Carga cancelada"
                return False
        
        try:
            with open(filepath, "rb") as f:
                data = pickle.load(f)
            # Asigna los datos cargados
            self.N = data.get("N", None)
            self.max_keys = data.get("max_keys", None)
            self.keys = data.get("keys", []).copy()
            self.N_text = data.get("N_text", "")
            self.count_text = data.get("count_text", "")
            self.status = "Estado cargado correctamente"
            self.history = []  # Limpiar historial al cargar
            return True
        except Exception as e:
            self.status = f"Error al cargar: {e}"
            return False

    # ---------------- Acciones de botones ----------------
    def _on_button(self, action):
        if action == "INSERTAR":
            if self.N is None:
                self.status = "Defina R (tamaño del arreglo)"; return
            if self.max_keys is None:
                self.status = "Defina Tamaño de clave"; return
            if not self.k_text.isdigit():
                self.status = "Ingrese clave numérica"; return

            # Validación de longitud exacta
            if len(self.k_text) > self.max_keys:
                self.status = f"La clave tiene MÁS de {self.max_keys} dígitos"; return
            if len(self.k_text) < self.max_keys:
                self.status = f"La clave tiene MENOS de {self.max_keys} dígitos"; return

            # Capacidad y duplicados
            if len(self.keys) >= self.N:
                self.status = "Arreglo lleno"; return

            k = int(self.k_text)
            self._save_snapshot()  # Guardar estado antes de modificar
            self.keys.append(k)  # añadir al final
            self.k_text = ""
            self.status = f"Insertada, total {len(self.keys)}/{self.N}"
            self.search.update({"active": False, "idx": 0, "result": None})  # cancelar animación

        elif action == "BUSCAR":
            if not self.keys:
                self.status = "Arreglo vacío"; return
            if not self.k_text.isdigit():
                self.status = "Ingrese clave numérica"; return
            if self.max_keys is not None:
                if len(self.k_text) > self.max_keys:
                    self.status = f"La clave tiene MÁS de {self.max_keys} dígitos"; return
                if len(self.k_text) < self.max_keys:
                    self.status = f"La clave tiene MENOS de {self.max_keys} dígitos"; return

            k = int(self.k_text)
            self.search.update({
                "active": True, "target": k,
                "left": 0, "right": len(self.keys) - 1,
                "mid": None, "timer": 0.0, "result": None
            })
            self.status = "Buscando (binaria)..."

        elif action == "ELIMINAR":
            if not self.k_text.isdigit():
                self.status = "Ingrese clave numérica"; return
            if self.max_keys is not None:
                if len(self.k_text) > self.max_keys:
                    self.status = f"La clave tiene MÁS de {self.max_keys} dígitos"; return
                if len(self.k_text) < self.max_keys:
                    self.status = f"La clave tiene MENOS de {self.max_keys} dígitos"; return

            k = int(self.k_text)
            try:
                i = self.keys.index(k)
                self._save_snapshot()  # Guardar estado antes de modificar
                self.keys.pop(i)
                self.status = "Eliminada"
            except ValueError:
                self.status = "No estaba en el arreglo"
            self.search.update({"active": False, "idx": 0, "result": None})

        elif action == "SAVE":
            self.guardar_estado()

        elif action == "LOAD":
            self.cargar_estado()

        elif action == "UNDO":
            self._undo()

        elif action == "CLEAN":
            self.N_text = ""
            self.count_text = ""   
            self.k_text = ""
            self.N = None
            self.max_keys = None    
            self.keys = []
            self.status = ""
            self.search.update({"active": False, "idx": 0, "result": None})

    # ---------------- Dibujo ----------------
    def render(self, surface: pygame.Surface, sim_rect: pygame.Rect):
        # Panel base
        pygame.draw.rect(surface, (255, 248, 227), sim_rect, border_radius=10)
        pygame.draw.rect(surface, K.DIVIDER, sim_rect, 1, border_radius=10)

        base_x = sim_rect.x + 24
        y = sim_rect.y + 18

        # Título
        title = K.FONT_B.render(self.title, True, K.ACCENT)
        surface.blit(title, (base_x, y))
        y += 36
        pygame.draw.line(surface, K.DIVIDER, (sim_rect.x + 12, y), (sim_rect.right - 12, y), 1)
        y += 12

        lbl_N = K.FONT.render("Tamaño del Arreglo (R):", True, K.SUBTEXT)
        lbl_C = K.FONT.render("Tamaño de clave:", True, K.SUBTEXT)
        lbl_K = K.FONT.render("Clave:", True, K.SUBTEXT)
        surface.blit(lbl_N, (base_x, y))
        surface.blit(lbl_C, (base_x + 360, y))
        y += 6

        self._rect_N = draw_input_box(surface, base_x, y + 18, 140, 36, self.N_text, K.FONT, K.TEXT, K.ACCENT, self.active_field == "N")
        self._rect_COUNT = draw_input_box(surface, base_x + 360, y + 18, 140, 36, self.count_text, K.FONT, K.TEXT, K.ACCENT, self.active_field == "COUNT")

        surface.blit(lbl_K, (base_x, y + 70))
        self._rect_K = draw_input_box(surface, base_x, y + 94, 140, 36, self.k_text, K.FONT, K.TEXT, K.ACCENT, self.active_field == "K")

        # Botonera
        buttons_y = y + 150
        pad = 10
        bx = base_x
        bw, bh = 120, 34
        labels = [
            ("Insertar", "INSERTAR"),
            ("Buscar", "BUSCAR"),
            ("Eliminar", "ELIMINAR"),
            ("Guardar", "SAVE"),
            ("Recuperar", "LOAD"),
            ("Retroceder", "UNDO"),
            ("Limpiar", "CLEAN"),
        ]
        self._button_rects = []
        for text, action in labels:
            rect = pygame.Rect(bx, buttons_y, bw, bh)
            pygame.draw.rect(surface, (245,245,245), rect, border_radius=6)
            pygame.draw.rect(surface, K.DIVIDER, rect, 1, border_radius=6)
            txt = K.FONT_S.render(text, True, K.TEXT)
            surface.blit(txt, (rect.x + (bw - txt.get_width())//2, rect.y + (bh - txt.get_height())//2))
            self._button_rects.append((rect, action))
            bx += bw + pad
            if bx + bw > sim_rect.right - 24:
                bx = base_x
                buttons_y += bh + pad

        if self.status:
            surface.blit(K.FONT.render(self.status, True, K.SUBTEXT), (base_x, buttons_y + bh + 10))

        # Grilla inferior (ordenada y resaltos de búsqueda) con scrollbar y centrado
        grid_top = buttons_y + bh + 48
        
        if self.N:
            # Calcular dimensiones totales de la grilla
            num_rows = (self.N + self.max_cols - 1) // self.max_cols
            grid_width = self.max_cols * self.box_size
            grid_height = num_rows * (self.box_size + self.spacing)
            
            # Área disponible para la grilla
            available_width = sim_rect.right - base_x - 40  # Dejar espacio para scrollbar
            available_height = sim_rect.bottom - grid_top - 20
            
            # Centrar horizontalmente
            grid_x = base_x + (available_width - grid_width) // 2
            if grid_x < base_x:
                grid_x = base_x
            
            # Configurar scrollbar si es necesario
            if grid_height > available_height:
                if self.scrollbar is None:
                    self.scrollbar = VerticalScrollbar(
                        sim_rect.right - 30, grid_top,
                        available_height, grid_height
                    )
                else:
                    self.scrollbar.rect.x = sim_rect.right - 30
                    self.scrollbar.rect.y = grid_top
                    self.scrollbar.view_height = available_height
                    self.scrollbar.update_content_height(grid_height)
                
                scroll_y = self.scrollbar.get_scroll()
                
                # Establecer región de clipping
                clip_rect = pygame.Rect(base_x, grid_top, available_width, available_height)
                surface.set_clip(clip_rect)
            else:
                self.scrollbar = None
                scroll_y = 0
            
            # Dibujar grilla
            for idx in range(self.N):
                fila = idx // self.max_cols
                col = idx % self.max_cols
                rx = grid_x + col * self.box_size
                ry = grid_top + fila * (self.box_size + self.spacing) - scroll_y
                
                # Solo dibujar si está visible
                if ry + self.box_size < grid_top or ry > grid_top + available_height:
                    continue
                
                rect = pygame.Rect(rx, ry, self.box_size, self.box_size)

                # Colores por defecto
                fill = None
                border = K.ACCENT

                # Resaltar el índice actual en búsqueda (ámbar)
                if self.search["active"] and self.search["idx"] == idx:
                    fill = (255, 223, 100)
                    border = (230, 180, 60)
                # Resultado encontrado (verde)
                if self.search["result"] is not None and self.search["result"] == idx:
                    fill = (100, 240, 160)
                    border = (0, 160, 90)

                if fill:
                    pygame.draw.rect(surface, fill, rect)
                pygame.draw.rect(surface, border, rect, 2)

                # Texto de la clave
                if idx < len(self.keys):
                    text_to_show = str(self.keys[idx]).zfill(self.max_keys or 1)
                    val_img = K.FONT.render(text_to_show, True, K.TEXT)
                    val_rect = val_img.get_rect(center=rect.center)
                    surface.blit(val_img, val_rect)
            
            # Quitar clipping
            surface.set_clip(None)
            
            # Dibujar scrollbar si existe
            if self.scrollbar:
                self.scrollbar.draw(surface)
