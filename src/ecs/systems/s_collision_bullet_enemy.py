import esper
from src.create.prefab_creator import create_explosion
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_bullet import CTagBullet

def system_collision_bullet_enemy(world:esper.World, explosion_cfg:dict):
    enemy_components = world.get_components(CSurface, CTransform, CTagEnemy)
    bullet_components = world.get_components(CSurface, CTransform, CTagBullet)
    c_s: CSurface
    c_se: CSurface
    c_t: CTransform
    c_te: CTransform

    for bullet_entity, (c_s, c_t, _) in bullet_components:
        bullet_rect = CSurface.get_area_relative(c_s.area, c_t.pos)
        for enemy_entity, (c_se, c_te, _) in enemy_components:
            enemy_rect = CSurface.get_area_relative(c_se.area, c_te.pos)
            if bullet_rect.colliderect(enemy_rect):
                world.delete_entity(bullet_entity)
                world.delete_entity(enemy_entity)
                create_explosion(world, c_te.pos, explosion_cfg)

