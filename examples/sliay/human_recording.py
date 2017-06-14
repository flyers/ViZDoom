#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import cv2
from vizdoom import *

parser = argparse.ArgumentParser(
    description='record human training data in CIG')
parser.add_argument('--config', type=str, default='/home/sliay/Documents/ViZDoom/scenarios/cig.cfg')
parser.add_argument('--map', type=str, default='map01')
parser.add_argument('--bots', type=int, default=7)
parser.add_argument('--frame-skip', type=int, default=4)
parser.add_argument('--ip', type=str, default=None)
parser.add_argument('--dir', type=str, required=True)
args = parser.parse_args()

save_dir = os.path.join(args.dir, 'screens')
os.makedirs(save_dir)
f_frag = open(os.path.join(save_dir, 'frags.txt'), 'w')
f_health = open(os.path.join(save_dir, 'health.txt'), 'w')
f_ammo = open(os.path.join(save_dir, 'ammo.txt'), 'w')
f_action = open(os.path.join(save_dir, 'action.txt'), 'w')

frame_skip = args.frame_skip

game = DoomGame()

game.load_config(args.config)
game.set_doom_map(args.map)  # Limited deathmatch.
# game.set_doom_map("map02")  # Full deathmatch.

game.add_game_args("-host 1 -deathmatch +sv_spawnfarthest 1 "
                   "+timelimit 5.0 +sv_forcerespawn 1 +sv_noautoaim 1 +sv_respawnprotect 1 +sv_nocrouch 1 "
                   "+viz_respawn_delay 10 +viz_nocheat 1 ")
if args.ip is not None:
    game.add_game_args("-join " + args.ip + " ")

game.add_game_args("+name AI +colorset 0")
game.set_screen_format(ScreenFormat.RGB24)
# game.set_screen_format(ScreenFormat.ARGB32)
# game.set_screen_format(ScreenFormat.GRAY8)

# game.set_screen_format(ScreenFormat.BGR24)
# game.set_screen_format(ScreenFormat.RGBA32)
# game.set_screen_format(ScreenFormat.BGRA32)
# game.set_screen_format(ScreenFormat.ABGR32)

# Raw Doom buffer with palette's values. This one makes no sense in particular
# game.set_screen_format(ScreenFormat.DOOM_256_COLORS)

# Sets resolution for all buffers.
game.set_screen_resolution(ScreenResolution.RES_640X480)

# Enables depth buffer.
game.set_depth_buffer_enabled(True)

# Enables labeling of in game objects labeling.
game.set_labels_buffer_enabled(True)

# Enables buffer with top down map of he current episode/level .
game.set_automap_buffer_enabled(True)
game.set_automap_mode(AutomapMode.OBJECTS)
game.set_automap_rotate(False)
game.set_automap_render_textures(False)

game.set_render_hud(True)
game.set_render_minimal_hud(False)
game.set_mode(Mode.ASYNC_SPECTATOR)
game.init()

print("Episode Started")
print('Available Buttons:', game.get_available_buttons())
game.send_game_command("removebots")
for i in range(args.bots):
    game.send_game_command("addbot")

# Play until the game (episode) is over.
cnt = 0
while not game.is_episode_finished():

    s = game.get_state()
    if cnt % frame_skip == 0:
        cv2.imwrite(os.path.join(save_dir, 'screen_%05d.png' % cnt), s.screen_buffer)
    cnt += 1
    game.advance_action()

    if game.is_player_dead():
        game.respawn_player()

    print("Frags:", game.get_game_variable(GameVariable.FRAGCOUNT))
    print("Health:", game.get_game_variable(GameVariable.HEALTH))
    print("Ammo:", game.get_game_variable(GameVariable.AMMO5))
    print("Performed Action:", game.get_last_action())

    f_frag.write('%d\n' % game.get_game_variable(GameVariable.FRAGCOUNT))
    f_health.write('%d\n' % game.get_game_variable(GameVariable.HEALTH))
    f_ammo.write('%d\n' % game.get_game_variable(GameVariable.AMMO5))
    action = game.get_last_action()
    for i in range(len(action)):
        if i != len(action)-1:
            f_action.write('%d ' % action[i])
        else:
            f_action.write('%d\n' % action[i])

print("Episode finished.")
print("************************")
f_frag.close()
f_health.close()
f_ammo.close()
f_action.close()

game.close()
