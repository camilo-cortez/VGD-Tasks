import pygame
import esper
from src.create.prefab_creator import create_enemy_square
from src.ecs.components.c_powerup_timer import CPowerupTimer
from src.ecs.components.c_surface import CSurface
from src.engine.service_locator import ServiceLocator

def system_powerup_timer(world:esper.World, delta_time:float, pui_entity:int):
    components = world.get_component(CPowerupTimer)
    pui = world.component_for_entity(pui_entity, CSurface)
    text_size = 15
    c_p:CPowerupTimer
    color = pygame.Color(0,255,0)
    for _, c_p in components:
        if c_p.current_time < c_p.max_time:
            c_p.current_time += delta_time
            color = pygame.Color(255,0,0)
        pui.surf = CSurface.from_text(str(int(100 * c_p.current_time/c_p.max_time)) + '%', 
                            color, 
                            ServiceLocator.fonts_service.get("assets/fnt/PressStart2P.ttf", text_size), 
                            text_size).surf
        
