import pygame


class FontsService:
    def __init__(self) -> None:
        self._fonts = {}

    def get(self, path:str, size:int) -> pygame.font.Font:
        path_s = path + str(size)
        if path_s not in self._fonts:
            self._fonts[path_s] = pygame.font.Font(path, size)
        return self._fonts[path_s]