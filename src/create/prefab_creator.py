import esper
import pygame
import random

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_hunter_state import CHunterState
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_powerup_timer import CPowerupTimer
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_enemy_spawner import CEnemySpawner, SpawnEventData
from src.ecs.components.tags.c_tag_bouncer import CTagBouncer
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_explosion import CTagExplosion
from src.ecs.components.tags.c_tag_hunter import CTagHunter
from src.ecs.components.tags.c_tag_player import CTagPlayer
from src.engine.service_locator import ServiceLocator

def crear_cuadrado(ecs_world:esper.World,
                   size:pygame.Vector2,
                   pos:pygame.Vector2,
                   vel:pygame.Vector2,
                   color:pygame.Color) -> int:
    cuad_entity = ecs_world.create_entity()
    ecs_world.add_component(cuad_entity,
                    CSurface(size, color))
    ecs_world.add_component(cuad_entity,
                    CTransform(pos))
    ecs_world.add_component(cuad_entity,
                    CVelocity(vel))
    return cuad_entity

def create_sprite(world:esper.World, pos:pygame.Vector2, vel:pygame.Vector2, surface:pygame.Surface) -> int:
    sprite_entity = world.create_entity()
    world.add_component(sprite_entity, CTransform(pos))
    world.add_component(sprite_entity, CVelocity(vel))
    world.add_component(sprite_entity, CSurface.from_surface(surface))
    return sprite_entity

def create_enemy_square(world:esper.World, pos:pygame.Vector2, enemy_info:dict, enemy_type:str):
    enemy_surface = ServiceLocator.images_service.get(enemy_info["image"])
    if enemy_type == 'Hunter':
        create_hunter(world, pos, enemy_info)
    else:
        vel_max = enemy_info['velocity_max']
        vel_min = enemy_info['velocity_min']
        vel_range = random.randrange(vel_min, vel_max)
        velocity = pygame.Vector2(random.choice([-vel_range, vel_range]), random.choice([-vel_range, vel_range]))
        enemy_entity = create_sprite(world, pos, velocity, enemy_surface)
        world.add_component(enemy_entity, CTagEnemy())
        world.add_component(enemy_entity, CTagBouncer())
        ServiceLocator.sounds_service.play(enemy_info["sound"])
    
def create_enemy_spawner(ecs_world:esper.World, level_data:dict):
    spawner_entity = ecs_world.create_entity()
    print('created entity')
    ecs_world.add_component(spawner_entity,
                            CEnemySpawner(level_data['enemy_spawn_events']))
    
def create_player_square(world:esper.World, player_info:dict, player_lvl_info:dict) -> int:
    player_sprite = ServiceLocator.images_service.get(player_info["image"])
    size = player_sprite.get_size()
    size = (size[0] / player_info["animations"]["number_frames"], size[1])
    pos = pygame.Vector2(player_lvl_info["position"]["x"] - (size[0] / 2), 
                         player_lvl_info["position"]["y"] - (size[1] / 2))
    vel = pygame.Vector2(0,0)
    player_entity = create_sprite(world, pos, vel, player_sprite)
    world.add_component(player_entity, CTagPlayer())
    world.add_component(player_entity, CAnimation(player_info["animations"]))
    world.add_component(player_entity, CPlayerState())
    return player_entity

def create_input_player(world:esper.World):
    input_left = world.create_entity()
    input_right = world.create_entity()
    input_up = world.create_entity()
    input_down = world.create_entity()
    input_fire = world.create_entity()
    input_pause = world.create_entity()
    input_powerup = world.create_entity()

    world.add_component(input_left, CInputCommand("PLAYER_LEFT", pygame.K_LEFT))
    world.add_component(input_right, CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT))
    world.add_component(input_up, CInputCommand("PLAYER_UP", pygame.K_UP))
    world.add_component(input_down, CInputCommand("PLAYER_DOWN", pygame.K_DOWN))
    world.add_component(input_pause, CInputCommand("PAUSE", pygame.K_p))
    world.add_component(input_fire, CInputCommand("PLAYER_FIRE", pygame.BUTTON_LEFT))
    world.add_component(input_powerup, CInputCommand("PLAYER_POWERUP", pygame.BUTTON_RIGHT))

