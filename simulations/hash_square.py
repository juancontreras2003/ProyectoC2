"""
Simulación de Función Hash Cuadrado (Mid-Square).
Implementa hash cuadrado medio con resolución de colisiones.
"""
import pygame
# import tkinter as tk  # Comentado temporalmente
# from tkinter import filedialog  # Comentado temporalmente
import pickle

import constants as K
from widgets import draw_input_box, VerticalScrollbar
from simulations.base import Simulation

class HashSquareSim(Simulation):
    """Simulación de función hash cuadrado medio"""
    
    def __init__(self):
        super().__init__("1.1.D.2", "Función Hash Cuadrado")
        self.N_text = ""
        self.keylen_text = ""
        self.k_text = ""
        self.N = None
        self.key_len = None
        self.table = []
        self.TOMBSTONE = object()

        self.status = ""
        self.active_field = None
        self._rect_N = self._rect_KEYLEN = self._rect_K = None
        self._button_rects = []

        self.collision_modes = [
            ("Prueba lineal", "LINEAR"),
            ("Prueba cuadrática", "QUADRATIC"),
            ("Doble función Hash", "DOUBLE")
        ]
        self.collision_mode = "LINEAR"
        self.dropdown_open = False
        self._rect_dd_main = None
        self._rect_dd_items = []

        self.search = {
            "result": None, "index": None
        }

        self.scrollbar = None
        self.scroll_y = 0

    def on_select(self):
        self.N_text = self.keylen_text = self.k_text = ""
        self.N = self.key_len = None
        self.table = []
        self.status = ""
        self.active_field = None
        self._rect_N = self._rect_KEYLEN = self._rect_K = None
        self._button_rects = []
        self.dropdown_open = False
        self._rect_dd_main = None
        self._rect_dd_items = []
        self.collision_mode = "LINEAR"
        self.search = {"result": None, "index": None}
        self.scrollbar = None

    def h1(self, k: int) -> int:
        """Hash base cuadrado medio"""
        # r = número de dígitos que caben en N-1 (base 10)
        r = max(1, len(str(self.N - 1))) if self.N else 1
        sq = str(k * k)
        
        # Asegurar que haya al menos 2*r dígitos para extraer el centro
        sq = sq.zfill(max(2 * r, len(sq)))
        
        # Extraer r dígitos del centro
        start = (len(sq) - r) // 2
        mid_digits = int(sq[start:start + r])
        return mid_digits % self.N

    def h2(self, k: int) -> int:
        return 1 + (k % (self.N - 1 if self.N and self.N > 1 else 1))

    def probe_index(self, base: int, k: int, i: int) -> int:
        if self.collision_mode == "LINEAR":
            return (base + i) % self.N
        elif self.collision_mode == "QUADRATIC":
            return (base + i * i) % self.N
        else:  # DOUBLE
            return (base + i * self.h2(k)) % self.N

    def _collision_label(self) -> str:
        return {
            "LINEAR": "Prueba lineal",
            "QUADRATIC": "Prueba cuadrática",
            "DOUBLE": "Doble función Hash",
        }[self.collision_mode]

    def handle_event(self, event, viewport_rect, window_offset):
        # Primero, manejar eventos del scrollbar
        if self.scrollbar and self.scrollbar.handle_event(event):
            return

        # Scroll con botones 4/5
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            if self.scrollbar:
                delta = -1 if event.button == 4 else 1
                fake = pygame.event.Event(pygame.MOUSEWHEEL, {"y": delta})
                self.scrollbar.handle_event(fake, window_offset)
                return

        # Scroll con flechas
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_UP, pygame.K_DOWN):
            if self.scrollbar:
                delta = 1 if event.key == pygame.K_UP else -1
                fake = pygame.event.Event(pygame.MOUSEWHEEL, {"y": delta})
                self.scrollbar.handle_event(fake, window_offset)
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            offx, offy = window_offset
            local_x = mx - offx
            local_y = my - offy

            if self._rect_dd_main and self._rect_dd_main.collidepoint(local_x, local_y):
                self.dropdown_open = not self.dropdown_open
                return
            if self.dropdown_open:
                for rect, value in self._rect_dd_items:
                    if rect.collidepoint(local_x, local_y):
                        self.collision_mode = value
                        self.dropdown_open = False
                        return
                self.dropdown_open = False

            self.active_field = None
            if self._rect_N and self._rect_N.collidepoint(local_x, local_y):
                self.active_field = "N"
            elif self._rect_KEYLEN and self._rect_KEYLEN.collidepoint(local_x, local_y):
                self.active_field = "KEYLEN"
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
                elif self.active_field == "KEYLEN":
                    self.keylen_text = self.keylen_text[:-1]
                elif self.active_field == "K":
                    self.k_text = self.k_text[:-1]
                return
            if event.key == pygame.K_RETURN:
                self._commit_active_field()
                return
            if event.unicode.isdigit():
                if self.active_field == "N":
                    self.N_text += event.unicode
                elif self.active_field == "KEYLEN":
                    self.keylen_text += event.unicode
                elif self.active_field == "K":
                    self.k_text += event.unicode

    def _commit_active_field(self):
        if self.active_field == "N" and self.N_text.isdigit() and int(self.N_text) > 0:
            self.N = int(self.N_text)
            self.table = [None] * self.N
            self.status = f"Tamaño del arreglo fijado en {self.N}"
            self.search = {"result": None, "index": None}
            self.scrollbar = None
        elif self.active_field == "KEYLEN" and self.keylen_text.isdigit() and int(self.keylen_text) > 0:
            self.key_len = int(self.keylen_text)
            self.status = f"Tamaño de clave: {self.key_len}"
        elif self.active_field == "K" and self.k_text.isdigit():
            self.status = f"Clave lista: {self.k_text}"

    def _validate_key_text(self):
        if not self.k_text.isdigit():
            return False, "Ingrese clave numérica"
        if self.key_len is None:
            return False, "Defina Tamaño de clave"
        if len(self.k_text) > self.key_len:
            return False, f"La clave tiene MÁS de {self.key_len} dígitos"
        if len(self.k_text) < self.key_len:
            return False, f"La clave tiene MENOS de {self.key_len} dígitos"
        return True, None

    def _find_key(self, k):
        if self.N is None:
            return None
        base = self.h1(k)
        for i in range(self.N):
            idx = self.probe_index(base, k, i)
            slot = self.table[idx]
            if slot is None:
                return None
            if slot is not self.TOMBSTONE and slot == k:
                return idx
        return None

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
            self.status = "Tabla hash cuadrado guardada y simulador reiniciado."
            self.on_select()
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
            self.N = data.get("N", None)
            self.key_len = data.get("key_len", None)
            self.N_text = data.get("N_text", "")
            self.keylen_text = data.get("keylen_text", "")
            self.k_text = data.get("k_text", "")
            self.table = data.get("table", []).copy()
            self.collision_mode = data.get("collision_mode", "LINEAR")
            self.status = "Tabla hash cuadrado cargada correctamente"
            return True
        except Exception as e:
            self.status = f"Error al cargar: {e}"
            return False

    def _on_button(self, action):
        if action == "INSERTAR":
            if self.N is None:
                self.status = "Defina R (tamaño del arreglo)"
                return
            ok, msg = self._validate_key_text()
            if not ok:
                self.status = msg
                return
            k = int(self.k_text)
            if self._find_key(k) is not None:
                self.status = "La clave ya existe en el arreglo"
                return
            base = self.h1(k)
            insert_idx = None
            first_blocked = None
            total_probes = 0
            for i in range(self.N):
                idx = self.probe_index(base, k, i)
                slot = self.table[idx]
                if i == 0 and slot is not None and slot is not self.TOMBSTONE:
                    first_blocked = idx
                if slot is None or slot is self.TOMBSTONE:
                    insert_idx = idx
                    total_probes = i
                    break
            if insert_idx is None:
                self.status = "Arreglo lleno"
                return
            self.table[insert_idx] = k
            self.k_text = ""
            if total_probes > 0:
                if first_blocked is None:
                    first_blocked = base
                self.status = f"Colisión en {first_blocked+1}; reubicado en {insert_idx+1} con {self._collision_label()}"
            else:
                self.status = f"Insertada en índice {insert_idx+1}"
            self.search = {"result": None, "index": insert_idx}

        elif action == "BUSCAR":
            if self.N is None or not any(x is not None and x is not self.TOMBSTONE for x in self.table):
                self.status = "Arreglo vacío"
                return
            ok, msg = self._validate_key_text()
            if not ok:
                self.status = msg
                return
            k = int(self.k_text)
            idx = self._find_key(k)
            self.search = {"result": idx, "index": idx}
            self.status = f"No encontrada" if idx is None else f"Encontrada en índice {idx+1}"

        elif action == "ELIMINAR":
            if self.N is None:
                self.status = "Defina R (tamaño del arreglo)"
                return
            ok, msg = self._validate_key_text()
            if not ok:
                self.status = msg
                return
            k = int(self.k_text)
            idx = self._find_key(k)
            if idx is None:
                self.status = "No estaba en el arreglo"
            else:
                self.table[idx] = self.TOMBSTONE
                self.status = "Eliminada"
            self.search = {"result": None, "index": idx}

        elif action == "SAVE":
            self.guardar_estado()
        elif action == "LOAD":
            self.cargar_estado()
        elif action == "CLEAN":
            self.on_select()

    def render(self, surface: pygame.Surface, sim_rect: pygame.Rect):
        pygame.draw.rect(surface, (255, 248, 227), sim_rect, border_radius=10)
        pygame.draw.rect(surface, K.DIVIDER, sim_rect, 1, border_radius=10)

        hash_left = sim_rect.x + 60
        hash_width = 110
        controls_x = hash_left + hash_width + 50

        y = sim_rect.y + 18
        surface.blit(K.FONT_B.render(self.title, True, K.ACCENT), (controls_x, y))
        y += 36
        pygame.draw.line(surface, K.DIVIDER, (sim_rect.x+12, y), (sim_rect.right-12, y), 1)
        y += 12

        # Inputs y labels
        lbl_N = K.FONT.render("Tamaño del Arreglo (R):", True, K.SUBTEXT)
        lbl_C = K.FONT.render("Tamaño de clave:", True, K.SUBTEXT)
        lbl_K = K.FONT.render("Clave:", True, K.SUBTEXT)
        lbl_mode = K.FONT.render("Solución de colisiones:", True, K.SUBTEXT)

        surface.blit(lbl_N, (controls_x, y))
        surface.blit(lbl_C, (controls_x + 260, y))
        y += 6

        self._rect_N = draw_input_box(surface, controls_x, y+18, 140, 36,
                                      self.N_text, K.FONT, K.TEXT, K.ACCENT,
                                      self.active_field == "N")
        self._rect_KEYLEN = draw_input_box(surface, controls_x+260, y+18, 140, 36,
                                           self.keylen_text, K.FONT, K.TEXT, K.ACCENT,
                                           self.active_field == "KEYLEN")

        surface.blit(lbl_K, (controls_x, y+70))
        self._rect_K = draw_input_box(surface, controls_x, y+94, 140, 36,
                                      self.k_text, K.FONT, K.TEXT, K.ACCENT,
                                      self.active_field == "K")

        # Dropdown colisiones
        dd_x = controls_x + 260
        surface.blit(lbl_mode, (dd_x, y+70))
        dd_main = pygame.Rect(dd_x, y+94, 220, 36)
        pygame.draw.rect(surface, (245,245,245), dd_main, border_radius=6)
        pygame.draw.rect(surface, K.DIVIDER, dd_main, 1, border_radius=6)
        sel_label = next(t for t,v in self.collision_modes if v == self.collision_mode)
        surface.blit(K.FONT_S.render(sel_label, True, K.TEXT), (dd_main.x+8, dd_main.y+8))
        pygame.draw.polygon(surface, K.TEXT, [
            (dd_main.right-16, dd_main.y+14),
            (dd_main.right-6,  dd_main.y+14),
            (dd_main.right-11, dd_main.y+22)
        ])
        self._rect_dd_main = dd_main

        # Botonera
        buttons_y = y + 150
        pad = 10
        bx = controls_x
        bw, bh = 120, 34
        labels = [
            ("Insertar", "INSERTAR"), ("Buscar", "BUSCAR"),
            ("Eliminar", "ELIMINAR"), ("Guardar", "SAVE"),
            ("Recuperar", "LOAD"), ("Limpiar", "CLEAN")
        ]

        self._button_rects = []
        for text, action in labels:
            rect = pygame.Rect(bx, buttons_y, bw, bh)
            pygame.draw.rect(surface, (245,245,245), rect, border_radius=6)
            pygame.draw.rect(surface, K.DIVIDER, rect, 1, border_radius=6)
            txt = K.FONT_S.render(text, True, K.TEXT)
            surface.blit(txt, (rect.x + (bw - txt.get_width())//2,
                              rect.y + (bh - txt.get_height())//2))
            self._button_rects.append((rect, action))
            bx += bw + pad
            if bx + bw > sim_rect.right - 24:
                bx = controls_x
                buttons_y += bh + pad

        if self.status:
            surface.blit(K.FONT.render(self.status, True, K.SUBTEXT),
                        (controls_x, buttons_y + bh + 10))

        # Contenedor de hash con scrollbar
        N = self.N if self.N is not None else len(self.table)
        if N > 0:
            top_y = sim_rect.y + 120
            max_h = 600
            max_slots = 20
            visible_slots = min(N, max_slots)
            slot_h = max_h / visible_slots
            total_height = slot_h * N

            pygame.draw.rect(surface, K.ACCENT,
                           (hash_left, top_y, hash_width, max_h),
                           2, border_radius=6)

            if self.scrollbar is None:
                self.scrollbar = VerticalScrollbar(
                    hash_left+hash_width+6, top_y, max_h, total_height)
            else:
                self.scrollbar.rect.y = top_y
                self.scrollbar.view_height = max_h
                self.scrollbar.update_content_height(total_height)
            
            scroll_y = self.scrollbar.get_scroll()

            clip = pygame.Rect(hash_left, top_y, hash_width, max_h)
            surface.set_clip(clip)

            # Líneas y slots
            for i in range(N+1):
                y_line = top_y + i*slot_h - scroll_y
                pygame.draw.line(surface, K.ACCENT,
                               (hash_left, y_line),
                               (hash_left+hash_width, y_line), 1)
            
            for idx in range(N):
                y0 = top_y + idx*slot_h - scroll_y
                if y0+slot_h < top_y or y0 > top_y+max_h:
                    continue
                r = pygame.Rect(hash_left, y0, hash_width, slot_h)
                val = self.table[idx] if idx < len(self.table) else None
                if val is self.TOMBSTONE:
                    dash = K.FONT_S.render("-", True, (160,160,160))
                    surface.blit(dash, dash.get_rect(center=r.center))
                elif val is not None:
                    fill,border = None,K.ACCENT
                    if self.search["result"]==idx:
                        fill,border=(100,240,160),(0,160,90)
                    if fill:
                        pygame.draw.rect(surface, fill, r)
                    pygame.draw.rect(surface, border, r, 2)
                    txt = K.FONT.render(str(val).zfill(self.key_len or 1), True, K.TEXT)
                    surface.blit(txt, txt.get_rect(center=r.center))

            surface.set_clip(None)

            # Índices
            occupied = {i for i,v in enumerate(self.table)
                       if v not in (None, self.TOMBSTONE)}
            visibles = occupied | {0, N-1} | set(range(0, N, 10))
            for idx in sorted(visibles):
                y0 = top_y + idx*slot_h - scroll_y
                mid = y0 + slot_h/2
                if top_y <= mid <= top_y+max_h:
                    lbl = K.FONT_S.render(str(idx+1), True, K.TEXT)
                    surface.blit(lbl, lbl.get_rect(midright=(hash_left-8, mid)))

            self.scrollbar.draw(surface)

        # Dropdown items
        self._rect_dd_items = []
        if self.dropdown_open:
            opt_y = dd_main.bottom + 2
            for t,v in self.collision_modes:
                r = pygame.Rect(dd_x, opt_y, 220, 28)
                pygame.draw.rect(surface, (255,255,255), r)
                pygame.draw.rect(surface, K.DIVIDER, r, 1)
                surface.blit(K.FONT_S.render(t, True, K.TEXT), (r.x+8, r.y+6))
                self._rect_dd_items.append((r, v))
                opt_y += 28


# ----- 1.1.D.3 Función Hash Truncamiento -----------------------------


