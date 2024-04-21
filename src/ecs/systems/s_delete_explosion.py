import esper

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.tags.c_tag_explosion import CTagExplosion

def system_delete_explosions(world:esper.World):
    components = world.get_components(CAnimation, CTagExplosion)
    for entity, (c_a, c_te) in components:
        if c_a.current_frame == c_a.animations_list[c_a.current_animation].end:
            world.delete_entity(entity)