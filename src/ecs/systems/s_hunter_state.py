import pygame
import esper
from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_hunter_state import CHunterState, HunterState
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.engine.service_locator import ServiceLocator


def system_hunter_state(world:esper.World, player_entity:int, hunter_cfg:dict):
    pl_t = world.component_for_entity(player_entity, CTransform)
    components = world.get_components(CVelocity, CAnimation, CTransform, CHunterState)
    for _, (c_v, c_a, c_t, c_hst) in components:
        if c_hst.state == HunterState.IDLE:
            _do_idle_state(c_v, c_a, c_t, c_hst, pl_t, hunter_cfg)
        elif c_hst.state == HunterState.CHASE:
            _do_chase_state(c_v, c_a, c_t, c_hst, pl_t, hunter_cfg)
        elif c_hst.state == HunterState.RETURN:
            _do_return_state(c_v, c_a, c_t, c_hst, pl_t, hunter_cfg)

def _do_idle_state(c_v:CVelocity, c_a:CAnimation, c_t: CTransform, c_hst:CHunterState, pl_t:CTransform, hunter_cfg:dict):
    _set_animation(c_a, 1)
    c_v.vel = pygame.Vector2(0,0)

    if (c_t.pos - pl_t.pos).magnitude_squared() < hunter_cfg["distance_start_chase"] ** 2:
        ServiceLocator.sounds_service.play(hunter_cfg["sound_chase"])
        c_hst.state = HunterState.CHASE

def _do_chase_state(c_v:CVelocity, c_a:CAnimation, c_t: CTransform, c_hst:CHunterState, pl_t:CTransform, hunter_cfg:dict):
    _set_animation(c_a, 0)
    c_v.vel = (pl_t.pos - c_t.pos).normalize() * hunter_cfg["velocity_chase"]
    if (c_hst.init_pos - c_t.pos).magnitude_squared() >= hunter_cfg["distance_start_return"] ** 2:
        c_hst.state = HunterState.RETURN

def _do_return_state(c_v:CVelocity, c_a:CAnimation, c_t: CTransform, c_hst:CHunterState, pl_t:CTransform, hunter_cfg:dict):
    _set_animation(c_a, 0)
    c_v.vel = (c_hst.init_pos - c_t.pos).normalize() * hunter_cfg["velocity_return"]
    if (c_hst.init_pos - c_t.pos).magnitude_squared() <= 1:
        c_hst.state = HunterState.IDLE

def _set_animation(c_a:CAnimation, num_anim:int):
    if c_a.current_animation == num_anim:
        return
    c_a.current_animation = num_anim
    c_a.current_animation_time = 0
    c_a.current_frame = c_a.animations_list[c_a.current_animation].start