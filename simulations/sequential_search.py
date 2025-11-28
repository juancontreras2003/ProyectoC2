"""
Simulación de Búsqueda Secuencial.
Implementa búsqueda secuencial con animación paso a paso.
"""
import pygame
import bisect
# import tkinter as tk  # Comentado temporalmente
# from tkinter import filedialog  # Comentado temporalmente
import pickle

import constants as K
from widgets import draw_input_box, VerticalScrollbar
from simulations.base import Simulation


class SequentialSearchSim(Simulation):
    """Simulación de búsqueda secuencial con animación."""
    
    def __init__(self):
        super().__init__("1.1.A", "Búsqueda Secuencial")
        # Estado de inputs
        self.N_text = ""
        self.count_text = ""    # "Tamaño de clave"
        self.k_text = ""
        self.N = None
        self.max_keys = None    # longitud exacta exigida
        # Datos (orden = inserción)
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

        # Simulación secuencial
        self.search = {
            "active": False, "target": None,
            "idx": 0, "result": None,
            "timer": 0.0, "pause": 0.55
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
        self.search.update({"active": False, "target": None, "idx": 0, "result": None, "timer": 0.0})

    # Avance de animación secuencial
    def update(self, dt: float):
        if not self.search["active"]:
            return
        self.search["timer"] += dt
        if self.search["timer"] < self.search["pause"]:
            return
        self.search["timer"] = 0.0

        i = self.search["idx"]
        k = self.search["target"]
        if i >= len(self.keys):
            self.search.update({"active": False, "result": None})
            self.status = "No encontrada"
            return

        if self.keys[i] == k:
            self.search.update({"active": False, "result": i})
            self.status = f"Encontrada en índice {i}"
        else:
            self.search["idx"] = i + 1

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
            self.max_keys = int(self.count_text)  # longitud exigida
            self.status = f"Tamaño de clave: {self.max_keys}"
        elif self.active_field == "K" and self.k_text.isdigit():
            self.status = f"Clave lista: {self.k_text}"

    def guardar_estado(self, filepath=None):
        """Guarda el estado en un archivo binario."""
        import os
        data = {
            "N": self.N,
            "max_keys": self.max_keys if hasattr(self, 'max_keys') else self.key_len if hasattr(self, 'key_len') else None,
            "keys": self.keys.copy() if hasattr(self, 'keys') else self.table.copy(),
            "N_text": self.N_text,
            "count_text": self.count_text if hasattr(self, 'count_text') else self.keylen_text if hasattr(self, 'keylen_text') else "",
            "status": self.status
        }
        if hasattr(self, 'collision_mode'):
            data['collision_mode'] = self.collision_mode
        
        if filepath is None:
            # Determinar nombre basado en topic_id
            filename = self.topic_id.replace('.', '_') + '.bin'
            filepath = f'saves/{filename}'
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'wb') as f:
                import pickle
                pickle.dump(data, f)
            self.status = 'Estado guardado correctamente. Reiniciado.'
            self.on_select()
            return True
        except Exception as e:
            self.status = f'Error al guardar: {e}'
            return False
        try:
            with open(filepath, "wb") as f:
                pickle.dump(data, f)
            self.status = "Arreglo guardado correctamente y reiniciado."
            self.on_select()  # Reinicia simulador al guardar
            return True
        except Exception as e:
            self.status = f"Error al guardar: {e}"
            return False

    def cargar_estado(self, filepath=None):
        """Carga el estado desde un archivo binario."""
        import os
        if filepath is None:
            filename = self.topic_id.replace('.', '_') + '.bin'
            filepath = f'saves/{filename}'
        
        if not os.path.exists(filepath):
            self.status = 'No hay archivo guardado'
            return False
        
        try:
            with open(filepath, 'rb') as f:
                import pickle
                data = pickle.load(f)
            
            self.N = data.get('N', None)
            if hasattr(self, 'max_keys'):
                self.max_keys = data.get('max_keys', None)
            if hasattr(self, 'key_len'):
                self.key_len = data.get('max_keys', None)
            if hasattr(self, 'keys'):
                self.keys = data.get('keys', []).copy()
            if hasattr(self, 'table'):
                self.table = data.get('keys', []).copy()
            self.N_text = data.get('N_text', '')
            if hasattr(self, 'count_text'):
                self.count_text = data.get('count_text', '')
            if hasattr(self, 'keylen_text'):
                self.keylen_text = data.get('count_text', '')
            if hasattr(self, 'collision_mode'):
                self.collision_mode = data.get('collision_mode', 'LINEAR')
            self.status = 'Estado cargado correctamente'
            return True
        except Exception as e:
            self.status = f'Error al cargar: {e}'
            return False
        try:
            with open(filepath, "rb") as f:
                data = pickle.load(f)
            # Asignación segura
            self.N = data.get("N", None)
            self.max_keys = data.get("max_keys", None)
            self.keys = data.get("keys", []).copy()
            self.N_text = data.get("N_text", "")
            self.count_text = data.get("count_text", "")
            self.status = "Arreglo cargado correctamente"
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

            if len(self.keys) >= self.N:
                self.status = "Arreglo lleno"; return

            k = int(self.k_text)
            # Rechazar duplicados
            if k in self.keys:
                self.status = "La clave ya existe en el arreglo"; return

            bisect.insort(self.keys, k)  # inserta manteniendo orden
            self.k_text = ""
            self.status = f"Insertada, total {len(self.keys)}/{self.N}"
            # cancelar animación en curso si se modifica el arreglo
            self.search.update({"active": False, "idx": 0, "result": None})

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
            # Preparar animación secuencial
            self.search.update({"active": True, "target": k, "idx": 0, "result": None, "timer": 0.0})
            self.status = "Buscando (secuencial)..."

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
                self.keys.pop(i)
                self.status = "Eliminada"
            except ValueError:
                self.status = "No estaba en el arreglo"
            self.search.update({"active": False, "idx": 0, "result": None})

        elif action == "SAVE":
            self.guardar_estado()
        elif action == "LOAD":
            self.cargar_estado()
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

        # Etiquetas e inputs
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
            ("Guardar ", "SAVE"),
            ("Recuperar ", "LOAD"),
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

        # Grilla inferior: resalta idx actual en ámbar y encontrado en verde con scrollbar y centrado
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

                # Determina colores para fondo (fill) y borde
                fill = None
                border = K.ACCENT

                if self.search["active"] and self.search["idx"] == idx:
                    fill = (255, 223, 100)  # color ámbar claro
                    border = (230, 180, 60)
                if self.search["result"] is not None and self.search["result"] == idx:
                    fill = (100, 240, 160)  # color verde claro
                    border = (0, 160, 90)

                # Dibuja fondo relleno si aplica
                if fill:
                    pygame.draw.rect(surface, fill, rect)

                # Dibuja borde
                pygame.draw.rect(surface, border, rect, 2)

                # Dibuja texto de la clave centrada
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
