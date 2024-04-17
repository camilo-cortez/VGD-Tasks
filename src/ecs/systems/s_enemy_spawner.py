import esper
import pygame
import random
from src.create.prefab_creator import create_enemy_square
from src.ecs.components.c_enemy_spawner import CEnemySpawner, SpawnEventData

def system_enemy_spawner(world:esper.World, enemies_data:dict, delta_time:float):
    components = world.get_component(CEnemySpawner)
    c_s:CEnemySpawner
    for _, c_s in components:
        c_s.current_time += delta_time
        spw_evt:SpawnEventData
        for spw_evt in c_s.spawn_event_data:
            if c_s.current_time >= spw_evt.time and not spw_evt.triggered:
                spw_evt.triggered = True
                print(f"{c_s.current_time} > {spw_evt.time}")
                create_enemy_square(world,
                                    spw_evt.position,
                                    enemies_data[spw_evt.enemy_type])
