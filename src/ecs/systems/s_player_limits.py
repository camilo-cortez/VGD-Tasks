import pygame
import esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_velocity import CVelocity

def system_player_limits(world:esper.World, screen:pygame.Surface, player_entity:int):
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    pl_rect = CSurface.get_area_relative(pl_s.area, pl_t.pos)
    screen_rect = screen.get_frect()   

    if not screen_rect.contains(pl_rect):
        pl_rect.clamp_ip(screen_rect)
        pl_t.pos.xy = pl_rect.topleft