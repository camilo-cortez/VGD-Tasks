import pygame
import esper
import json

from src.create.prefab_creator import create_input_player, create_pause_text, create_player_square, create_enemy_spawner, create_bullet, create_interface, create_powerup_bullets, create_powerup_interface, create_powerup_timer
from src.ecs.components.c_enemy_spawner import SpawnEventData
from src.ecs.components.c_input_command import CInputCommand, CommandPhase
from src.ecs.components.c_powerup_timer import CPowerupTimer
from src.ecs.systems.s_animation import system_animation
from src.ecs.systems.s_bullet_limits import system_bullet_limits
from src.ecs.systems.s_collision_bullet_enemy import system_collision_bullet_enemy
from src.ecs.systems.s_collision_player_enemy import system_collision_player_enemy
from src.ecs.systems.s_delete_explosion import system_delete_explosions
from src.ecs.systems.s_hunter_state import system_hunter_state
from src.ecs.systems.s_input_player import system_input_player
from src.ecs.systems.s_movement import system_movement
from src.ecs.systems.s_player_limits import system_player_limits
from src.ecs.systems.s_player_state import system_player_state
from src.ecs.systems.s_powerup_timer import system_powerup_timer
from src.ecs.systems.s_rendering import system_rendering
from src.ecs.systems.s_screen_bounce import system_screen_bounce
from src.ecs.systems.s_enemy_spawner import system_enemy_spawner
from src.ecs.components.c_velocity import CVelocity
from src.ecs.components.c_transform import CTransform
from src.ecs.components.c_surface import CSurface
from src.ecs.components.tags.c_tag_bullet import CTagBullet
from src.engine.service_locator import ServiceLocator

