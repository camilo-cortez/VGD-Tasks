import esper
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_bullet import CTagBullet

def system_collision_bullet_enemy(world:esper.World):
    enemy_components = world.get_components(CSurface, CTransform, CTagEnemy)
    bullet_components = world.get_components(CSurface, CTransform, CTagBullet)
    c_s: CSurface
    c_se: CSurface
    c_t: CTransform
    c_te: CTransform

    for bullet_entity, (c_s, c_t, _) in bullet_components:
        bullet_rect = c_s.surf.get_rect(topleft = c_t.pos)
        for enemy_entity, (c_se, c_te, _) in enemy_components:
            enemy_rect = c_se.surf.get_rect(topleft = c_te.pos)
            if bullet_rect.colliderect(enemy_rect):
                world.delete_entity(bullet_entity)
                world.delete_entity(enemy_entity)
