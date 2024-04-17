import pygame
import esper
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_velocity import CVelocity

def system_player_limits(world:esper.World, screen:pygame.Surface, player_entity:int):
    pl_t = world.component_for_entity(player_entity, CTransform)
    pl_s = world.component_for_entity(player_entity, CSurface)
    pl_v = world.component_for_entity(player_entity, CVelocity)
    pl_rect = pl_s.surf.get_rect(topleft = pl_t.pos)
    screen_rect = screen.get_frect()   

    if pl_rect.left < 0 or pl_rect.right > screen_rect.width:
        pl_rect.clamp_ip(screen_rect)
        pl_t.pos.x = pl_rect.left

    if pl_rect.top < 0 or pl_rect.bottom > screen_rect.height:
        pl_rect.clamp_ip(screen_rect)
        pl_t.pos.y = pl_rect.top