class GameEngine:
    def __init__(self) -> None:
        self._load_config_files()

        pygame.init()
        pygame.display.set_caption(self.window_cfg['title'])
        self.screen = pygame.display.set_mode((self.window_cfg["size"]["w"], self.window_cfg["size"]["h"]), 0)
        self.clock = pygame.time.Clock()
        self.is_running = False
        self.framerate = self.window_cfg['framerate']
        self.delta_time = 0
        self.window_bg_color = pygame.Color(self.window_cfg['bg_color']['r'],
                                            self.window_cfg['bg_color']['g'],
                                            self.window_cfg['bg_color']['b'])
        self.ecs_world = esper.World()

    def _load_config_files(self):
        with open('./assets/cfg/window.json') as window_file:
            self.window_cfg = json.load(window_file)
        with open('./assets/cfg/enemies.json') as enemies_file:
            self.enemies_cfg = json.load(enemies_file)
        with open('./assets/cfg/level_01.json') as level_01_file:
            self.level_01_cfg = json.load(level_01_file)
        with open('./assets/cfg/player.json') as player_file:
            self.player_cfg = json.load(player_file)
        with open('./assets/cfg/bullet.json') as bullet_file:
            self.bullet_cfg = json.load(bullet_file)
        with open('./assets/cfg/explosion.json') as explosion_file:
            self.explosion_cfg = json.load(explosion_file)
        with open('./assets/cfg/interface.json') as interface_file:
            self.interface_cfg = json.load(interface_file)
        with open('./assets/cfg/bullet_pu.json') as bullet_pu_file:
            self.bullet_pu_cfg = json.load(bullet_pu_file)

    def run(self) -> None:
        self._create()
        self.is_running = True
        while self.is_running:
            self._calculate_time()
            self._process_events()
            self._update()
            self._draw()
        self._clean()

    def _create(self):
       self._player_entity = create_player_square(self.ecs_world, self.player_cfg, self.level_01_cfg["player_spawn"])
       self._player_c_v = self.ecs_world.component_for_entity(self._player_entity, CVelocity)
       self._player_c_t = self.ecs_world.component_for_entity(self._player_entity, CTransform)
       self._player_c_s = self.ecs_world.component_for_entity(self._player_entity, CSurface)
       self._is_paused = False
       self._pause_font = ServiceLocator.fonts_service.get('assets/fnt/PressStart2P.ttf', 20)
       self._pause_entity = None
       create_interface(self.ecs_world, self.interface_cfg)
       self._powerup_interface = create_powerup_interface(self.ecs_world, self.screen)
       create_enemy_spawner(self.ecs_world, self.level_01_cfg)
       create_input_player(self.ecs_world)
       self._powerup_timer_entity = create_powerup_timer(self.ecs_world, 5.0)
       
    def _calculate_time(self):
        self.clock.tick(self.framerate)
        self.delta_time = self.clock.get_time() / 1000.0

    def _process_events(self):
        for event in pygame.event.get():
            system_input_player(self.ecs_world, event, self._do_action)
            if event.type == pygame.QUIT:
                self.is_running = False

    def _update(self):
        self.cursor_pos = pygame.mouse.get_pos()
        if not self._is_paused:
            system_enemy_spawner(self.ecs_world, self.enemies_cfg, self.delta_time)
            system_movement(self.ecs_world, self.delta_time)
            system_player_state(self.ecs_world)
            system_hunter_state(self.ecs_world, self._player_entity, self.enemies_cfg["Hunter"])

            system_screen_bounce(self.ecs_world, self.screen)
            system_player_limits(self.ecs_world, self.screen, self._player_entity)
            system_bullet_limits(self.ecs_world, self.screen)
            system_collision_player_enemy(self.ecs_world, self._player_entity, self.level_01_cfg, self.explosion_cfg)
            system_collision_bullet_enemy(self.ecs_world, self.explosion_cfg)
            system_animation(self.ecs_world, self.delta_time)
            system_powerup_timer(self.ecs_world, self.delta_time, self._powerup_interface)

            system_delete_explosions(self.ecs_world)
        self.ecs_world._clear_dead_entities()

    def _draw(self):
        self.screen.fill(self.window_bg_color)
        system_rendering(self.ecs_world, self.screen)
        pygame.display.flip()

    def _clean(self):
        self.ecs_world.clear_database()
        pygame.quit()

    def _do_action(self, c_input:CInputCommand):
        if c_input.name == "PLAYER_LEFT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
        elif c_input.name == "PLAYER_RIGHT":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.x += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.x -= self.player_cfg["input_velocity"]
        elif c_input.name == "PLAYER_UP":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
        elif c_input.name == "PLAYER_DOWN":
            if c_input.phase == CommandPhase.START:
                self._player_c_v.vel.y += self.player_cfg["input_velocity"]
            elif c_input.phase == CommandPhase.END:
                self._player_c_v.vel.y -= self.player_cfg["input_velocity"]
        elif c_input.name == "PAUSE" and c_input.key == pygame.K_p and c_input.phase == CommandPhase.START:
            self._is_paused = not self._is_paused
            if self._is_paused:
                self._pause_entity = create_pause_text(self.ecs_world, pygame.Vector2(self.screen.get_width()/2, self.screen.get_height()/2), self._pause_font)
            else:
                self.ecs_world.delete_entity(self._pause_entity)
                self._pause_entity = None
        elif c_input.name == "PLAYER_FIRE":
            if c_input.phase == CommandPhase.START:
                player_size = pygame.Vector2(self._player_c_s.area.size[0], self._player_c_s.area.size[1])
                cursor_pos = pygame.mouse.get_pos()
                max_bullets = self.level_01_cfg["player_spawn"]["max_bullets"]
                current_bullets = len(self.ecs_world.get_component(CTagBullet))
                if (current_bullets < max_bullets):
                    create_bullet(self.ecs_world, self._player_c_t.pos, pygame.Vector2(cursor_pos[0], cursor_pos[1]), self.bullet_cfg, player_size)
        elif c_input.name == "PLAYER_POWERUP":
            pu_timer = self.ecs_world.component_for_entity(self._powerup_timer_entity, CPowerupTimer)
            can_use = pu_timer.reset()
            if (can_use == True):
                create_powerup_bullets(self.ecs_world, self.bullet_pu_cfg)
            else:
                print(f"on cd: {pu_timer.current_time}")
        
  


