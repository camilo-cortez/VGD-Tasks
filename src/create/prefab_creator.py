import esper
import pygame
import random

from src.ecs.components.c_animation import CAnimation
from src.ecs.components.c_input_command import CInputCommand
from src.ecs.components.c_player_state import CPlayerState
from src.ecs.components.c_surface import CSurface
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_enemy_spawner import CEnemySpawner, SpawnEventData
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.ecs.components.tags.c_tag_enemy import CTagEnemy
from src.ecs.components.tags.c_tag_player import CTagPlayer

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

def create_enemy_square(world:esper.World, pos:pygame.Vector2, enemy_info:dict):
    enemy_surface = pygame.image.load(enemy_info['image']).convert_alpha()
    vel_max = enemy_info['velocity_max']
    vel_min = enemy_info['velocity_min']
    vel_range = random.randrange(vel_min, vel_max)
    velocity = pygame.Vector2(random.choice([-vel_range, vel_range]), random.choice([-vel_range, vel_range]))
    enemy_entity = create_sprite(world, pos, velocity, enemy_surface)
    world.add_component(enemy_entity, CTagEnemy())
    
def create_enemy_spawner(ecs_world:esper.World, level_data:dict):
    spawner_entity = ecs_world.create_entity()
    print('created entity')
    ecs_world.add_component(spawner_entity,
                            CEnemySpawner(level_data['enemy_spawn_events']))
    
def create_player_square(world:esper.World, player_info:dict, player_lvl_info:dict) -> int:
    player_sprite = pygame.image.load(player_info["image"]).convert_alpha()
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

    world.add_component(input_left, CInputCommand("PLAYER_LEFT", pygame.K_LEFT))
    world.add_component(input_right, CInputCommand("PLAYER_RIGHT", pygame.K_RIGHT))
    world.add_component(input_up, CInputCommand("PLAYER_UP", pygame.K_UP))
    world.add_component(input_down, CInputCommand("PLAYER_DOWN", pygame.K_DOWN))
    world.add_component(input_fire, CInputCommand("PLAYER_FIRE", pygame.MOUSEBUTTONDOWN))

def create_bullet(world:esper.World, pos_player:pygame.Vector2, pos_cursor:pygame.Vector2, bullet_info:dict, player_size:pygame.Vector2):
    bullet_surface = pygame.image.load(bullet_info['image'])
    bullet_size = bullet_surface.get_rect().size
    vel_direction = (pos_cursor - pos_player).normalize()
    vel = vel_direction * bullet_info["velocity"]
    pos = pygame.Vector2(pos_player.x + player_size.x/2 - (bullet_size[0] / 2 ),
                        pos_player.y + player_size.y/2 - (bullet_size[1] / 2 ))
    bullet_entity = create_sprite(world, pos, vel, bullet_surface)
    world.add_component(bullet_entity, CTagBullet())