import pygame
import os
from constants import WIDTH, HEIGHT

# Ruta base relativa
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

# Carga de imágenes
background_path = os.path.join(ASSETS_DIR, "background.jpg")
logo_path = os.path.join(ASSETS_DIR, "logo.png")

background_img = pygame.image.load(background_path)
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

logo_img = pygame.image.load(logo_path)
logo_img = pygame.transform.scale(logo_img, (300, 300))

initial_title = "Ciencias de la Computación II"
initial_desc = ""

def rescale_background(w, h):
    global background_img
    bg = pygame.image.load(background_path)
    background_img = pygame.transform.scale(bg, (w, h))
