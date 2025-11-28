import pygame
import subprocess
import os
import constants as K

def _pygame_input_dialog(surface, prompt, default_text=""):
    """
    Muestra un diálogo de entrada simple usando Pygame.
    Bloquea el bucle principal hasta que se ingrese texto o se cancele.
    """
    if not surface:
        return None

    clock = pygame.time.Clock()
    input_text = default_text
    done = False
    result = None
    
    # Dimensiones del diálogo
    w, h = 400, 160
    x = (surface.get_width() - w) // 2
    y = (surface.get_height() - h) // 2
    rect = pygame.Rect(x, y, w, h)
    input_rect = pygame.Rect(x + 20, y + 70, w - 40, 32)
    
    # Guardar fondo
    background = surface.copy()
    
    while not done:
        # Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    result = input_text
                    done = True
                elif event.key == pygame.K_ESCAPE:
                    done = True
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode
        
        # Dibujar
        surface.blit(background, (0, 0))
        
        # Sombra
        s = pygame.Surface((w, h))
        s.set_alpha(128)
        s.fill((0, 0, 0))
        surface.blit(s, (x+5, y+5))
        
        # Caja principal
        pygame.draw.rect(surface, (250, 250, 250), rect, border_radius=10)
        pygame.draw.rect(surface, K.ACCENT, rect, 2, border_radius=10)
        
        # Título
        title_surf = K.FONT_B.render(prompt, True, K.TEXT)
        surface.blit(title_surf, (x + 20, y + 20))
        
        # Caja de texto
        pygame.draw.rect(surface, (255, 255, 255), input_rect, border_radius=4)
        pygame.draw.rect(surface, K.ACCENT, input_rect, 1, border_radius=4)
        
        # Texto
        txt_surf = K.FONT.render(input_text, True, K.TEXT)
        # Clip texto si es muy largo
        surface.set_clip(input_rect)
        surface.blit(txt_surf, (input_rect.x + 5, input_rect.y + 5))
        surface.set_clip(None)
        
        # Instrucciones
        hint = K.FONT_S.render("Enter: Aceptar  |  Esc: Cancelar", True, K.SUBTEXT)
        surface.blit(hint, (x + 20, y + 120))
        
        pygame.display.flip()
        clock.tick(30)
        
    # Restaurar
    surface.blit(background, (0, 0))
    pygame.display.flip()
    return result

def save_file_dialog(default_name="estado.bin", surface=None):
    """
    Muestra diálogo para guardar archivo.
    Intenta zenity -> kdialog -> pygame input.
    """
    # 1. Intentar Zenity
    try:
        os.makedirs("saves", exist_ok=True)
        result = subprocess.run([
            'zenity', '--file-selection', '--save', '--confirm-overwrite',
            '--filename=saves/' + default_name,
            '--file-filter=Archivos binarios (*.bin) | *.bin',
            '--title=Guardar Estado'
        ], capture_output=True, text=True, timeout=1) # Timeout rápido si no existe
        
        if result.returncode == 0:
            filepath = result.stdout.strip()
            if not filepath.endswith('.bin'): filepath += '.bin'
            return filepath
    except:
        pass

    # 2. Intentar KDialog
    try:
        result = subprocess.run([
            'kdialog', '--getsavefilename', 'saves/' + default_name,
            '*.bin |Archivos binarios'
        ], capture_output=True, text=True, timeout=1)
        
        if result.returncode == 0:
            filepath = result.stdout.strip()
            return filepath
    except:
        pass
        
    # 3. Fallback a Pygame
    if surface:
        name = _pygame_input_dialog(surface, "Guardar como:", default_name)
        if name:
            if not name.endswith('.bin'): name += '.bin'
            return os.path.join("saves", os.path.basename(name))
            
    # 4. Fallback final automático
    print("Warning: Usando guardado automático por defecto")
    return f"saves/{default_name}"


def open_file_dialog(surface=None):
    """
    Muestra diálogo para abrir archivo.
    Intenta zenity -> kdialog -> pygame input.
    """
    # 1. Intentar Zenity
    try:
        result = subprocess.run([
            'zenity', '--file-selection',
            '--filename=saves/',
            '--file-filter=Archivos binarios (*.bin) | *.bin',
            '--title=Cargar Estado'
        ], capture_output=True, text=True, timeout=1)
        
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    # 2. Intentar KDialog
    try:
        result = subprocess.run([
            'kdialog', '--getopenfilename', 'saves/',
            '*.bin |Archivos binarios'
        ], capture_output=True, text=True, timeout=1)
        
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
        
    # 3. Fallback a Pygame
    if surface:
        name = _pygame_input_dialog(surface, "Nombre del archivo a cargar:", "")
        if name:
            if not name.endswith('.bin'): name += '.bin'
            path = os.path.join("saves", os.path.basename(name))
            if os.path.exists(path):
                return path
            
    return None
