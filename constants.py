import pygame

# Dimensiones
MIN_W, MIN_H = 900, 540
WIDTH, HEIGHT = 1100, 700
SIDEBAR_W = 320
HEADER_H = 60
ROW_H = 30
INDENT = 16

# Colores
BG = (237, 224, 185)
WHITE = (255, 255, 255)
TEXT = (30, 33, 36)
SUBTEXT = (60, 64, 110)
ACCENT = (140, 140, 140)
DIVIDER = (210, 214, 220)
HILITE = (235, 240, 246)

SCROLLBAR_W = 10
SCROLLBAR_MARGIN = 6
SCROLLBAR_MIN_THUMB = 40
SCROLLBAR_TRACK = (230, 233, 239)
SCROLLBAR_THUMB = (180, 186, 197)

AMBAR = (255, 223, 116)
VERDE = (150, 250, 195)

# Fuentes
pygame.init()
FONT_S = pygame.font.SysFont("Segoe UI", 16)
FONT = pygame.font.SysFont("Segoe UI", 17, bold=True)
FONT_B = pygame.font.SysFont("Segoe UI", 18, bold=True)
FONT_T = pygame.font.SysFont("Segoe UI", 28, bold=True)