def create_bullet(world:esper.World, pos_player:pygame.Vector2, pos_cursor:pygame.Vector2, bullet_info:dict, player_size:pygame.Vector2):
    bullet_surface = ServiceLocator.images_service.get(bullet_info["image"])
    bullet_size = bullet_surface.get_rect().size
    vel_direction = (pos_cursor - pos_player).normalize()
    vel = vel_direction * bullet_info["velocity"]
    pos = pygame.Vector2(pos_player.x + player_size.x/2 - (bullet_size[0] / 2 ),
                        pos_player.y + player_size.y/2 - (bullet_size[1] / 2 ))
    bullet_entity = create_sprite(world, pos, vel, bullet_surface)
    world.add_component(bullet_entity, CTagBullet())
    ServiceLocator.sounds_service.play(bullet_info["sound"])

def create_explosion(world:esper.World, pos:pygame.Vector2, explosion_info:dict):
    explosion_surf = ServiceLocator.images_service.get(explosion_info["image"])
    vel = pygame.Vector2(0,0)
    explosion_entity = create_sprite(world, pos, vel, explosion_surf)
    world.add_component(explosion_entity, CTagExplosion())
    world.add_component(explosion_entity, CAnimation(explosion_info["animations"]))
    ServiceLocator.sounds_service.play(explosion_info["sound"])

def create_hunter(world:esper.World, pos:pygame.Vector2, hunter_info:dict):
    hunter_surface = ServiceLocator.images_service.get(hunter_info["image"])
    velocity = pygame.Vector2(0,0)
    hunter_entity = create_sprite(world, pos, velocity, hunter_surface)
    #world.add_component(hunter_entity, CTagHunter())
    world.add_component(hunter_entity, CAnimation(hunter_info["animations"]))
    world.add_component(hunter_entity, CHunterState(pos.copy()))
    world.add_component(hunter_entity, CTagEnemy())

def create_interface(world:esper.World, interface_info:dict):
    for text_entry in interface_info:
        val = interface_info[text_entry]
        pos = pygame.Vector2(val["position"]["x"],val["position"]["y"])
        text_entity = world.create_entity()
        world.add_component(text_entity, CTransform(pos))
        world.add_component(text_entity, 
                            CSurface.from_text(val["text"], 
                            pygame.Color(val["color"]["r"],val["color"]["g"],val["color"]["b"]), 
                            ServiceLocator.fonts_service.get(val["font"], val["size"]), val["size"]))
        
def create_powerup_interface(world:esper.World, screen:pygame.Surface):
    text_size = 15
    pos = pygame.Vector2(0, screen.get_height() - text_size * 2) #bottom left
    text_entity = world.create_entity()
    world.add_component(text_entity, CTransform(pos))
    world.add_component(text_entity, 
                        CSurface.from_text("100%", 
                                            pygame.Color(255, 255, 255), 
                                            ServiceLocator.fonts_service.get("assets/fnt/PressStart2P.ttf", text_size), 
                                            text_size))
    return text_entity
    

def create_pause_text(world:esper.World, pos:pygame.Vector2, font:pygame.Font):
    pt_entity = world.create_entity()
    world.add_component(pt_entity, CTransform(pos))
    world.add_component(pt_entity, 
                        CSurface.from_text("Paused", 
                                            pygame.Color(255,255,255), 
                                            font, 
                                            20)
                        )
    return pt_entity

def create_powerup_timer(world:esper.World, max_time:float):
    timer_entity = world.create_entity()
    world.add_component(timer_entity, CPowerupTimer(max_time))
    return timer_entity

def create_powerup_bullets(world:esper.World, bullet_info:dict):
    pu_bullet_surface = ServiceLocator.images_service.get(bullet_info["image"])
    pu_bullet_size = pu_bullet_surface.get_rect().size
    vel_directions = [
        pygame.Vector2(1,1).normalize(),
        pygame.Vector2(-1,1).normalize(),
        pygame.Vector2(1,-1).normalize(),
        pygame.Vector2(-1,-1).normalize()
    ]
    components = world.get_components(CTagBullet, CTransform)
    c_b:CTagBullet
    c_t:CTransform
    for bullet_entity, (c_b, c_t) in components:
        for vel_dir in vel_directions:
            vel = vel_dir * bullet_info["velocity"]
            pos = pygame.Vector2(c_t.pos.x - (pu_bullet_size[0] / 2 ),
                                c_t.pos.y - (pu_bullet_size[1] / 2 ))
            bullet_pu_entity = create_sprite(world, pos, vel, pu_bullet_surface)
            world.add_component(bullet_pu_entity, CTagBullet())
        world.delete_entity(bullet_entity)
    ServiceLocator.sounds_service.play(bullet_info["sound"])