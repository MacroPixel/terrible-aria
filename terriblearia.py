import os
from math import sin, cos
import random
import traceback
import time

# IMPORTANT CONSTANTS
DEBUG = False
SHOW_PROG = True








# Used for switching rooms
class MoveException( BaseException ):

  def __init__( self, room, arg ):
    self.room = room
    self.arg = arg

# A pretty simple 2D vector class
# Its main purpose is to allow you to perform calculations that I find helpful
# e.g. instead of writing `a = V2( a.x * 3, a.y * 5 )`, you can write `a.m( 3, 5 )`
class V2:

  def __init__( self, x = 0, y = 0 ):
    self.u( x, y )

  # These two functions help to reduce repetitive code within the operation functions
  def __op( self, a, b, op ):

    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': return a / b

  def __op2( self, a, b, op ):

    if isinstance( a, V2 ):
      self.x = self.__op( self.x, a.x, op )
      self.y = self.__op( self.y, a.y, op )
    else:
      self.x = self.__op( self.x, a, op )
      self.y = self.__op( self.y, a if b == 'd' else b, op )

  # Update
  def u( self, a = 0, b = 0 ):
    self.x = a
    self.y = b
    return self

  # Add
  def a( self, a, b = 'd' ):
    self.__op2( a, b, '+' )
    return self

  # Subtract
  def s( self, a, b = 'd' ):
    self.__op2( a, b, '-' )
    return self

  # Multiply
  def m( self, a, b = 'd' ):
    self.__op2( a, b, '*' )
    return self

  # Divide
  def d( self, a, b = 'd' ):
    self.__op2( a, b, '/' )
    return self

  # Return a list
  def l( self ):
    return [ self.x, self.y ]

  # Return a copy
  def copy( self ):
    c = V2( self.x, self.y )
    return c

# ITEM CONSTANTS
I_NULL = 0
I_C_SSWORD = 1
I_C_PICK = 2
I_GRASS = 3
I_STONE = 4
I_WOOD = 5
I_IRON_ORE = 6
I_SILVER_ORE = 7
I_GOLD_ORE = 8
I_IRON_BAR = 9
I_SILVER_BAR = 10
I_GOLD_BAR = 11
I_W_SWORD = 12
I_I_SWORD = 13
I_S_SWORD = 14
I_G_SWORD = 15
I_W_BOW = 16
I_I_BOW = 17
I_S_BOW = 18
I_G_BOW = 19
I_TORCH = 20
I_ARROW = 21
I_F_ARROW = 22
I_PLATFORM = 23
I_CHEST = 24
I_SUS_EYE = 25
I_GRENADE = 26
I_HEALTH_POTION = 27
I_CRYSTAL = 28
I_MAGIC_STAFF = 29
I_TROPHY = 30
I_MEGA_CRYSTAL = 31
I_SHACKLE = 32
I_HARPY_WINGS = 33
I_I_ARMOR = 34
I_S_ARMOR = 35
I_G_ARMOR = 36
I_GEL = 37
I_FEATHER = 38
I_LENS = 39

ITEM_META = [
  [ 'NULL', 'An item you shouldn\'t have' ],
  [ 'Copper Shortsword', 'Better than nothing! ## Medn damage: 12' ],
  [ 'Copper Pickaxe', 'The best pick in the game ## (Also the only pick in the game)' ],
  [ 'Grass', 'Not useful for much, but you\'ll acquire it anyway ## Placeable' ],
  [ 'Stone', 'The most prevalent material in the world ## Placeable ## Material' ],
  [ 'Wood', 'A reliable building block/material ## Placeable ## Material' ],
  [ 'Iron Ore', 'A relatively weak ore ## Material' ],
  [ 'Silver Ore', 'A slightly more powerful ore ## Material' ],
  [ 'Gold Ore', 'A relatively strong ore ## Material' ],
  [ 'Iron Bar', 'A relatively weak bar ## Material' ],
  [ 'Silver Bar', 'A slightly more powerful bar ## Material' ],
  [ 'Gold Bar', 'A relatively strong bar ## Material' ],
  [ 'Wooden Sword', 'Unobtainable because I forgot I was supposed to make them' ],
  [ 'Iron Sword', 'Not that strong ## Mean damage: 18' ],
  [ 'Silver Sword', 'Decently strong ## Mean damage: 22' ],
  [ 'Golden Sword', 'Pretty strong ## Mean damage: 26' ],
  [ 'Wooden Bow', 'Pretty weak ## Mean damage: 9' ],
  [ 'Iron Bow', 'Not that strong ## Mean damage: 14' ],
  [ 'Silver Bow', 'Decently strong ## Mean damage: 17' ],
  [ 'Golden Bow', 'Pretty strong ## Mean damage: 22' ],
  [ 'Torch', 'bright. ## Material' ],
  [ 'Arrow', 'Used as ammo for bows ## Material' ],
  [ 'Flaming Arrow', 'Used as ammo for bows ## Damage multiplier: 2' ],
  [ 'Wooden Platform', 'Can be stood on or passed through' ],
  [ 'Chest', 'Holds items ## (Also took a long time to program)' ],
  [ 'Sus Eye', 'You should use it; it\'d make for a cool party trick ## What could go wrong?' ],
  [ 'Grenade', 'Explodes on contact, dealing a lot of damage ## Mean damage: 36' ],
  [ 'Healing Potion', 'Usable anytime ## Grants 100 HP' ],
  [ 'Life Crystal', 'Increases MHP by 20 HP' ],
  [ 'Magic Staff', 'Extremely strong ## Mean damage: 30 ## Damage multiplier: 3 (33% chance)' ],
  [ 'Trophy', 'That\'s it. That\'s all you get.' ],
  [ 'Mega Crytstal', 'Description' ],
  [ 'Shackle', 'Drastically increases your chance of fleeing from a battle.' ],
  [ 'Harpy Wings', 'Infinite upward mobility ## (Equipped automatically)' ],
  [ 'Iron Armor', 'Not that strong ## 30% damage absorption ## (Equipped automatically)' ],
  [ 'Silver Armor', 'Decently strong ## 55% damage absorption ## (Equipped automatically)' ],
  [ 'Gold Armor', 'Pretty strong ## 85% damage absorption ## (Equipped automatically)' ],
  [ 'Gel', 'Can be crafted into torches ## Material' ],
  [ 'Feather', 'Used properly, can grant you access to the sky ## Material' ],
  [ 'Lens', 'What could these be for? ## Material' ]
]

# GLOBAL CONSTANTS
AIR_BLOCKS = [ ' ', 'l', 'L', 'c', 'C', 'p' ]
PLATFORM_BLOCKS = [ 'p' ]
ITEM_BLOCKS = { 'g': I_GRASS, 's': I_STONE, 'w': I_WOOD, 'l': I_WOOD, 'i': I_IRON_ORE, 'S': I_SILVER_ORE, 'G': I_GOLD_ORE,
  'p': I_PLATFORM, 'c': I_CHEST, 'C': I_CRYSTAL }

# GLOBAL VARIABLES
g_data = {}
g_cname = ''
g_wname = ''
g_pos = V2( 0, 0 )
g_spawn = V2( 0, 0 )
g_view = V2( 0, 0 )
g_world_size = V2( 0, 0 )
g_tile_data = []
g_tile_special = {}
g_enemy_timer = 0
g_seed = 0
g_hp = 0
g_hp_max = 0
g_items = []
g_items_extra = []
g_slot = 0
g_deaths = 0
g_versions = [ '', '' ]
g_play_time = 0
g_play_time_last = 0
g_show_help = True
g_tmap = {
  'player': 'Δ',
  'air': ' ',
  'grass': '~',
  'stone': '#',
  'log': ']',
  'leaves': '*',
  'iron': '&',
  'silver': '$',
  'gold': '%',
  'wood': '=',
  'chest': '©',
  'crystal': '♥',
  'enemy': '!'
}
g_monster = 0

# Returns a number such that min <= x <= max
def clamp( n, mn, mx ):

  return min( max( n, mn ), mx )

# Returns the distance between two vector objects
def dist( a, b ):

  return ( ( a.x - b.x ) ** 2 + ( a.y - b.y ) ** 2 ) ** 0.5

def get_tile( a, b = 0 ):

  if isinstance( a, V2 ):
    return g_tile_data[ xy2c( a.x, a.y, g_world_size.x ) ]
  else:
    return g_tile_data[ xy2c( a, b, g_world_size.x ) ]

def item_meta( item_id, component = 0, c = 0 ):

  # Correct ID if c is flagged as 1
  if c == 1:
    item_id = g_items[ item_id ][0]

  if not ( 0 <= item_id < len( ITEM_META ) ) or component not in [ 0, 1 ]:
    return ( 'RANGE_ERROR' )
  return ITEM_META[ item_id ][ component ]

# Updates global time since last queried
def update_playtime():

  global g_play_time, g_play_time_last

  if g_play_time_last == 0:
    g_play_time_last = time.time()
  g_play_time += ( time.time() - g_play_time_last )
  g_play_time_last = time.time()

# Prints playtime in DD:HH:MM:SS format
def format_playtime( tm ):

  t_d = tm // 86400
  t_h = ( tm % 86400 ) // 3600
  t_m = ( tm % 3600 ) // 60
  t_s = ( tm % 60 )

  t_str = ""
  t_str += f'{ t_d }d ' if tm >= 86400 else ''
  t_str += f'{ t_h }h ' if tm >= 3600 else ''
  t_str += f'{ t_m }m ' if tm >= 60 else ''
  t_str += f'{ t_s }s'

  return t_str

# Flattens a 2D index [x, y] down to a 1D index [c]
def xy2c( x, y, w ):

  return ( y * w ) + x

# Inflates a 1D index [c] into a 2D index [x, y]
def c2xy( c, w ):

  return ( c % w, c // w )

# Converts a block's character-ID into the character displayed in-game
def char2tile( c ):

  if c == ' ': return g_tmap[ 'air' ]
  if c == 'g': return g_tmap[ 'grass' ]
  if c == 's': return g_tmap[ 'stone' ]
  if c == 'l': return g_tmap[ 'log' ]
  if c == 'L': return g_tmap[ 'leaves' ]
  if c == 'i': return g_tmap[ 'iron' ]
  if c == 'S': return g_tmap[ 'silver' ]
  if c == 'G': return g_tmap[ 'gold' ]
  if c == 'w': return g_tmap[ 'wood' ]
  if c == 'p': return g_tmap[ 'platform' ]
  if c == 'c': return g_tmap[ 'chest' ]
  if c == 'C': return g_tmap[ 'crystal' ]
  return '?'

# Monster class
# This class (mainly the player_turn() and monster_turn() functions) is a little bit of a mess,
# but there's no way of fixing it that would be worth my time at the moment
class Monster:

  # I don't think I need to explain what this list is for
  TYPES = [ 'slime', 'zombie', 'demon_eye', 'cave_bat', 'skeleton', 'undead_miner', 'harpy', 'tim' ]

  # The health each monster starts off with
  HEALTHS = {
    'slime' : 50, 'zombie' : 90, 'demon_eye' : 70, 'cave_bat' : 40,
    'skeleton' : 150, 'undead_miner' : 120, 'harpy' : 80, 'tim' : 200
  }

  # The player's options for each player turn
  # Format: [ Letter ID, Action Name, Requirements ]
  PLAYER_ATTACKS = {
    'slime' : [ [ 's', 'Swing sword', 's' ], [ 'f', 'Shoot forward', 'b' ], [ 'u', 'Shoot upward', 'b' ], [ 'n', 'Do nothing' ] ],
    'zombie' : [ [ 's', 'Swing sword', 's' ], [ 'f', 'Shoot forward', 'b' ], [ 'u', 'Shoot upward', 'b' ], [ 'n', 'Do nothing' ] ],
    'demon_eye' : [ [ 's', 'Jump and swing sword (*)', 's' ], [ 'r', 'Shoot rightward', 'b' ], [ 'l', 'Shoot leftward', 'b' ], [ 'n', 'Do nothing' ] ],
    'cave_bat' : [ [ 's', 'Jump and swing sword', 's' ], [ 'f', 'Shoot forward', 'b' ], [ 'r', 'Shoot rightward', 'b' ], [ 'n', 'Do nothing' ] ],
    'skeleton' : [ [ 's', 'Swing sword (*)', 's' ], [ 'j', 'Jump and swing sword', 's' ], [ 'u', 'Shoot upward', 'b' ],
      [ 'r', 'Shoot rightward', 'b' ], [ 'l', 'Shoot leftward', 'b' ], [ 'n', 'Do nothing' ] ],
    'undead_miner' : [ [ 's', 'Swing sword', 's' ], [ 'a', 'Shoot arrow', 'b' ], [ 'n', 'Do nothing' ] ],
    'harpy' : [ [ 'g', 'Throw grenade', 'g' ], [ 'r', 'Shoot rightward', 'b' ], [ 'l', 'Shoot leftward', 'b' ], [ 'n', 'Do nothing' ] ],
    'tim' : [ [ 's', 'Swing sword', 's' ], [ 'a', 'Shoot arrow', 'b' ], [ 'g', 'Throw grenade', 'g' ], [ 'n', 'Do nothing' ] ]
  }

  # The monster's options for each player turn
  MONSTER_DODGES = {
    'slime' : [ 'jump', 'sit' ],
    'zombie' : [ 'jump', 'move backward' ],
    'demon_eye' : [ 'fly rightward', 'fly leftward' ],
    'cave_bat' : [ 'hover', 'fly sideways', 'fly upward' ],
    'skeleton' : [ 'shield', 'jump', 'move rightward', 'move leftward' ],
    'undead_miner' : [ 'deflect', 'jump' ],
    'harpy' : [ 'fly upward', 'fly rightward', 'fly leftward' ],
    'tim' : [ 'reflect', 'charge attack', 'heal', 'teleport' ]
  }

  # The result of each player turn
  # Format: [ Text + HP Lost + modifier ]
  P_TURN_RESULTS = {
    'slime : s : jump' : [ 'The enemy jumped over your sword.' ],
    'slime : s : sit' : [ 'You attacked the enemy.', ( 12, 24 ) ],
    'slime : f : jump' : [ 'The enemy jumped over your arrow.' ],
    'slime : f : sit' : [ 'The enemy remained stationary and was hit by your arrow.', ( 8, 16 ) ],
    'slime : u : jump' : [ 'The enemy jumped into your arrow.', ( 8, 16 ) ],
    'slime : u : sit' : [ 'The enemy remained stationary, so your arrow missed.' ],
    'slime : n : jump' : [ 'The enemy jumped, and you didn\'t attack it.' ],
    'slime : n : sit' : [ 'The enemy remained stationary, and you didn\'t attack it.' ],
    'zombie : s : jump' : [ 'The enemy jumped over your sword.' ],
    'zombie : s : move backward' : [ 'The enemy moved backward, but was still hit by your sword.', ( 12, 24 ) ],
    'zombie : f : jump' : [ 'The enemy jumped over your arrow.' ],
    'zombie : f : move backward' : [ 'The enemy moved backward, but was still hit by your arrow.', ( 8, 16 ) ],
    'zombie : u : jump' : [ 'The enemy jumped into your arrow.', ( 8, 16 ) ],
    'zombie : u : move backward' : [ 'The enemy moved backward, so your arrow missed.' ],
    'zombie : n : jump' : [ 'The enemy jumped, and you didn\'t attack it.' ],
    'zombie : n : move backward' : [ 'The enemy moved backward, and you didn\'t attack it.' ],
    'demon_eye : s : fly rightward' : [ 'chance', ( ( 0, 49, 'hit' ), ( 50, 99, 'miss' ) ) ],
    'demon_eye : s : fly rightward : hit' : [ 'You jumped and hit the enemy with your sword.', ( 12, 24 ) ],
    'demon_eye : s : fly rightward : miss' : [ 'You jumped, but barely missed the enemy.' ],
    'demon_eye : s : fly leftward' : [ 'chance', ( ( 0, 49, 'hit' ), ( 50, 99, 'miss' ) ) ],
    'demon_eye : s : fly leftward : hit' : [ 'You jumped and hit the enemy with your sword.', ( 12, 24 ) ],
    'demon_eye : s : fly leftward : miss' : [ 'You jumped, but barely missed the enemy.' ],
    'demon_eye : r : fly rightward' : [ 'The enemy flew rightward and was hit by your arrow.', ( 8, 16 ) ],
    'demon_eye : r : fly leftward' : [ 'The enemy flew leftward, so your arrow missed.' ],
    'demon_eye : l : fly rightward' : [ 'The enemy flew rightward, so your arrow missed.' ],
    'demon_eye : l : fly leftward' : [ 'The enemy flew leftward and was hit by your arrow.', ( 8, 16 ) ],
    'demon_eye : n : fly rightward' : [ 'The enemy flew rightward, and you didn\'t attack it.' ],
    'demon_eye : n : fly leftward' : [ 'The enemy flew leftward, and you didn\'t attack it.', ( 8, 16 ) ],
    'cave_bat : s : hover' : [ 'The enemy didn\'t move, so you jumped and hit it with your sword.', ( 12, 24 ) ],
    'cave_bat : s : fly sideways' : [ 'You jumped towards the enemy, but it flew sideways.' ],
    'cave_bat : s : fly upward' : [ 'You jumped towards the enemy, but it flew further away.' ],
    'cave_bat : f : hover' : [ 'The enemy didn\'t move, so your arrow hit it.', ( 8, 16 ) ],
    'cave_bat : f : fly sideways' : [ 'You shot at the enemy, but it flew sideways.' ],
    'cave_bat : f : fly upward' : [ 'The enemy flew further away, but was still hit by your arrow.', ( 8, 16 ) ],
    'cave_bat : r : hover' : [ 'The enemy didn\'t move, so your arrow flew to its right.' ],
    'cave_bat : r : fly sideways' : [ 'The enemy flew rightward into your arrow.', ( 8, 16 ) ],
    'cave_bat : r : fly upward' : [ 'The enemy flew further away, and your arrow flew to its right.' ],
    'cave_bat : n : hover' : [ 'The enemy didn\'t move, and you didn\'t attack it.' ],
    'cave_bat : n : fly sideways' : [ 'The enemy flew rightward, and you didn\'t attack it.' ],
    'cave_bat : n : fly upward' : [ 'The enemy flew further away, and you didn\'t attack it.' ],
    'skeleton : s : shield' : [ 'You swung your sword at the enemy, but it absorbed your attack.' ],
    'skeleton : s : jump' : [ 'chance', ( ( 0, 49, 'hit' ), ( 50, 99, 'miss' ) ) ],
    'skeleton : s : jump : hit' : [ 'The enemy was about to jump, but you hit it with your sword.', ( 12, 24 ) ],
    'skeleton : s : jump : miss' : [ 'You swung your sword at the enemy, but it jumped over it.' ],
    'skeleton : s : move rightward' : [ 'You swung your sword at the enemy, but it moved rightward.' ],
    'skeleton : s : move leftward' : [ 'You swung your sword at the enemy, but it moved leftward.' ],
    'skeleton : j : shield' : [ 'The enemy remained stationary, so you jumped too high to hit it.' ],
    'skeleton : j : jump' : [ 'The enemy jumped, so you jumped and hit it with your sword.', ( 16, 28 ) ],
    'skeleton : j : move rightward' : [ 'You jumped and swung, but the enemy dodged rightward.' ],
    'skeleton : j : move leftward' : [ 'You jumped and swung, but the enemy dodged leftward.' ],
    'skeleton : u : shield' : [ 'The enemy remained stationary, so your arrow missed it.' ],
    'skeleton : u : jump' : [ 'The enemy jumped and was hit by your arrow.', ( 8, 16 ) ],
    'skeleton : u : move rightward' : [ 'You shot your arrow upward, but the enemy moved rightward.' ],
    'skeleton : u : move leftward' : [ 'You shot your arrow upward, but the enemy moved leftward.' ],
    'skeleton : r : shield' : [ 'The enemy remained stationary, so your arrow missed it.' ],
    'skeleton : r : jump' : [ 'You shot your arrow rightward, but the enemy jumped.' ],
    'skeleton : r : move rightward' : [ 'The enemy moved rightward into your arrow.', ( 8, 16 ) ],
    'skeleton : r : move leftward' : [ 'You shot your arrow rightward, but the enemy moved leftward.' ],
    'skeleton : l : shield' : [ 'The enemy remained stationary, so your arrow missed it.' ],
    'skeleton : l : jump' : [ 'You shot your arrow rightward, but the enemy jumped.' ],
    'skeleton : l : move rightward' : [ 'You shot your arrow leftward, but the enemy moved rightward.' ],
    'skeleton : l : move leftward' : [ 'The enemy moved leftward into your arrow.', ( 8, 16 ) ],
    'skeleton : n : shield' : [ 'The enemy remained stationary, and you didn\'t attack it.' ],
    'skeleton : n : jump' : [ 'The enemy jumped, and you didn\'t attack it.' ],
    'skeleton : n : move rightward' : [ 'The enemy moved rightward, and you didn\'t attack it.' ],
    'skeleton : n : move leftward' : [ 'The enemy moved leftward, and you didn\'t attack it.' ],
    'undead_miner : s : deflect' : [ 'The enemy stayed still, so you hit it with your sword.', ( 12, 24 ) ],
    'undead_miner : s : jump' : [ 'The enemy jumped over your sword.' ],
    'undead_miner : a : deflect' : [ 'You shot at the enemy, but it blew up your arrow with a grenade.' ],
    'undead_miner : a : jump' : [ 'The enemy jumped, and you shot your arrow at it.', ( 6, 12 ) ],
    'undead_miner : n : deflect' : [ 'The enemy stayed still, and you didn\'t attack it.' ],
    'undead_miner : n : jump' : [ 'The enemy jumped, and you didn\'t attack it.' ],
    'harpy : g : fly upward' : [ 'The enemy flew upward and your grenade hit it.', ( 24, 48 ) ],
    'harpy : g : fly rightward' : [ 'The enemy flew right of your grenade, which fell back and hit you.', ( 24, 48 ), 'p' ],
    'harpy : g : fly leftward' : [ 'The enemy flew left of your grenade, which fell back and hit you.', ( 24, 48 ), 'p' ],
    'harpy : r : fly upward' : [ 'The enemy flew upward, so your arrow missed.' ],
    'harpy : r : fly rightward' : [ 'The enemy flew rightward into your arrow.', ( 6, 12 ) ],
    'harpy : r : fly leftward' : [ 'The enemy flew leftward, so your arrow missed.' ],
    'harpy : l : fly upward' : [ 'The enemy flew upward, so your arrow missed.' ],
    'harpy : l : fly rightward' : [ 'The enemy flew rightward, so your arrow missed.' ],
    'harpy : l : fly leftward' : [ 'The enemy flew leftward into your arrow.', ( 6, 12 ) ],
    'harpy : n : fly upward' : [ 'The enemy flew upward, and you didn\'t attack it.' ],
    'harpy : n : fly rightward' : [ 'The enemy flew rightward, and you didn\'t attack it.' ],
    'harpy : n : fly leftward' : [ 'The enemy flew leftward, and you didn\'t attack it.' ],
    'tim : s : reflect' : [ 'You swung your sword, but the enemy reflected your attack towards you.', ( 8, 16 ), 'p' ],
    'tim : s : charge attack' : [ 'You hit the enemy while it charged its attack.', ( 8, 16 ), 'c' ],
    'tim : s : heal' : [ 'You hit the enemy while it healed itself.', ( 8, 16 ), 'h' ],
    'tim : s : teleport' : [ 'You swung your sword at the enemy, but it teleported away from your attack.' ],
    'tim : a : reflect' : [ 'You shot an arrow at the enemy, but it reflected your attack towards you.', ( 6, 12 ), 'p' ],
    'tim : a : charge attack' : [ 'You shot the enemy while it charged its attack.', ( 6, 12 ), 'c' ],
    'tim : a : heal' : [ 'You shot the enemy while it healed itself.', ( 6, 12 ), 'h' ],
    'tim : a : teleport' : [ 'You shot at the enemy, but it teleported away from your attack.' ],
    'tim : g : reflect' : [ 'You used a grenade, but the enemy reflected your attack towards you.', ( 24, 48 ), 'p' ],
    'tim : g : charge attack' : [ 'You hit the enemy with a grenade while it charged its attack.', ( 24, 48 ), 'c' ],
    'tim : g : heal' : [ 'You hit the enemy with a grenade while it healed itself.', ( 24, 48 ), 'h' ],
    'tim : g : teleport' : [ 'You threw a grenade at the enemy, but it teleported away from your attack.' ],
    'tim : n : reflect' : [ 'The enemy attempted to reflect your attack, but you didn\'t attack it.' ],
    'tim : n : charge attack' : [ 'The enemy charged its next attack.', 0, 'c' ],
    'tim : n : heal' : [ 'The enemy healed itself.', 0, 'h' ],
    'tim : n : teleport' : [ 'The enemy teleported away from you.' ]
  }

  # The player's options for each monster turn
  # Format: [ Letter ID, Action Name, Requirements ]
  PLAYER_DODGES = {
    'slime' : [ [ 'b', 'Move backward' ], [ 'f', 'Move forward' ], [ 's', 'Remain stationary' ] ],
    'zombie' : [ [ 'b', 'Move backward' ], [ 'f', 'Move forward' ], [ 'j', 'Jump' ] ],
    'demon_eye' : [ [ 'b', 'Move backward' ], [ 'r', 'Move rightward' ], [ 'l', 'Move leftward' ], [ 'j', 'Jump (*)' ] ],
    'cave_bat' : [ [ 'j', 'Jump' ], [ 's', 'Remain stationary' ] ],
    'skeleton' : [ [ 'j', 'Jump' ], [ 'b', 'Move backward' ] ],
    'undead_miner' : [ [ 'j', 'Jump' ], [ 'f', 'Step forward' ], [ 's', 'Remain stationary' ] ],
    'harpy' : [ [ 'j', 'Jump' ], [ 'b', 'Move backward' ], [ 's', 'Move sideways' ] ],
    'tim' : [ [ 's', 'Remain stationary' ], [ 'j', 'Jump' ], [ 'r', 'Move rightward' ], [ 'l', 'Move leftward' ] ]
  }

  # The monster's options for each monster turn
  MONSTER_ATTACKS = {
    'slime' : [ 'leap', 'leap' ],
    'zombie' : [ 'jump', 'arm' ],
    'demon_eye' : [ 'from front', 'from side' ],
    'cave_bat' : [ 'missed', 'low attack', 'high attack' ],
    'skeleton' : [ 'charge', 'jump', 'bone', 'bone upward' ],
    'undead_miner' : [ 'charge', 'grenade' ],
    'harpy' : [ 'from top', 'from front', 'from side' ],
    'tim' : [ 'normal spell', 'dual spell', 'circular spell', 'teleports behind you' ]
  }

  # The result of each monster turn
  # Format: [ Text + HP Lost + Modifiers ]
  M_TURN_RESULTS = {
    'slime : b : leap' : [ 'The enemy leaped onto you, but you moved out of the way.' ],
    'slime : f : leap' : [ 'The enemy leaped onto you, but you moved out of the way.' ],
    'slime : s : leap' : [ 'The enemy leaped onto you.', ( 8, 20 ) ],
    'slime : ! : leap' : [ 'The enemy leaped onto you.', ( 8, 20 ) ],
    'zombie : b : jump' : [ 'You moved backward, and the enemy jumped into you.', ( 12, 20 ) ],
    'zombie : b : arm' : [ 'The enemy swung its arm, but you moved out of its reach.' ],
    'zombie : f : jump' : [ 'You run past the enemy while it was jumping.' ],
    'zombie : f : arm' : [ 'The enemy swing its arm, and you walked into it.', ( 6, 12 ) ],
    'zombie : j : jump' : [ 'You and the enemy both jumped forward.', ( 10, 16 ) ],
    'zombie : j : arm' : [ 'The enemy swung its arm, but you jumped over it.' ],
    'zombie : ! : jump' : [ 'The enemy jumped onto you.', ( 12, 20 ) ],
    'zombie : ! : arm' : [ 'The enemy swing its arm at you.', ( 6, 12 ) ],
    'demon_eye : b : from front' : [ 'You moved backward, and the enemy flew into you.', ( 10, 18 ) ],
    'demon_eye : b : from side' : [ 'The enemy flew in from the side, and you dodged its attack.' ],
    'demon_eye : r : from front' : [ 'The enemy flew in from the front, and you dodged its attack.' ],
    'demon_eye : r : from side' : [ 'You moved rightward, and the enemy flew into you.', ( 10, 18 ) ],
    'demon_eye : l : from front' : [ 'The enemy flew in from the front, and you dodged its attack.' ],
    'demon_eye : l : from side' : [ 'You moved leftward, and the enemy flew into you.', ( 10, 18 ) ],
    'demon_eye : j : from front' : [ 'chance', ( ( 0, 49, 'dodge' ), ( 50, 99, 'fail' ) ) ],
    'demon_eye : j : from front : dodge' : [ 'The enemy flew in from the front, and you jumped over it.' ],
    'demon_eye : j : from front : fail' : [ 'The enemy flew in from the front, and you didn\'t jump over it in time.' ],
    'demon_eye : j : from side' : [ 'chance', ( ( 0, 49, 'dodge' ), ( 50, 99, 'fail' ) ) ],
    'demon_eye : j : from side : dodge' : [ 'The enemy flew in from the side, and you jumped over it.' ],
    'demon_eye : j : from side : fail' : [ 'The enemy flew in from the side, and you didn\'t jump over it in time.', ( 10, 18 ) ],
    'demon_eye : ! : from front' : [ 'The enemy flew into you.', ( 10, 18 ) ],
    'demon_eye : ! : from side' : [ 'The enemy flew into you.', ( 10, 18 ) ],
    'cave_bat : j : missed' : [ 'The enemy flew towards you, but it missed.' ],
    'cave_bat : j : low attack' : [ 'You jumped, and the enemy flew under you.' ],
    'cave_bat : j : high attack' : [ 'The enemy flew over you, and you jumped into it.', ( 10, 18 ) ],
    'cave_bat : s : missed' : [ 'The enemy flew towards you, but it missed.' ],
    'cave_bat : s : low attack' : [ 'The enemy flew into you.', ( 10, 18 ) ],
    'cave_bat : s : high attack' : [ 'The enemy flew over you.' ],
    'cave_bat : ! : missed' : [ 'The enemy flew into you.', ( 10, 18 ) ],
    'cave_bat : ! : low attack' : [ 'The enemy flew into you.', ( 10, 18 ) ],
    'cave_bat : ! : high attack' : [ 'The enemy flew over you.' ],
    'skeleton : j : charge' : [ 'The enemy charged toward you, and you jumped over it.' ],
    'skeleton : j : jump' : [ 'You and the enemy both jumped towards each other.', ( 18, 28 ) ],
    'skeleton : j : bone' : [ 'The enemy threw a bone at you, and you jumped over it.' ],
    'skeleton : j : bone upward' : [ 'The enemy threw a bone upward, and you jumped into it.', ( 18, 28 ) ],
    'skeleton : b : charge' : [ 'The enemy charged toward you, and you didn\'t back up far enough.', ( 20, 40 ) ],
    'skeleton : b : jump' : [ 'The enemy tried to jump on you, but you moved backwards.' ],
    'skeleton : b : bone' : [ 'The enemy threw a bone, and it hit you.', ( 8, 18 ) ],
    'skeleton : b : bone upward' : [ 'The enemy threw a bone upward, and it missed you.' ],
    'skeleton : ! : charge' : [ 'The enemy charged toward you, and you didn\'t back up far enough.', ( 20, 40 ) ],
    'skeleton : ! : jump' : [ 'The enemy tried to jump on you, but you moved backwards.' ],
    'skeleton : ! : bone' : [ 'The enemy threw a bone, and it hit you.', ( 8, 18 ) ],
    'skeleton : ! : bone upward' : [ 'The enemy threw a bone upward, and it missed you.' ],
    'undead_miner : j : charge' : [ 'The enemy charged towards you, but you jumped over it.' ],
    'undead_miner : j : grenade' : [ 'You jumped, but the enemy arced a grenade at you.', ( 24, 48 ) ],
    'undead_miner : f : charge' : [ 'The enemy charged towards you, and you ran into it.', ( 14, 28 ) ],
    'undead_miner : f : grenade' : [ 'The enemy arced a grenade at you, but you stepped forward out of the way.' ],
    'undead_miner : s : charge' : [ 'The enemy charged towards you, and you didn\'t move out of its way.', ( 14, 28 ) ],
    'undead_miner : s : grenade' : [ 'The enemy arced a grenade at you, and you didn\'t move out of the way.', ( 14, 28 ) ],
    'undead_miner : ! : charge' : [ 'The enemy charged towards you.', ( 14, 28 ) ],
    'undead_miner : ! : grenade' : [ 'The enemy arced a grenade at you.', ( 14, 28 ) ],
    'harpy : j : from top' : [ 'A feather was shot downward at you, and you jumped into it.', ( 24, 36 ) ],
    'harpy : j : from front' : [ 'A feather was shot backward at you, and you jumped over it.' ],
    'harpy : j : from side' : [ 'A feather was shot rightward at you, and you jumped over it.' ],
    'harpy : b : from top' : [ 'A feather was shot downward at you, and you moved out of the way.' ],
    'harpy : b : from front' : [ 'A feather was shot backward at you, and you didn\'t move out of the way.', ( 24, 36 ) ],
    'harpy : b : from side' : [ 'A feather was shot rightward at you, and you moved out of the way.' ],
    'harpy : s : from top' : [ 'A feather was shot downward at you, and you moved out of the way.' ],
    'harpy : s : from front' : [ 'A feather was shot backward at you, and you moved out of the way.' ],
    'harpy : s : from side' : [ 'A feather was shot rightward at you, and you didn\'t move out of the way.', ( 24, 36 ) ],
    'harpy : ! : from top' : [ 'A feather was shot downward at you.', ( 24, 36 ) ],
    'harpy : ! : from front' : [ 'A feather was shot backward at you.', ( 24, 36 ) ],
    'harpy : ! : from side' : [ 'A feather was shot rightward at you.', ( 24, 36 ) ],
    'tim : s : normal spell' : [ 'The enemy shot a spell at you, and you didn\'t move out of the way.', ( 30, 45 ) ],
    'tim : s : dual spell' : [ 'The enemy shot a dual spell to your right and left.' ],
    'tim : s : circular spell' : [ 'The enemy shot a circular spell around you.' ],
    'tim : s : teleports behind you' : [ 'The enemy teleported behind you, and you didn\'t move out of its way.', ( 15, 25 ) ],
    'tim : j : normal spell' : [ 'The enemy shot a spell at you, and you jumped over it.' ],
    'tim : j : dual spell' : [ 'The enemy shot a dual spell to your right and left.' ],
    'tim : j : circular spell' : [ 'The enemy shot a circular spell, and you jumped into it.', ( 30, 45 ) ],
    'tim : j : teleports behind you' : [ 'The enemy teleported behind you, and you fell onto it.', ( 15, 25 ) ],
    'tim : r : normal spell' : [ 'The enemy shot a spell at you, and you moved to its right.' ],
    'tim : r : dual spell' : [ 'The enemy shot a dual spell, and you moved rightward into it.', ( 30, 45 ) ],
    'tim : r : circular spell' : [ 'The enemy shot a circular spell, and you stepped rightward into it.', ( 30, 45 ) ],
    'tim : r : teleports behind you' : [ 'The enemy teleported behind you, and you moved to its right.' ],
    'tim : l : normal spell' : [ 'The enemy shot a spell at you, and you moved to its left.' ],
    'tim : l : dual spell' : [ 'The enemy shot a dual spell, and you moved leftward into it.', ( 30, 45 ) ],
    'tim : l : circular spell' : [ 'The enemy shot a circular spell, and you stepped leftward into it.', ( 30, 45 ) ],
    'tim : l : teleports behind you' : [ 'The enemy teleported behind you, and you moved to its right.' ],
    'tim : ! : normal spell' : [ 'The enemy shot a spell at you.', ( 30, 45 ) ],
    'tim : ! : dual spell' : [ 'The enemy shot a dual spell to your right and left.' ],
    'tim : ! : circular spell' : [ 'The enemy shot a circular spell around you.' ],
    'tim : ! : teleports behind you' : [ 'The enemy teleported behind you.', ( 15, 25 ) ]
  }

  # Determines the chances for each item drop
  # -1 in index 0 means 1 in (index 1) chance of dropping
  # Otherwise, the two numbers form the range of the amount that will drop
  DROPS = {
    'slime': [ ( 1, 4, I_GEL ), ( 1, 1, I_HEALTH_POTION ) ],
    'zombie': [ ( -1, 15, I_SHACKLE ), ( 1, 1, I_HEALTH_POTION ) ],
    'demon_eye': [ ( -1, 2, I_LENS ), ( 1, 2, I_HEALTH_POTION ) ],
    'cave_bat': [ ( 1, 2, I_HEALTH_POTION ) ],
    'skeleton': [ ( 1, 2, I_GOLD_BAR ), ( 2, 2, I_HEALTH_POTION ) ],
    'undead_miner': [ ( 4, 10, I_GRENADE ), ( 2, 3, I_HEALTH_POTION ) ],
    'harpy': [ ( 1, 3, I_FEATHER ), ( 2, 3, I_HEALTH_POTION ) ],
    'tim': [ ( -1, 2, I_MAGIC_STAFF ), ( 2, 5, I_HEALTH_POTION ) ]
  }

  def __init__( self, name ):

    self.hp = self.HEALTHS[ name ]
    self.name = name if ( name in self.TYPES ) else 'slime'

    # The next move, first move, and current move are used for calculating the next move ID
    self.move = random.randint( 0, len( self.MONSTER_DODGES[ name ] ) - 1 )
    self.move_0 = self.move
    self.move_c = 0

    self.charged = False

    if self.name == 'zombie':
      self.move_c = 1 if self.move == 0 else 0

    if self.name == 'cave_bat':
      self.move_c = self.move

  # Deals damage to self, allowing a random range and multiplier to be used
  def damage( self, a, b, method = '', entity = 'self' ):

    global g_hp

    amount = random.randint( a, b )
    if amount == 0:
      return 0

    # multiply damage based on stronger weapons/armor
    if method == 's':
      amount *= ( 1, 1.5, 1.8, 2.2, 2.5 )[ ( 'copper', 'iron', 'silver', 'gold', 'staff' ).index( self.weapon_melee ) ]
    if method == 's' and self.weapon_melee == 'staff' and random.randint( 0, 2 ) == 0:
      amount *= 3
    if method == 'b':
      amount *= ( 1, 1.6, 1.9, 2.5 )[ ( 'wood', 'iron', 'silver', 'gold' ).index( self.weapon_bow[0] ) ]
    if method == 'b':
      amount *= ( 1, 2 )[ ( 'arrow', 'flame_arrow' ).index( self.weapon_bow[1] ) ]
    if entity == 'you':
      amount *= ( 1, 0.7, 0.45, 0.15 )[ ( 'none', 'iron', 'silver', 'gold' ).index( self.armor ) ]
    if entity == 'you':
      amount *= ( 1.5 if self.charged else 1 )

    amount = int( amount )

    if entity == 'self':
      self.hp -= amount
    else:
      g_hp -= amount
    return amount

  def update_stats( self ):

    # Determine sword
    self.weapon_melee = 'none'
    if update_inv( I_C_SSWORD, 0, mode = 't' ) > 0:
      self.weapon_melee = 'copper'
    if update_inv( I_I_SWORD, 0, mode = 't' ) > 0:
      self.weapon_melee = 'iron'
    if update_inv( I_S_SWORD, 0, mode = 't' ) > 0:
      self.weapon_melee = 'silver'
    if update_inv( I_G_SWORD, 0, mode = 't' ) > 0:
      self.weapon_melee = 'gold'
    if update_inv( I_MAGIC_STAFF, 0, mode = 't' ) > 0:
      self.weapon_melee = 'staff'

    # Determine bow
    self.weapon_bow = [ 'none', 'none' ]
    if update_inv( I_W_BOW, 0, mode = 't' ) > 0:
      self.weapon_bow[0] = 'wood'
    if update_inv( I_I_BOW, 0, mode = 't' ) > 0:
      self.weapon_bow[0] = 'iron'
    if update_inv( I_S_BOW, 0, mode = 't' ) > 0:
      self.weapon_bow[0] = 'silver'
    if update_inv( I_G_BOW, 0, mode = 't' ) > 0:
      self.weapon_bow[0] = 'gold'
    if update_inv( I_ARROW, 0, mode = 't' ) > 0:
      self.weapon_bow[1] = 'arrow'
    if update_inv( I_F_ARROW, 0, mode = 't' ) > 0:
      self.weapon_bow[1] = 'flame_arrow'

    # Determine grenade
    self.weapon_grenade = 'none'
    if update_inv( I_GRENADE, 0, mode = 't' ) > 0: self.weapon_grenade = 'grenade'

    # Determine armor
    self.armor = 'none'
    if update_inv( I_I_ARMOR, 0, mode = 't' ) > 0: self.armor = 'iron'
    if update_inv( I_S_ARMOR, 0, mode = 't' ) > 0: self.armor = 'silver'
    if update_inv( I_G_ARMOR, 0, mode = 't' ) > 0: self.armor = 'gold'

  def get_options( self, player_turn, should_print = True ):

    self.update_stats() # Query weapon, armor, etc.

    options_list = []

    for s in ( self.PLAYER_ATTACKS[ self.name ] if player_turn else self.PLAYER_DODGES[ self.name ] ):

      # Throw out weapon choice if the player doesn't have the required item
      if len( s ) > 2 and s[2] == 's' and self.weapon_melee == 'none':
        continue
      if len( s ) > 2 and s[2] == 'b' and self.weapon_bow[0] == 'none':
        continue
      if len( s ) > 2 and s[2] == 'b' and self.weapon_bow[1] == 'none':
        continue
      if len( s ) > 2 and s[2] == 'g' and self.weapon_grenade == 'none':
        continue

      # Format print message based on keycode and items required for it
      if should_print and s[0] != 'n':

        suffix = ''
        if len( s ) > 2 and s[2] == 's':
          suffix += f"({ ( 'Copper Shortsword', 'Iron Broadsword', 'Silver Broadsword', 'Gold Broadsword', 'Magic Staff' )[ ( 'copper', 'iron', 'silver', 'gold', 'staff' ).index( self.weapon_melee ) ] })"
        if len( s ) > 2 and s[2] == 'b':
          suffix += f"({ ( 'Bow', 'Iron Bow', 'Silver Bow', 'Gold Bow' )[ ( 'wood', 'iron', 'silver', 'gold' ).index( self.weapon_bow[0] ) ] } + "
          suffix += f"{ ( 'Arrow', 'Flaming Arrow' )[ ( 'arrow', 'flame_arrow' ).index( self.weapon_bow[1] ) ] } x"
          suffix += f"{ update_inv( ( I_ARROW, I_F_ARROW )[ ( 'arrow', 'flame_arrow' ).index( self.weapon_bow[1] ) ], 0, mode = 't' ) })"
        if len( s ) > 2 and s[2] == 'g':
          suffix += f"(Grenade x{ update_inv( I_GRENADE, 0, mode = 't' ) })"

        print( f'[{ s[0].upper() }] { s[1] } { suffix }' )
      options_list.append( s[0].lower() )

    return options_list
  
  def turn( self, p, player_turn ):

    # Allows attacks to do the proper amount of damage
    self.update_stats()

    # Get result of action [text, damage, modifiers]
    if player_turn:
      result = self.P_TURN_RESULTS[ f'{ self.name } : { p } : { self.MONSTER_DODGES[ self.name ][ self.move ] }' ]
    else:
      result = self.M_TURN_RESULTS[ f'{ self.name } : { p } : { self.MONSTER_ATTACKS[ self.name ][ self.move ] }' ]

    # Attacks can have different outcomes by using [ chance, [ [ low_range, high_range, attack_name ], ... ] ]
    # This code evaulates that chance, and chooses an actual result based on it
    if result[0] == 'chance':
      temp_rand = random.randint( 0, 99 )
      for i in result[1]:
        if ( i[0] <= temp_rand <= i[1] ):
          if player_turn:
            result = self.P_TURN_RESULTS[ f'{ self.name } : { p } : { self.MONSTER_DODGES[ self.name ][ self.move ] } : { i[2] }' ]
          else:
            result = self.M_TURN_RESULTS[ f'{ self.name } : { p } : { self.MONSTER_ATTACKS[ self.name ][ self.move ] } : { i[2] }' ]
          break
      else:
        print( "ERROR: Random values don't add up to 100." )

    # Fill in default values for the result
    if len( result ) == 1: result.append( 0 )
    if isinstance( result[1], int ):
      result[1] = ( result[1], result[1] )
    if len( result ) == 2: result.append( 'e' if player_turn else 'p' )

    # Damage method determines what gear the player used, and therefore, how much damage the entity should take
    if player_turn:
      dmg_method = [ i for i in self.PLAYER_ATTACKS[ self.name ] if i[0] == p ][0]
    elif p != '!':
      dmg_method = [ i for i in self.PLAYER_DODGES[ self.name ] if i[0] == p ][0]
    else:
      dmg_method = []
    dmg_method = ( '' if len( dmg_method ) < 3 else dmg_method[2] )

    # Subtract HP
    dmg_amount = self.damage( *result[1], entity = 'self' if 'e' in result[2] else 'you', method = dmg_method )

    # Remove items
    if dmg_method == 'b':
      update_inv( I_ARROW if self.weapon_bow[1] == 'arrow' else I_F_ARROW, 1, 'r' )
    elif dmg_method == 'g':
      update_inv( I_GRENADE, 1, 'r' )

    # Display text
    print( '[!] ' + result[0] )
    if dmg_amount == 0:
      print( f"[*] { 'Enemy' if result[2] == 'e' else 'You' }: NO DAMAGE"  )
    elif dmg_amount != 0:
      print( f"[*] { 'Enemy' if result[2] == 'e' else 'You' }: -{ dmg_amount } HP"  )

    # Change HP/Display text for special moves
    self.charged = ( 'c' in result[2] )
    if self.charged:
      print( '[*] Enemy: +50% DMG next turn' )
    if 'h' in result[2]:
      print( f'[*] Enemy: +{ -self.damage( -10, -1 ) } HP' )

    # Remove item

    # Check if fight is over
    self.hp_check()

    # Advance move
    self.advance_move()

  # Checks if either entity has died
  def hp_check( self ):

    # If player won
    if self.hp <= 0:
      print_line()
      print( f"[!] { self.name.replace( '_', ' ' ).title() } was killed." )
      self.give_items()
      input( '[!] Press enter to exit the fight. ' )
      goto_room( room_scene )

    # If player lost
    if g_hp <= 0:
      print_line()
      print( f"[!] { self.name.replace( '_', ' ' ).title() } won." )
      input( '[!] Press enter to exit the fight. ' )
      goto_room( room_death )

  def give_items( self ):

    # Stores all the items the player will receive
    temp_items = []
    
    # Loop through 
    for i in self.DROPS[ self.name ]:

      # Chance drop
      if i[0] == -1 and random.randint( 1, i[1] ) == 1:
        temp_items.append( ( i[2], 1 ) )

      # Range drop
      else:
        temp_items.append( ( i[2], random.randint( i[0], i[1] ) ) )

    # Print different messages for 0, 1, 2, and 3+ items
    if len( temp_items ) == 0:
      print( '[!] You received nothing.' )

    if len( temp_items ) == 1:
      print( f'[!] You received { temp_items[0][1] }x { item_meta( temp_items[0][0] ) }.' )
      update_inv( temp_items[0][0], temp_items[0][1] )

    elif len( temp_items ) == 2:
      print( f'[!] You received { temp_items[0][1] }x { item_meta( temp_items[0][0] ) } ', end = '' )
      print( f'and { temp_items[1][1] }x { item_meta( temp_items[1][0] ) }.' )
      update_inv( temp_items[0][0], temp_items[0][1] )
      update_inv( temp_items[1][0], temp_items[1][1] )

    else:
      print( f'[!] You received { temp_items[0][1] }x { item_meta( temp_items[0][0] ) }, ', end = '' )
      update_inv( temp_items[0][0], temp_items[0][1] )
      for i in temp_items[1:-1]:
        print( f'{ i[1] }x { item_meta( i[0] ) }, ', end = '' )
        update_inv( i[0], i[1] )
      print( f'and { temp_items[-1][1] }x { item_meta( temp_items[-1][0] ) }.' )
      update_inv( temp_items[-1][0], temp_items[-1][1] )

  def advance_move( self ):

    # If you're trying to find each enemy's attack pattern,
    # this is where you want to look
    if self.name == 'slime':
      self.move_c += 1
      if self.move_c % 2 == 0:
        self.move = ( 1 - self.move )

    elif self.name == 'zombie':
      self.move_c += 1
      if self.move_c % 3 == 0:
        self.move = 1 - self.move

    elif self.name == 'demon_eye':
      self.move_c += 1
      self.move = ( self.move_0 ) if ( self.move_c % 6 in ( 0, 2, 3 ) ) else ( 1 - self.move_0 )

    elif self.name == 'cave_bat':
      self.move_c += ( 1 if self.move_0 != 1 else -1 )
      self.move = self.move_c % 3

    elif self.name == 'skeleton':
      self.move_c += 1
      self.move = ( ( 0, 1, 2, 3, 3, 2, 1 )[ self.move_c % 7 ] + self.move_0 ) % 4

    elif self.name == 'undead_miner':
      self.move_c += 1
      self.move = ( self.move_0 ) if ( self.move_c % 5 == 0 ) else ( 1 - self.move_0 )
    
    elif self.name == 'harpy':
      self.move = random.choice( [ m for m in [ 0, 1, 2 ] if m != self.move ] )

    elif self.name == 'tim':
      self.move_c += 1
      self.move = ( self.move + 1 + ( 1 if self.move_c % ( 2 * ( self.move_0 + 1 ) ) == 0 else 0 ) ) % 4

# Eye of Cthulhu
class EyeOfCthulhu( Monster ):

  # The player's options for each player turn
  # Format: [ Letter ID, Action Name, Requirements, Hit Angles ]
  PLAYER_ATTACKS = [ [ 'j', 'Jump', '', -1 ], [ 's', 'Swing sword', 's', 2 ], [ 'r', 'Shoot rightward', 'b', 0 ], [ 'l', 'Shoot leftward', 'b', 4 ],
  [ 'd', 'Shoot downward', 'b', 6 ], [ 'x', 'Throw grenade rightward', 'g', ( 7, 0 ) ], [ 'y', 'Throw grenade leftward', 'g', ( 4, 5 ) ],
  [ 'z', 'Throw grenade downward', 'g', 6 ] ]

  # The player's options for each monster turn
  # Format: [ Letter ID, Action Name, Hit Angles ]
  PLAYER_DODGES = [ [ 'j', 'Jump', '', 2 ], [ 'r', 'Dodge rightward', '', 0 ], [ 'l', 'Dodge leftward', '', 4 ],
  [ 'x', 'Jump and dodge rightward', 1 ], [ 'z', 'Jump and dodge leftward', 3 ] ]

  # Determines the damage each weapon does
  # (Can't have it defined for each possible outcome like in the base class b/c
  # there's too many possible outcomes, so it's only defined for each weapon type)
  DAMAGE_RANGES = { 's': ( 8, 16 ), 'b': ( 6, 12 ), 'g': ( 24, 48 ) }

  def __init__( self ):

    self.hp = 1024

    self.move = [ random.randint( 0, 3 ), random.choice( list( 'abc' ) ) ]
    self.move_0 = self.move
    self.move_c = 0
    self.stage = 1

    self.charged = False

  def get_options( self, player_turn, should_print = True ):

    self.update_stats() # Query weapon, armor, etc.

    options_list = []
    for s in ( self.PLAYER_ATTACKS if player_turn else self.PLAYER_DODGES ):

      # Throw out weapon choice if the player doesn't have the required item
      if len( s ) > 2 and s[2] == 's' and self.weapon_melee == 'none':
        continue
      if len( s ) > 2 and s[2] == 'b' and self.weapon_bow[0] == 'none':
        continue
      if len( s ) > 2 and s[2] == 'b' and self.weapon_bow[1] == 'none':
        continue
      if len( s ) > 2 and s[2] == 'g' and self.weapon_grenade == 'none':
        continue

      # Format print message based on keycode and items required for it
      if should_print:

        suffix = ''
        if len( s ) > 2 and s[2] == 's':
          suffix += f"({ ( 'Copper Shortsword', 'Iron Broadsword', 'Silver Broadsword', 'Gold Broadsword', 'Magic Staff' )[ ( 'copper', 'iron', 'silver', 'gold', 'staff' ).index( self.weapon_melee ) ] })"
        if len( s ) > 2 and s[2] == 'b':
          suffix += f"({ ( 'Bow', 'Iron Bow', 'Silver Bow', 'Gold Bow' )[ ( 'wood', 'iron', 'silver', 'gold' ).index( self.weapon_bow[0] ) ] } + "
          suffix += f"{ ( 'Arrow', 'Flaming Arrow' )[ ( 'arrow', 'flame_arrow' ).index( self.weapon_bow[1] ) ] } x"
          suffix += f"{ update_inv( ( I_ARROW, I_F_ARROW )[ ( 'arrow', 'flame_arrow' ).index( self.weapon_bow[1] ) ], 0, mode = 't' ) })"
        if len( s ) > 2 and s[2] == 'g':
          suffix += f"(Grenade x{ update_inv( I_GRENADE, 0, mode = 't' ) })"

        print( f'[{ s[0].upper() }] { s[1] } { suffix }' )
      options_list.append( s[0].lower() )

    if player_turn and update_inv( I_HEALTH_POTION, 0, 't' ) > 0:
      print( '[H] Drink health potion' )
      options_list.append( 'h' )

    return options_list
  
  def turn( self, p, player_turn ):

    global g_hp

    if player_turn:
      p = p.split( ' ' )

    # Allows attacks to do the proper amount of damage
    self.update_stats()

    # Decide the angles for each move
    # Angles are as follows:
    # 3  2  1
    # 4  P  0     (P = Player's start pos)
    # 5  6  7

    print( self.move )

    if player_turn:

      # Decide the eye's position
      angle = ( self.move[0] * 2 + ( 1, 3, 0 )[ list( 'abc' ).index( self.move[1] ) ] ) % 8

      # The player gets 3 turns if they're attacking
      # Otherwise the enemy gets 1 or 2 turns depending on its stage
      for i in range( 3 ):

        # Drink health potion
        if p[i] == 'h':

          # Damage method determines what gear the player used, and therefore, how much damage the entity should take
          dmg_method = ''
          dmg_method_text = ''

          # Make sure player has a health potion
          has_item = update_inv( I_HEALTH_POTION, 0, 't' ) > 0

          # Remove items
          update_inv( I_HEALTH_POTION, 1, 'r' )

          # Determine the string to print regarding the eye's direction
          dmg_amount = 0
          temp_dir = ( 'to the right', 'upward and rightward', 'upward', 'upward and leftward', 'to the left',
            'leftward and downward', 'downward', 'rightward and downward' )[ angle ]
          attack_angles = [ -2 ]

        else:

          # Damage method determines what gear the player used, and therefore, how much damage the entity should take
          dmg_method = [ j for j in self.PLAYER_ATTACKS if j[0] == p[i] ][0]
          dmg_method = ( '' if len( dmg_method ) < 3 else dmg_method[2] )
          dmg_method_text = ( 'swung your sword', 'shot an arrow', 'threw a grenade', '' )[ ( 's', 'b', 'g', '' ).index( dmg_method ) ]

          # Remove items
          if dmg_method == 'b':
            update_inv( I_ARROW if self.weapon_bow[1] == 'arrow' else I_F_ARROW, 1, 'r' )
          elif dmg_method == 'g':
            update_inv( I_GRENADE, 1, 'r' )

          # Make sure player has their requred item
          has_item = True
          if dmg_method == 's' and self.weapon_melee == 'none':
            has_item = False
          if dmg_method == 'b' and 'none' in self.weapon_bow:
            has_item = False
          if dmg_method == 'g' and self.weapon_grenade == 'none':
            has_item = False

          # Get result of action
          dmg_amount = 0
            
          # Determine the string to print regarding the eye's direction
          # As well as at which angle the player is attacking
          temp_dir = ( 'to the right', 'upward and rightward', 'upward', 'upward and leftward', 'to the left',
            'leftward and downward', 'downward', 'righward and downward' )[ angle ]
          attack_angles = [ j for j in self.PLAYER_ATTACKS if j[0] == p[i] ][0][3]
          if isinstance( attack_angles, int ):
            attack_angles = [ attack_angles ]
          else:
            attack_angles = list( attack_angles )

          # Add height to attack if the player jumped
          if i > 0 and p[ i - 1 ] == 'j':
            for j in range( len( attack_angles ) ):
              if attack_angles[j] in ( 7, 0, 4, 5 ):
                attack_angles[j] = ( 0, 1, 3, 4 )[ ( 7, 0, 4, 5 ).index( attack_angles[j] ) ]

        # Firstly, print which direction the enemy went
        if i == 0:
          print( f'[!] The enemy flew { temp_dir }.' )

        # Then print the effect of the player's attack
        if -1 in attack_angles:
          print( '[!] You jumped, allowing you to be higher up for the next attack.' )
        elif -2 in attack_angles and has_item:
          print( '[!] You used a healing potion.' )
          print( f'[*] YOU: +{ min( g_hp + 100, g_hp_max ) - g_hp } HP' )
          g_hp = min( g_hp + 100, g_hp_max )
        elif -2 in attack_angles and not has_item:
          print( f'[!] You ran out of healing potions.' )
        elif angle in attack_angles and has_item:
          print( f'[!] You { dmg_method_text } and hit the enemy.' )
          dmg_amount = self.damage( *self.DAMAGE_RANGES[ dmg_method ], entity = 'self', method = dmg_method )
        elif has_item:
          print( f'[!] You { dmg_method_text }, but you missed the enemy.' )
        else:
          print( f'[!] You ran out of the weapon necessary to perform this attack.' )

        # Display text
        if dmg_amount == 0:
          print( f"[*] Boss: NO DAMAGE"  )
        elif dmg_amount != 0:
          print( f"[*] Boss: -{ dmg_amount } HP" )

        # Check if fight is over
        self.hp_check()

        # Wait
        time.sleep( 0.5 )

    else:

      # Attack twice if in second stage
      for i in range( self.stage ):

        # Decide the eye's charge direction (angle = the start angle; charges to the opposite angle)
        angle = ( self.move[0] + i + 1 + list( 'abc' ).index( self.move[1] ) ) % 4

        # Damage method determines what gear the player used, and therefore, how much damage the entity should take
        dmg_method = [ j for j in self.PLAYER_DODGES if j[0] == p ][0]
        dmg_method = ( '' if len( dmg_method ) < 3 else dmg_method[2] )

        # Get result of action
        dmg_amount = 0

        temp_dir = 'from the ' + ( 'right', 'upper-right', 'top', 'upper-left', 'left', 'bottom-left', 'bottom', 'bottom-right' )[ angle + random.choice( ( 0, 4 ) ) ]
        dodge_angle = [ j for j in self.PLAYER_DODGES if j[0] == p ][0][3]
        if dodge_angle >= 4:
          dodge_angle -= 1

        # Hit the player if they're in range of the start or finish position
        if dodge_angle == angle:
          print( f'[!] The enemy charged { temp_dir }, and it hit you.' )
          dmg_amount = self.damage( 40, 100, entity = 'you', method = dmg_method )
        else:
          print( f'[!] The enemy charged { temp_dir }, and you dodged its attack.' )

        # Display text
        if dmg_amount == 0:
          print( f"[*] You: NO DAMAGE"  )
        elif dmg_amount != 0:
          print( f"[*] You: -{ dmg_amount } HP" )

        # Check if fight is over
        self.hp_check()

        # Wait
        time.sleep( 0.5 )

    # Transform stage if necessary
    if self.stage == 1 and self.hp <= 512:
      self.stage = 2
      time.sleep( 0.6 )
      print( '[!!!] The enemy progressed to Stage 2!' )

    # Advance move
    self.advance_move()

  # Checks if either entity has died
  def hp_check( self ):

    if self.hp <= 0:
      print_line()
      for c in 'Eye of Cthulhu has been defeated!':
        print( c, end = '', flush = True )
        time.sleep( 0.065 )
      time.sleep( 2 )
      print( '[!] You received 1x Trophy.' )
      update_inv( I_TROPHY, 1 )
      input( '[!] Press enter to exit the fight. ' )
      goto_room( room_scene )

    if g_hp <= 0:
      print_line()
      print( f"[!] Eye of Cthulhu won." )
      input( '[!] Press enter to exit the fight. ' )
      goto_room( room_death )

  def advance_move( self ):

    self.move_c += 1
    self.move[0] = ( self.move[0] + ( 2 if self.move_c % 2 else 3 ) ) % 4
    self.move[1] = list( 'cab' )[ list( 'abc' ).index( self.move[1] ) ]

# Switches rooms
def goto_room( room, arg = '' ):
  raise MoveException( room, arg )

# Prints line
def print_line():
  print( '- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -' )

# Prints the worldgen progress
# I don't think it's important to explain what the arguments do
def print_progress( prog, div_this, div_total, s ):

  prog += ( 1 / div_this ) * ( div_total / 2 ) # Add to progress
  suffix = f'{ int( prog * 2 ) }% ' if prog < 50 else 'Done!' # Create a suffix that contains the progress/current task
  if prog < 50:
    suffix += f'({ s })'
  if SHOW_PROG:
    print( '[' + ( '|' * int( prog ) ) + ( '-' * ( 50 - int( prog ) ) ) + ']  ' + suffix + ( ' ' * 30 ), end = '\r' )
  return prog

# A function used for the top of the world
# (A really interesting bug came up when I was integrating this function into worldgen,
# so I may or may not make a supplemental video dedicated to explaining it)
def noise_top( x, seed ):

  next_seed = random.randint( 1, 10 ** 12 )
  random.seed( seed )
  sine = 0
  for i in range( 12 ):
    sine += random.randrange( 3, 12 ) * sin( x / random.randrange( 6, 24 ) - random.randrange( 10, 80 ) )
  random.seed( next_seed )
  return sine / 4;

# Allow time to move forward a little bit
# Includes gravity, monster movements, etc.
def tick( nofall = False ):

  global g_pos, g_hp, g_hp_max, g_enemy_timer

  # Move player 5 blocks downward
  if not nofall:
    for i in range( 5 ):

      # Move
      if g_pos.y + 1 < g_world_size.y and get_tile( g_pos.copy().a( 0, 1 ) ) in [ i for i in AIR_BLOCKS if i not in PLATFORM_BLOCKS ]:
        g_pos.y += 1

  # Start fight
  g_enemy_timer -= 1
  if g_enemy_timer <= 0:
    g_enemy_timer = random.randint( 20, 35 )
    try_fight()

  # Regen health
  g_hp = min( g_hp + 1, g_hp_max )

  data_save()

# Modify the inventory
# Modes = pickup, remove, or set
def update_inv( item_id, amount, mode = 'p', slot = 0, allow_stash = True ):

  global g_items, g_items_extra

  inv_keys = [] # Holds the 'keys' of the inventory

  # Before doing anything else, make sure everything is properly stacked
  for i in range( 16 ):

    # Reset ID of anything with count 0
    if g_items[i][1] == 0:
      g_items[i][0] = 0
    inv_keys.append( g_items[i][0] )

  for i in range( len( inv_keys ) ):

    # If this is a duplicate, and it isn't the first slot with this item,
    # then add count to first slot with this item
    if inv_keys[i] != 0 and inv_keys.count( inv_keys[i] ) != 1 and inv_keys.index( inv_keys[i] ) != i:
      g_items[ inv_keys.index( inv_keys[i] ) ][1] += g_items[i][1]
      g_items[i] = [ 0, 0 ]

  # Pickup mode
  if mode == 'p':

    # First try to stack (MAKE SURE SLOT ISN'T EMPTY)
    for i in range( 16 ):
      if g_items[i][0] == item_id and g_items[i][1] > 0:
        g_items[i][1] += amount
        data_save()
        return True

    else:

      # Then find empty slot
      for i in range( 16 ):
        if g_items[i][1] == 0:
          g_items[i][0] = item_id
          g_items[i][1] = amount
          data_save()
          return True

    # If stash is allowed
    if allow_stash:
      g_items_extra.append( [ item_id, amount ] )
    return False

  # Removal mode
  # (Returns the # of items that were able to be removed)
  elif mode == 'r':

    # Try to remove
    for i in range( 16 ):
      if g_items[i][0] == item_id:
        if g_items[i][1] >= amount:

          g_items[i][1] -= amount
          data_save()
          return amount

        elif g_items[i][1] > 0:

          old_value = g_items[i][1]
          g_items[i][1] = 0
          data_save()
          return old_value

    # Failed to remove
    return 0

  # Set mode
  # Sets the specified slot to the provided item and amount
  elif mode == 's':

    # Check range
    if ( 0 <= slot < 16 ):

      # Modify
      g_items[ slot ][0] = item_id
      g_items[ slot ][1] = amount

  # Test mode
  # Tests how much of an item is present in the inventory
  elif mode == 't':

    for i in range( 16 ):
      if g_items[i][0] == item_id:
        return g_items[i][1]

    return 0

  # Update character file
  data_save()

# Create new (empty) chest
def chest_create( x, y ):

  global g_tile_special

  g_tile_special[ f'{ x } : { y }' ] = {}
  for i in range( 10 ):
    g_tile_special[ f'{ x } : { y }' ][ f'slot{ i }' ] = '0:0'

def chest_modify( x, y, item_id, amount, mode = 'i' ):

  global g_tile_special
  
  # Insert
  if mode == 'i':

    # The same as the code for update_inv()
    for i in range( 10 ):
      if chest_slot( x, y, i ) == item_id and chest_slot( x, y, i, amount = True ) > 0:
        chest_slot( x, y, i, amount, amount = True, op = '+' )
        return True

    for i in range( 10 ):
      if chest_slot( x, y, i, amount = True ) == 0:
        chest_slot( x, y, i, item_id, op = '=' )
        chest_slot( x, y, i, amount, amount = True, op = '=' )
        return True

    return False

  # Remove
  elif mode == 'r':

    # Try to remove
    for i in range( 10 ):
      if chest_slot( x, y, i ) == item_id:
        if chest_slot( x, y, i, amount = True ) >= amount:

          chest_slot( x, y, i, amount, amount = True, op = '-' )
          data_save()
          return amount

        elif chest_slot( x, y, i, amount = True ) > 0:

          chest_slot( x, y, i, 0, amount = True, op = '=' )
          data_save()
          return chest_slot( x, y, i, amount = True )

    # Failed to remove
    return 0

def chest_remove( x, y ):

  global g_tile_special

  g_tile_special.pop( f'{ x } : { y }' )

def chest_slot( x, y, s, a = 0, amount = False, op = '?' ):

  global g_tile_special

  if op == '?':
    return int( g_tile_special[ f'{ x } : { y }' ][ f'slot{ s }' ].split( ':' )[ 1 if amount else 0 ] )

  values = g_tile_special[ f'{ x } : { y }' ][ f'slot{ s }' ].split( ':' )
  values = [ int( values[0] ), int( values[1] ) ]

  if op == '=':
    values[ 1 if amount else 0 ] = a
  elif op in ( '+', '-' ):
    values[ 1 if amount else 0 ] += a * ( 1 if op == '+' else -1 )

  g_tile_special[ f'{ x } : { y }' ][ f'slot{ s }' ] = f'{ values[0] }:{ values[1] }'

# Break a block
def break_block( x, y, ignore_tree = False ):

  global g_tile_data, g_tile_special

  # Make sure it's within the world boundaries
  if not ( 0 <= x < g_world_size.x ): return
  if not ( 0 <= y < g_world_size.y ): return

  # Store what the block was, then change it
  old_value = g_tile_data[ xy2c( x, y, g_world_size.x ) ]
  g_tile_data[ xy2c( x, y, g_world_size.x ) ] = ' '

  # If the block is part of a tree
  if not ignore_tree and old_value in ( 'l', 'L' ) and 'type' in g_tile_special[ f'{ x } : { y }' ]:

    # Copy the tile positions from the root
    tile_positions = []
    if g_tile_special[ f'{ x } : { y }' ][ 'type' ] == 'root':
      root_pos = V2( x, y )
      for i in g_tile_special[ f'{ x } : { y }' ][ 'links' ].split( ',,' ):
        tile_positions.append( V2( int( i.split( ',' )[0] ), int( i.split( ',' )[1] ) ) )
    else:
      root_pos = g_tile_special[ f'{ x } : { y }' ][ 'root' ]
      root_pos = V2( int( root_pos.split( ',' )[0] ), int( root_pos.split( ',' )[1] ) )
      for i in g_tile_special[ f"{ root_pos.x } : { root_pos.y }" ][ 'links' ].split( ',,' ):
        tile_positions.append( V2( int( i.split( ',' )[0] ), int( i.split( ',' )[1] ) ) )

    # Remove branches that are above the one broken
    # And all the leaves
    for pos in tile_positions.copy():
      if ( pos.y <= y or get_tile( *pos.l() ) == 'L' ) and ( pos.x != x or pos.y != y ):
        old_value = break_block( *pos.l(), ignore_tree = True )
        if old_value in ITEM_BLOCKS:
          update_inv( ITEM_BLOCKS[ old_value ], 1 )
        tile_positions.remove( pos )
      elif ( pos.x == x and pos.y == y ):
        tile_positions.remove( pos )

    # Remove unwanted positions from stem data
    if get_tile( *root_pos.l() ) == 'l':
      tile_strings = []
      for pos in tile_positions:
        tile_strings.append( f'{ pos.x },{ pos.y }' )
      g_tile_special[ f'{ root_pos.x } : { root_pos.y }' ][ 'links' ] = ',,'.join( tile_strings )

  # Remove special data if necessary
  if f'{ x } : { y }' in g_tile_special:
    g_tile_special.pop( f'{ x } : { y }' )

  data_save() # Save data

  # Return what the block was
  return old_value

# Place a block
def place_block( x, y ):

  global g_tile_data

  # Make sure it's within the world boundaries
  if not ( 0 <= x < g_world_size.x ): return
  if not ( 0 <= y < g_world_size.y ): return

  # If the block is air, replace it
  if g_tile_data[ xy2c( x, y, g_world_size.x ) ] == ' ':

    # Get the block ID of the currently selected item ID
    g_tile_data[ xy2c( x, y, g_world_size.x ) ] = list( ITEM_BLOCKS.keys() )[ list( ITEM_BLOCKS.values() ).index( g_items[ g_slot ][0] ) ]

    # Initialize chest data if necessary
    if g_tile_data[ xy2c( x, y, g_world_size.x ) ] == 'c':
      chest_create( x, y )

    data_save() # Save data
    return True

  # Else, return False to indicate failure
  return False

# This function exists to reduce code repetition
def try_break_block( x, y ):

  # Check whether the player is holding a pickaxe

  # Not holding anything
  if g_items[ g_slot ][1] <= 0:
    print( f'[!] You are not holding an item!' )
    goto_room( room_scene, '1' )

  # Not holding pickaxe
  elif g_items[ g_slot ][0] != 2:
    print( f'[!] Item "{ item_meta( g_slot, c = 1 ) }" cannot break blocks!' )
    goto_room( room_scene, '1' )

  # Holding pickaxe
  else:

    # Break block
    # break_block() performs bounds checking, so there's no need to check whether our break position is within the world
    old_value = break_block( g_pos.x + x, g_pos.y + y )

    # break_block() returns the ID of the block that was broken, which is stored in t
    # If possible, this block is put in the player's inventory
    if old_value in ITEM_BLOCKS:
      update_inv( ITEM_BLOCKS[ old_value ], 1 )

    # Performing a game tick prevents the player from floating above it like a cartoon character
    tick()
    goto_room( room_scene ) # We can now reload the room

# This function also exists to reduce code repetition
# (even though it's pretty much just an inverse of the above function)
def try_place_block( x, y ):

  # Check whether the player is holding a block

  # Not holding anything
  if g_items[ g_slot ][1] <= 0:
    print( f'[!] You are not holding an item!' )
    goto_room( room_scene, '1' )

  # Not holding a block
  elif g_items[ g_slot ][0] not in ITEM_BLOCKS.values():
    print( f'[!] Item "{ item_meta( g_slot, c = 1 ) }" is not placeable!' )
    goto_room( room_scene, '1' )

  # Holding a block
  else:

    # Place block
    # place_block() performs bounds checking, so there's no need to check whether our break position is within the world
    success = place_block( g_pos.x + x, g_pos.y + y )

    # place_block() returns whether the attempt was successful, which is stored in t
    # If successful, one block is removed from the player's inventory
    if success:
      update_inv( g_items[ g_slot ][0], 1, 'r' )

    # Performing a game tick prevents the player from floating above it like a cartoon character
    tick()
    goto_room( room_scene ) # We can now reload the room

def try_fight():

  temp_rand = random.randint( 1, 100 ) # Used for deciding which enemy is encountered

  # Top 25% - Harpies only
  if ( g_pos.y <= g_world_size.y * 0.25 ):
    start_fight( 'harpy' )

  # 40%-60% - 50% slime, 30% zombie, 20% demon_eye
  elif ( g_world_size.y * 0.25 < g_pos.y <= g_world_size.y * 0.6 ):
    if ( temp_rand < 50 ): start_fight( 'slime' )
    elif ( temp_rand < 80 ): start_fight( 'zombie' )
    else: start_fight( 'demon_eye' )

  # 60%-80% - 70% cave bat, 30% skeleton
  elif ( g_world_size.y * 0.6 < g_pos.y <= g_world_size.y * 0.8 ):
    if ( temp_rand < 70 ): start_fight( 'cave_bat' )
    else: start_fight( 'skeleton' )

  # Bottom 20% - 30% cave bat, 15% skeleton, 50% undead miner, 5% tim
  elif ( g_world_size.y * 0.8 < g_pos.y ):
    if ( temp_rand < 30 ): start_fight( 'cave_bat' )
    elif ( temp_rand < 80 ): start_fight( 'undead_miner' )
    elif ( temp_rand < 95 ): start_fight( 'skeleton' )
    else: start_fight( 'tim' )

def start_fight( monster_id ):
  
  global g_monster
  g_monster = Monster( monster_id )
  
  print_line()
  input( f"You encountered a { g_monster.name.replace( '_', ' ' ).title() }! " )
  
  goto_room( room_fight )

def start_bossfight():

  global g_monster
  g_monster = EyeOfCthulhu()

  print_line()
  for c in 'Eye of Cthulhu has awoken!':
    print( c, end = '', flush = True )
    time.sleep( 0.08 )
  time.sleep( 2 )
  print()

  goto_room( room_bossfight )

# Initialize the data file if it doesn't exist
def data_main_init():

  file = open( 'data.txt', 'w', encoding = 'utf-8' )
  file.write( 'characters: \n' )
  file.write( 'worlds: \n' )
  file.write( 'blocks: player=Δ;air= ;grass=~;stone=#;log=];leaves=*;iron=&;silver=$;gold=%;wood==;platform=-;chest=©;crystal=♥,enemy=!' )

# Loads character list, world list, and settings
def data_main_load():

  global g_data, g_tmap

  # Initialize the data file if it doesn't exist
  test = open( 'data.txt', 'a+', encoding = 'utf-8' )
  test.seek( 0 )
  if test.read() == '':
    data_main_init()

  # Read the character and world lists
  file = open( 'data.txt', 'r', encoding = 'utf-8' ).read().split( '\n' )
  g_data[ 'char_list' ] = file[0][ 12: ].split( ',' )
  if g_data[ 'char_list' ] == [ '' ]:
    g_data[ 'char_list' ] = []
  g_data[ 'world_list' ] = file[1][ 8: ].split( ',' )
  if g_data[ 'world_list' ] == [ '' ]:
    g_data[ 'world_list' ] = []

  # Define the tile map
  raw_tile_map = file[2][ 8: ].replace( '==', '=__EQUAL__').split( ';' )
  for pair in raw_tile_map:
    if len( pair.split( '=' ) ) == 2 and len( pair.split( '=' )[1] ) > 0:
      g_tmap[ pair.split( '=' )[0] ] = ( pair.split( '=' )[1] if pair.split( '=' )[1] != '__EQUAL__' else '=' )

# Write back to the data file if something changed
def data_main_update():

  file = open( 'data.txt', 'w', encoding = 'utf-8' )

  # Character/world lists
  file.write( 'characters: ' )
  for c in g_data[ 'char_list' ]:
    file.write( ( ',' if c != g_data[ 'char_list' ][0] else '' ) + c )
  file.write( '\nworlds: ' )
  for c in g_data[ 'world_list' ]:
    file.write( ( ',' if c != g_data[ 'world_list' ][0] else '' ) + c )

  # Tile map
  tile_map_string = ''
  for b in g_tmap:
    tile_map_string += ';' + b + '=' + g_tmap[b]
  file.write( '\nblocks: ' + tile_map_string[1:] )

# Initialize a character file upon creation
def data_char_init( name ):

  # Open/write to file
  file = open( 'c_' + name + '.txt', 'w' )
  file.write( 'version: 1.0\n' )
  file.write( 'hp: 100,100\n' )
  file.write( 'items: 1:1,2:1,' ) # Defaults to sword/pickaxe
  for i in range( 14 ):
    file.write( '0:0' + ( ',' if i != 15 else '' ) )
  file.write( '\nextra_items: \n' )
  file.write( 'deaths: 0\n' )
  file.write( 'play_time: 0' )

# Load a character file with a given name
def data_char_load( name ):

  global g_hp, g_hp_max, g_items, g_items_extra, g_deaths, g_versions, g_play_time

  # Split file into statements
  file = open( 'c_' + name + '.txt', 'r' ).read().split( '\n' )

  # Read version
  g_versions[0] = file[0][9:]

  # Read HP data
  g_hp = int( file[1][4:].split( ',' )[0] )
  g_hp_max = int( file[1][4:].split( ',' )[1] )

  # Setup item array
  g_items = []
  item_string = file[2][7:].split( ',' )
  for i in range( 16 ):
    g_items.append( [ int( item_string[i].split( ':' )[0] ), int( item_string[i].split( ':' )[1] ) ] )

  # Setup extra item array
  g_items_extra = []
  item_string = file[3][13:].split( ',' )
  if len( file[3][13:] ) > 0:
    for i in item_string:
      g_items_extra.append( [ int( i.split( ':' )[0] ), int( i.split( ':' )[1] ) ] )

  # Other stuff
  g_deaths = int( file[4][8:] )
  g_play_time = int( file[5][11:] )

  update_inv( 0, 0, mode = '!' ) # Properly organizes inventory

# Prints the details of a character file
def data_char_info( name ):

  # Split file into statements
  file = open( 'c_' + name + '.txt', 'r' ).read().split( '\n' )

  # Print info
  print( f"Name: { name }" )
  print( f"HP: { file[1][4:].split( ',' )[0] } / { file[1][4:].split( ',' )[1] }" )
  print( f"Deaths: { file[4][8:] }" )
  print( f"Play Time: { format_playtime( int( file[5][11:] ) ) }" )

# Write back to the character file if something changed
def data_char_update( name ):

  update_playtime()

  file = open( 'c_' + name + '.txt', 'w' )

  # Write version
  file.write( f'version: { g_versions[0] }\n' )

  # Write HP data
  file.write( f'hp: { g_hp },{ g_hp_max }\n' )

  # Write item array
  file.write( 'items: ' )
  for i in range( 16 ):
    file.write( f'{ g_items[i][0] }:{ g_items[i][1] }' + ( ',' if i != 15 else '' ) )

  # Write extra item array
  file.write( '\nextra_items: ' )
  for i in range( len( g_items_extra ) ):
    file.write( f'{ g_items_extra[i][0] }:{ g_items_extra[i][1] }' + ( ',' if i != len( g_items_extra ) - 1 else '' ) )

  # Other stuff
  file.write( f'\ndeaths: { g_deaths }\n' ) 
  file.write( f'play_time: { int( g_play_time ) }' )

def generate_world( size, seed ):

  # WORLDGEN PARAMETERS
  CAVES = True
  CAVES_FREQ = 32
  POCKETS = True
  POCKETS_FREQ = 128
  TREES = True
  ORES = True
  ORES_FREQ = 128
  CRYSTALS = True
  CRYSTALS_FREQ = 25
  CHESTS = True
  CHESTS_FREQ = 8

  global g_tile_data, g_tile_special, g_pos

  # Clean slate
  g_tile_data = ''
  g_tile_special = {}
  progress = 0
  random.seed( seed )
  print( 'Generating World:' )

  # Fill world with air
  for j in range( size.y ):
    for i in range( size.x ):
      g_tile_data += ' '
    progress = print_progress( progress, size.y, 5, 'Creating world array' ) # Update progress as it iterates
  g_tile_data = list( g_tile_data )

  # Fill in area under the noise curve
  for i in range( size.x ):
    noise_height = int( ( size.y / 2 ) + noise_top( i, seed ) )

    # 4 blocks of grass
    for j in range( noise_height, noise_height + 4 ):
      g_tile_data[ xy2c( i, j, size.x ) ] = 'g'

    # And everything under it is stone
    for j in range( noise_height + 4, size.y ):
      g_tile_data[ xy2c( i, j, size.x ) ] = 's'

    progress = print_progress( progress, size.x, 15, 'Generating initial terrain' ) # Update progress

  # Generate iron, silver, and gold
  if ORES:

    for l1 in range( ORES_FREQ ): # Each iteration creates another vein

      # Create a vector at a random underground position
      o = V2( random.randint( 0, size.x ), 0 )
      o.y = random.randint( int( ( size.y / 2 ) + noise_top( o.x, seed ) ) + 10, size.y )

      d = 0 # This variable represents the direction (in radians)

      # Choose which kind of ore it is (depending on height)
      if ( o.y / size.y < 0.65 ):
        c = 'i'
      elif ( o.y / size.y < 0.75 ):
        c = random.choice( ( 'i', 'i', 'S' ) )
      else:
        c = random.choice( ( 'i', 'i', 'i', 'S', 'S', 'G' ) )

      # This block moves the vector in a random direction on each iteration,
      # Which (somehow) usually leads to the blob-like shape I was going for
      # However, it's still possible for it to come out looking like a snake
      for l2 in range( 48 ):
        d += random.randrange( -10, 10 ) 
        o.a( cos( d ), sin( d ) )
        if o.y < ( size.y / 2 ) + noise_top( o.x, seed ) + 4:
          continue
        g_tile_data[ xy2c( clamp( int( o.x ), 1, size.x - 2 ), clamp( int( o.y ), 1, size.y - 2 ), size.x ) ] = c

      progress = print_progress( progress, ORES_FREQ, 35, 'Generating ore veins' ) # Update progress
  else:
    progress = print_progress( progress, 1, 35, 'Generating ore veins' ) # Autofill progress if skipped

  # Generate large caves
  if CAVES:

    # Each iteration creates another cave
    for l1 in range( CAVES_FREQ ):

      # Create a vector in the bottom 30% of the world
      o = V2( random.randint( 0, size.x ), random.randint( size.y * 0.7, size.y ) )

      d = 0 # This variable represents the current direction (in radians)
      s = random.randrange( 2, 4 ) # This variable represents the current side (as a radiUS :D)

      # This block moves the vector in a random direction on each iteration,
      # very similar to how the veins are created.
      # However, unlike the ore veins, the direction only slightly changes
      # on each iteration, creating longer snake-like formations
      for l2 in range( 48 ):
        d += random.randrange( -10, 10 ) / 10
        o.a( cos( d ) * 2, sin( d ) * 2 )
        s += random.randrange( -10, 10 ) / 10
        s = clamp( s, 2, 4.5 )
        for j in range( max( int( o.y ) - int( s ), 1 ), min( int( o.y ) + int( s ), size.y - 2 ) ):
          for i in range( max( int( o.x ) - int( s ), 1 ), min( int( o.x ) + int( s ), size.x - 2 ) ):
            if dist( o, V2( i, j ) ) < s:
              g_tile_data[ xy2c( i, j, size.x ) ] = ' '

      progress = print_progress( progress, CAVES_FREQ, 15, 'Generating caves' ) # Update progress

  else:
    progress = print_progress( progress, 1, 15, 'Generating caves' ) # Autofill progress if skipped

  # Generate small air pockets
  if POCKETS:

    # Each iteration creates another air pocket
    for l1 in range( POCKETS_FREQ ):

      # This code works in the exact same way as the ore code
      # (I wrote this one first, though)
      o = V2( random.randint( 0, size.x ), 0 )
      o.y = random.randint( int( ( size.y / 2 ) + noise_top( o.x, seed ) ) + 10, size.y )
      d = 0
      for l2 in range( 64 ):
        d += random.randrange( -10, 10 ) 
        o.a( cos( d ), sin( d ) )
        g_tile_data[ xy2c( clamp( int( o.x ), 1, size.x - 2 ), clamp( int( o.y ), 1, size.y - 2 ), size.x ) ] = ' '

      progress = print_progress( progress, POCKETS_FREQ, 15, 'Generating air pockets' ) # Update progress

  else:
    progress = print_progress( progress, 1, 15, 'Generating air pockets' ) # Autofill progress if skipped

  # Generate trees
  if TREES:

    # Pick a random starting position [5, 15] blocks from the world's left bound
    i1 = random.randint( 5, 15 )

    # Continue until the position is within 15 blocks of the right bound
    while i1 < size.x - 15:

      # Create a vector at the current x position and the y position of the surface
      o = V2( i1, int( ( size.y / 2 ) + noise_top( i1, seed ) - 1 ) )

      if g_tile_data[ xy2c( o.x, o.y + 1, size.x ) ] == 'g': # Make sure there's grass below
      
        # Mark root
        root = o.copy()
        root_links = []

        # Continue upward for a random height [10, 20]
        for i2 in range( random.randint( 10, 20 ) ):

          # Place down a log and move vector upward (also save special tile data)
          g_tile_data[ xy2c( o.x, o.y, size.x ) ] = 'l'
          if o.l() != root.l():
            g_tile_special[ str( o.x ) + " : " + str( o.y ) ] = { 'type': 'tile', 'root': f'{ root.x },{ root.y }' }
            root_links.append( f'{ o.x },{ o.y }' )
          o.y -= 1

          # Decide whether the tree should sway a little
          if random.randint( 0, 35 ) == 0:
            o.x -= 1
          if random.randint( 0, 35 ) == 0:
            o.x += 1

        # Create leaves in a circular pattern
        # (with decreasing frequency as you travel away from the origin)
        for j in range( o.y - 4, o.y + 4 ):
          for i in range( o.x - 4, o.x + 4 ):
            if random.randint( 0, int( dist( V2( i, j ), o ) ) ) <= 1:
              g_tile_data[ xy2c( i, j, size.x ) ] = 'L'
              g_tile_special[ str( i ) + " : " + str( j ) ] = { 'type': 'stem', 'root': f'{ root.x },{ root.y }' }
              root_links.append( f'{ i },{ j }' )

        # Create root data now that the tree's tile positions have been recorded 
        g_tile_special[ str( root.x ) + " : " + str( root.y ) ] = { 'type': 'root', 'links': ',,'.join( root_links ) }

      # Choose how far to move before creating another tree
      i1 += int( random.randint( 8, 15 ) * random.choice( ( 0.6, 1, 1, 4 ) ) )

    progress = print_progress( progress, 1, 5, 'Generating trees' ) # Update progress
  else:
    progress = print_progress( progress, 1, 5, 'Generating trees' ) # Autofill progress if skipped

  # Chest rooms
  if CHESTS:

    # List of the position of every chest
    chest_positions = []

    # Each iteration creates a new chest room
    for l1 in range( CHESTS_FREQ ):

      # Basically a while loop but with a limit so it doesn't go forever if something unexpected happens
      for l2 in range( 999 ):      

        # Choose a random position underground
        o = V2( random.randint( 30, size.x - 30 ), random.randint( int( size.y * 0.7 ), size.y - 5 ) )

        # See if it's too close to another chest
        too_close = False
        for i in chest_positions:
          if dist( o, i ) < 40: too_close = True

        # If not, place it and the room
        if not too_close:
          
          chest_positions.append( o )
          for yy in range( o.y - 8, o.y + 2 ):
            for xx in range( o.x - 10, o.x + 11 ):
              g_tile_data[ xy2c( xx, yy, size.x ) ] = ( 'w' if xx in ( o.x - 10, o.x + 10 ) or yy in ( o.y - 8, o.y + 1 ) else ' ' ) # Place outline / air pocket
          g_tile_data[ xy2c( *o.l(), size.x ) ] = 'c' # Place chest

          # CHEST INFO
          chest_create( *o.l() )

          chosen_item = random.choice( ( ( I_SUS_EYE, 1, 1 ), ( I_HEALTH_POTION, 1, 1 ), ( I_GRENADE, 4, 7 ) ) )
          chest_modify( *o.l(), chosen_item[0], random.randint( chosen_item[1], chosen_item[2] ), mode = 'i' ) # Random item for slot 1

          chosen_item = random.choice( ( ( I_IRON_BAR, 3, 5 ), ( I_SILVER_BAR, 3, 5 ), ( I_GOLD_BAR, 3, 5 ) ) )
          chest_modify( *o.l(), chosen_item[0], random.randint( chosen_item[1], chosen_item[2] ), mode = 'i' ) # Random bar for slot 1

          chosen_item = random.choice( ( ( I_TORCH, 10, 15 ), ( I_ARROW, 15, 25 ), ( I_F_ARROW, 8, 15 ) ) )
          chest_modify( *o.l(), chosen_item[0], random.randint( chosen_item[1], chosen_item[2] ), mode = 'i' ) # Random bar for slot 1

          break

      progress = print_progress( progress, CHESTS_FREQ, 5, 'Generating chest rooms' ) # Update progress
  else:
    progress = print_progress( progress, 1, 5, 'Generating chest rooms' ) # Autofill progress if skipped

  # Generate life crystals
  if CRYSTALS:
    
    # Each iteration creates a new life crystal
    for l1 in range( CRYSTALS_FREQ ):

      # Basically a while loop but with a limit so it doesn't go forever if something unexpected happens
      for l2 in range( 999 ):

        # Choose a random position underground
        o = V2( random.randint( 0, size.x ), random.randint( int( size.y * 0.62 ), size.y - 5 ) )

        # Continue downward until stone block is found
        for l3 in range( o.y, size.y - 4 ):

          # Check if a life crystal can go here
          o.y += 1
          if g_tile_data[ xy2c( *o.l(), size.x ) ] == ' ' and g_tile_data[ xy2c( *o.copy().a( 0, 1 ).l(), size.x ) ] == 's':

            # Create a life crystal and exit the loop
            g_tile_data[ xy2c( *o.l(), size.x ) ] = 'C'
            break
        else:
          continue

        break

      progress = print_progress( progress, CRYSTALS_FREQ, 5, 'Generating life crystals' ) # Update progress
  else:
    progress = print_progress( progress, 1, 5, 'Generating life crystals' ) # Autofill progress if skipped

  # Lastly, position the player
  g_pos = V2( size.x // 2, int( ( size.y / 2 ) + noise_top( size.x // 2, seed ) ) - 1 )
  g_spawn = V2( size.x // 2, int( ( size.y / 2 ) + noise_top( size.x // 2, seed ) ) - 1 )
  g_tile_data[ xy2c( g_pos.x, g_pos.y + 1, size.x ) ] = 'g' # Make sure the player is standing on a block

  # Set progress to 100 (in case something glitched)
  print_progress( 50, 1, 1, 'This should never print' )
  print() # Newline

# Initialize a world file upon creation
def data_world_init( name, seed ):

  file = open( 'w_' + name + '.txt', 'w' )
  size = V2( 400, 200 )

  generate_world( size, seed )

  # Write non-tile data
  file.write( 'version: 1.0\n')
  file.write( f'size: { size.x },{ size.y }\n')
  file.write( f'seed: { seed }\n')
  file.write( f'player_pos: { g_pos.x },{ g_pos.y }\n' )
  file.write( f'player_pos: { g_pos.x },{ g_pos.y }\n' )

  # Write tile data
  for j in range( size.y ):
    file.write( ''.join( g_tile_data[ ( j * size.x ):( ( j + 1 ) * size.x ) ] ) )
    file.write( '\n' )

  # Write special tile data
  for t in g_tile_special:

    file.write( 'S' + t.replace( ' ', '' ) + ': ' )
    special_data_keys = [] # Empty list to hold temp data

    # ;; separates K:V pairs, and ; separates the K and V
    for k in g_tile_special[t]:
      special_data_keys.append( f'{ k };{ g_tile_special[t][k] }' )
    file.write( ';;'.join( special_data_keys ) + '\n' )

# Load a world file with a given name
def data_world_load( name ):

  global g_pos, g_spawn, g_world_size, g_seed, g_tile_data, g_tile_special, g_show_help, g_slot, g_versions, g_play_time_last, g_enemy_timer

  # Split file into statements
  file = open( 'w_' + name + '.txt', 'r' ).read().split( '\n' )

  # Read version
  g_versions[1] = file[0][9:]

  # Read basic positional data
  g_world_size = V2( int( file[1][6:].split( ',' )[0] ), int( file[1][6:].split( ',' )[1] ) )
  g_seed = int( file[2][6:] )
  g_pos = V2( int( file[3][12:].split( ',' )[0] ), int( file[3][12:].split( ',' )[1] ) )
  g_spawn = V2( int( file[4][12:].split( ',' )[0] ), int( file[4][12:].split( ',' )[1] ) )

  # Read tile data
  g_tile_data = "";
  for j in range( g_world_size.y ):
    g_tile_data += file[5 + j]
  g_tile_data = list( g_tile_data )

  # Read special tile data
  g_tile_special = {}
  for line in file[ 5 + g_world_size.y:len( file ) ]:

    # Exit if not data
    if not ( len( line ) > 0 and line[0] == 'S' ): continue

    temp_key = ' : '.join( line.split( ': ' )[0][1:].split( ':' ) )
    g_tile_special[ temp_key ] = {}
    for i in line.split( ': ' )[1].split( ';;' ):
      g_tile_special[ temp_key ][ i.split( ';' )[0] ] = i.split( ';' )[1]

  g_show_help = True # Shows a help message on your first turn in the world
  g_slot = 0 # Reset selected slot
  g_play_time_last = time.time()

  # Reset enemy timer
  g_enemy_timer = random.randint( 20, 35 )

# Prints info for a world file
def data_world_info( name ):

  # Split file into statements
  file = open( 'w_' + name + '.txt', 'r' ).read().split( '\n' )

  # Print info
  print( f"Name: { name }" )
  print( f"Seed: { int( file[2][6:] ) }" )
  print( f"Size: { int( file[1][6:].split( ',' )[0] ) }x{ int( file[1][6:].split( ',' )[1] ) }" )

# Write back to the world file if something changed
def data_world_update( name ):

  global g_tile_special

  file = open( 'w_' + name + '.txt', 'w' )

  # Write non-tile data
  file.write( f'version: { g_versions[1] }\n')
  file.write( f'size: { g_world_size.x },{ g_world_size.y }\n')
  file.write( f'seed: { g_seed }\n')
  file.write( f'player_pos: { g_pos.x },{ g_pos.y }\n' )
  file.write( f'spawnpoint: { g_spawn.x },{ g_spawn.y }\n' )

  # Write tile data
  for j in range( g_world_size.y ):
    file.write( ''.join( g_tile_data[ ( j * g_world_size.x ):( ( j + 1 ) * g_world_size.x ) ] ) )
    file.write( '\n' )

  # Write special tile data
  for t in g_tile_special:

    file.write( 'S' + t.replace( ' ', '' ) + ': ' )
    special_data_keys = [] # Empty list to hold temp data
    
    # Read the K:V pair for this tile
    for k in g_tile_special[t]:
      special_data_keys.append( f'{ k };{ g_tile_special[t][k] }' )
    file.write( ';;'.join( special_data_keys ) + '\n' )

# Saves both character data and world data
def data_save():

  global g_cname, g_wname

  if g_cname != '':
    data_char_update( g_cname )
  if g_wname != '':
    data_world_update( g_wname )

# All room functions should be passed into the goto_room() function as a pointer object
# The starting room
def room_menu():
  
  global g_cname, g_wname

  # TITLE TEXT :D
  # (generated using https://patorjk.com/software/taag/#p=display&h=0&v=0&f=Soft&t=Terrible-aria)
  print_line()
  print( '''

,--------.                         ,--. ,--.    ,--.                                  ,--.
'--.  .--'  ,---.  ,--.--. ,--.--. `--' |  |-.  |  |  ,---.  ,-----.  ,--,--. ,--.--. `--'  ,--,--.
   |  |    | .-. : |  .--' |  .--' ,--. | .-. ' |  | | .-. : '-----' ' ,-.  | |  .--' ,--. ' ,-.  |
   |  |    \   --. |  |    |  |    |  | | `-' | |  | \   --.         \ '-'  | |  |    |  | \ '-'  |
   `--'     `----' `--'    `--'    `--'  `---'  `--'  `----'          `--`--' `--'    `--'  `--`--'
                                                                                    (v1.0)

[P] Play
[Q] Quit''')

  # Reset important stuff
  g_cname = ''
  g_wname = ''
  
  # Keep looping until a valid input is provided
  while True:
    p = input( '> ' ).lower()

    # Play
    if p == 'p':
      goto_room( room_char_select )

    # Quit
    elif p == 'q':
      print( '[!] Game was closed.' )
      goto_room( 0 )

    # Error handling
    else:
      print( '[#] Unknown command.' )

# Character selection room
def room_char_select():

  global g_cname, g_data

  # Print options
  print_line()
  print( 'Characters:' )
  for i in range( len( g_data[ 'char_list' ] ) ):
    print( f'[{ i + 1 }] { g_data[ "char_list" ][i] }' )
  print( '[C] Create new character' )
  print( '[I] Character info' )
  print( '[D] Delete character' )
  print( '[Q] Back' )

  while True:

    p = input( '> ' ).lower()

    # Create character
    if p == 'c':
      goto_room( room_char_create )

    # Back
    elif p == 'q':
      goto_room( room_menu )

    # Delete character/character info
    elif p == 'd' or p == 'i':

      # Exit if no worlds exist (to prevent softlock :))
      if len( g_data[ 'char_list' ] ) == 0:
        print( '[#] The character list is empty.' )
        goto_room( room_char_select )

      p_old = p

      # Get index
      print( f'Enter the character slot would like to { "delete" if p == "d" else "get info for" }:' )
      while True:
        p = input( '> ' )

        # Attempt cast
        try:
          p = int( p )
        except ValueError:
          print( '[#] Enter a number.' )
        else:

          # Too large/too small
          if not ( 0 < p <= len( g_data[ 'char_list' ] ) ):
            print( '[#] Out of range.' )

          else:

            # Store name in a temp variable
            temp_name = g_data[ 'char_list' ][ p - 1 ]

            # Delete
            if p_old == 'd':

              # Make sure they actually want to
              print( f'Are you sure you want to delete character "{ temp_name }"?' )
              print( 'Type "yes" to proceed.' )
              if input( '> ' ).lower() == 'yes':

                # Delete character file and update character list in data.txt
                print( '[!] Character deleted.' )
                if os.path.exists( 'c_' + temp_name + '.txt' ):
                  os.remove( 'c_' + temp_name + '.txt' )
                g_data[ 'char_list' ].pop( p - 1 )
                data_main_update()

            # Info
            else:

              # Show info
              data_char_info( temp_name )

            # Re-show character list
            goto_room( room_char_select )

    # Either number or invalid input
    else:

      # Attempt cast
      try:
        p = int( p )
      except ValueError:
        print( '[#] Unknown command.' )

      else:

        # Too large/too small
        if not ( 0 < p <= len( g_data[ 'char_list' ] ) ):
          print( '[#] Out of range' )

        # Select character and move to world select room
        else:
          print( f'[!] Selected character "{ g_data[ "char_list" ][ p - 1 ] }"' )
          g_cname = g_data[ 'char_list' ][ p - 1 ]
          data_char_load( g_cname )
          goto_room( room_world_select )

# Character creation room
def room_char_create():

  global g_data

  # Get name
  print_line()
  print( 'Enter a name:' )
  while True:
    name = input( '> ' )

    # Check length
    if not ( 0 < len( name ) <= 64 ):
      print( '[#] Name must be between 1 and 64 characters long.' )

    # Check for duplicate
    elif name in g_data[ 'char_list' ]:
      print( '[#] This character already exists.' )

    # Create file and reload character list
    else:
      g_data[ 'char_list' ].append( name )
      data_main_update()
      data_char_init( name )
      goto_room( room_char_select )

# World selection room
def room_world_select():

  global g_wname, g_data

  # Print options
  print_line()
  print( 'Worlds:' )
  for i in range( len( g_data[ 'world_list' ] ) ):
    print( f'[{ i + 1 }] { g_data[ "world_list" ][i] }' )
  print( '[C] Create new world' )
  print( '[I] World info' )
  print( '[D] Delete world' )
  print( '[Q] Back' )

  while True:

    p = input( '> ' ).lower()

    # Create world
    if p == 'c':
      goto_room( room_world_create )

    # Back
    elif p == 'q':
      goto_room( room_char_select )

    # Delete world/world info
    elif p == 'd' or p == 'i':

      # Exit if no worlds exist (to prevent softlock :))
      if len( g_data[ 'world_list' ] ) == 0:
        print( '[#] The world list is empty.' )
        goto_room( room_world_select )

      p_old = p

      # Get index
      print( f'Enter the world slot would like to { "delete" if p == "d" else "get info for" }:' )
      while True:
        p = input( '> ' )

        # Attempt cast
        try:
          p = int( p )
        except ValueError:
          print( '[#] Enter a number.' )
        else:

          print( p )

          # Too large/too small
          if not ( 0 < p <= len( g_data[ 'world_list' ] ) ):
            print( '[#] Out of range.' )

          else:

            # Store name in a temp variable so I don't have to retype this mess ↓
            temp_name = g_data[ 'world_list' ][ p - 1 ]

            # Delete
            if p_old == 'd':

              # Make sure they actually want to
              print( f'Are you sure you want to delete world "{ temp_name }"?' )
              print( 'Type "yes" to proceed.' )
              if input( '> ' ).lower() == 'yes':

                # Delete world file and update world list in data.txt
                print( '[!] World deleted.' )
                if os.path.exists( 'w_' + temp_name + '.txt' ):
                  os.remove( 'w_' + temp_name + '.txt' )
                g_data[ 'world_list' ].pop( p - 1 )
                data_main_update()

            # Info
            else:

              # Show info
              data_world_info( temp_name )

            # Re-show world list
            goto_room( room_world_select )

    # Either number or invalid input
    else:

      # Attempt cast
      try:
        p = int( p )
      except ValueError:
        print( '[#] Unknown command.' )

      else:

        # Too large/too small
        if not ( 0 < p <= len( g_data[ 'world_list' ] ) ):
          print( '[#] Out of range' )

        # Select character and move to scene
        else:
          print( f'[!] Selected world "{ g_data[ "world_list" ][ p - 1 ] }"' )
          g_wname = g_data[ 'world_list' ][ p - 1 ]
          data_world_load( g_wname )
          goto_room( room_scene )

# World creation room
def room_world_create():

  global g_data

  # Get name
  print_line()
  print( 'Enter a name:' )
  while True:
    name = input( '> ' )

    # Check length
    if not ( 0 < len( name ) <= 16 ):
      print( '[#] Name must be between 1 and 16 characters long.' )

    # Check for duplicate
    elif name in g_data[ 'world_list' ]:
      print( '[#] This world already exists.' )

    else:

      # Filter name
      name = list( name )
      for i in range( len( name ) ):
        if name[i] in [ ':', '/', '\\', '*', '?', '"', '<', '>', '|' ]:
          name[i] = '_'
      name = ''.join( name )

      # Continue to other options
      break

  # Get seed
  print( 'Enter a seed (blank = random):' )
  while True:
    seed = list( input( '> ' ).lower() )

    # Numerify seed
    # The seed needs to be a number, but instead of deleting all non-digit characters,
    # they're instead converted to either 0 or their index within the alphabet :D
    for i in range( len( seed ) ):
      if seed[i] in list( 'abcdefghijklmnopqrstuvwxyz' ):
        seed[i] = str( list( 'abcdefghijklmnopqrstuvwxyz' ).index( seed[i] ) + 1 )
      elif seed[i] not in list( '0123456789' ):
        seed[i] = '0'
    if seed == []:
      seed = random.randint( 1, 10 ** 32 )
    else:
      seed = int( ''.join( seed )[:32] )

    # Continue to other options
    break

  g_data[ 'world_list' ].append( name )
  data_main_update()
  data_world_init( name, seed )
  goto_room( room_world_select )

#
# WORLD SCENE ROOM
#
def room_scene( arg = '' ):

  global g_pos, g_view, g_tile_data, g_show_help, g_slot, g_monster, g_hp, g_hp_max

  # Track play time :)
  update_playtime()

  # Args can be set to 1 to avoid re-printing room data
  if not ( len( arg ) > 0 and arg[0] == '1' ):

    # Set view position, setting it offset (-30, -20) from the player pos,
    # then ensuring it stays within the world border
    g_view = g_pos.copy()
    g_view.x = clamp( g_pos.x - 30, 0, g_world_size.x - 61 )
    g_view.y = clamp( g_pos.y - 20, 0, g_world_size.y - 41 )

    # Print important data (HP, item)
    print_line()
    print( f'HP: { g_hp }/{ g_hp_max }' )
    print( f'ITEM: { item_meta( g_slot, c = 1 ) if g_items[ g_slot ][1] > 0 else "..." }' )
    print()

    # Display world
    # (The code to do this is surprisingly short, eh?)
    for j in range( g_view.y, g_view.y + 41 ):
      char_buffer = ''
      for i in range( g_view.x, g_view.x + 61 ):
        if i == g_pos.x and j == g_pos.y:
          char_buffer += g_tmap[ 'player' ] + ' '
        else:
          char_buffer += char2tile( g_tile_data[ xy2c( i, j, g_world_size.x ) ] ) + ' '
      print( char_buffer )

    # Show help options if loaded in for first time
    if g_show_help:
      print( '[H] Help' )
      print( '[H <command name>] Help with a specific command' )
      g_show_help = False

  while True:
    p = input( '> ' )
    parse_scene_cmd( p )

def parse_scene_cmd( cmd ):

  global g_pos, g_view, g_tile_data, g_show_help, g_slot, g_monster, g_hp, g_hp_max

  p_def = cmd
  p = cmd.lower()

  if p == 'h':
      print( '[H] Show this screen' )
      print( '[H <command name>] Help with a specific command' )
      print( '[M] Move in direction' )
      print( '[J] Jump' )
      print( '[D] Move down' )
      print( '[W] Wait' )
      print( '[I] Inventory' )
      print( '[S] Select item' )
      print( '[U] Use current item' )
      print( '[B] Break' )
      print( '[Z] Break/Move' )
      print( '[P] Break' )
      print( '[C] Use chest' )
      if DEBUG: print( '[$] Debug' )
      print( '[*] Pause' )

  # Show specific help info
  elif p[0:2] == 'h ':
    if p[2:] == 'h':
      print( '[?] Syntax: h' )
      print( '[?] Effect: Shows a list of valid commands.' )
      print( '[?] Syntax: h <command>' )
      print( '[?] Effect: Shows help for a specific command.' )
      print( '[?] (I mean, you clearly already know how this works...)' )
    elif p[2:] == '*':
      print( '[?] Syntax: *' )
      print( '[?] Effect: Brings up the pause menu.' )
    elif p[2:] == 'm':
      print( '[?] Syntax: m <direction> [steps (1)]' )
      print( '[?] Effect: Moves the specified number of steps in the given direction.' )
    elif p[2:] == 'j':
      print( '[?] Syntax: j [height (5)]' )
      print( '[?] Effect: Jumps the specified height.' )
    elif p[2:] == 'd':
      print( '[?] Syntax: d' )
      print( '[?] Effect: Moves downward through pseudo-solid blocks' )
    elif p[2:] == 'w':
      print( '[?] Syntax: w' )
      print( '[?] Effect: Allows a game tick to pass without the player performing an action.' )
    elif p[2:] == 'i':
      print( '[?] Syntax: i' )
      print( '[?] Effect: Opens the inventory.' )
    elif p[2:] == 's':
      print( '[?] Syntax: s <slot ID>' )
      print( '[?] Effect: Selects the item in a given slot.' )
      print( '[?] (Open your inventory to check slot IDs.)' )
    elif p[2:] == 'u':
      print( '[?] Syntax: u' )
      print( '[?] Effect: Uses the currently selected item.' )
      print( '[?] Effect: (Most items don\'t have a use function).' )
    elif p[2:] == 'b':
      print( '[?] Syntax: b <x> <y>' )
      print( '[?] Effect: Breaks the block x units right of the player and y units below the player.' )
      print( '[?] (Maximum is 4 blocks away in any direction.)' )
      print( '[?] Syntax: b <direction>' )
      print( '[?] Effect: Breaks the block 1 unit away from the player in the specified direction.' )
      print( '[?] (Accepted directions are "left", "right", "up", and "down".)' )
    elif p[2:] == 'z':
      print( '[?] Syntax: z <direction>' )
      print( '[?] Effect: Runs the break command and the move command in succession' )
      print( '[?] (Accepted directions are "left", "right", "up", and "down".)' )
    elif p[2:] == 'p':
      print( '[?] Syntax: p <x> <y>' )
      print( '[?] Effect: Places the selected block x units right of the player and y units below the player.' )
      print( '[?] (Maximum is 4 blocks away in any direction.)' )
      print( '[?] Syntax: p <direction>' )
      print( '[?] Effect: Places the selected block 1 unit away from the player in the specified direction.' )
      print( '[?] (Accepted directions are "left", "right", "up", and "down".)' )
    elif p[2:] == 'c':
      print( '[?] Syntax: c' )
      print( '[?] Effect: Opens a chest within the same block as the player.' )
      print( '[?] Syntax: c <x> <y>' )
      print( '[?] Effect: Opens a chest x units right of the player and y units below the player.' )
      print( '[?] (Maximum is 4 blocks away in any direction.)' )
    elif p[2:] == '$' and DEBUG:
      print( '[?] Syntax: $ <command> <arguments>' )
      print( '[?] Effect: Runs a sub-command.' )
      print()
      print( '[?] All sub commands can be found below:' )
      print( '[?] Syntax: $ jump <x> <y>' )
      print( '[?] Effect: Jumps to a position (x, y) within the world.' )
      print( '[?] Syntax: $ shift <x> <y>' )
      print( '[?] Effect: Moves x units rightward and y units downward.' )
      print( '[?] Syntax: $ give <id> [amount]' )
      print( '[?] Effect: Gives the player the specified amount of the given item.' )
      print( '[?] Syntax: $ take <id> [amount]' )
      print( '[?] Effect: Removes the specified amount of the given item.' )
      print( '[?] Syntax: $ set <x> <y> <block>' )
      print( '[?] Effect: Replaces the block at (x, y) relative to the player.' )
      print( '[?] Syntax: $ fight <monster id>' )
      print( '[?] Effect: Triggers a fight with the supplied monster ID.' )
    else:
      print( f'[#] Unknown command "{ p[2:] }".' )

  # Pause game
  elif p == '*':
    print( '[!] Game was paused.' )
    goto_room( room_pause )

  # Move command
  elif p == 'm':
    print( '[#] Must supply a direction.' )

  elif p[:2] == 'm ':

    # Make sure direction is valid
    if p.split( ' ' )[1] not in ( 'right', 'r', 'left', 'l' ):
      print( '[#] Invalid direction. (Accepts: "right", "left", "r", "l")' )

    else:

      # Get step count
      if len( p.split( ' ' ) ) >= 3:
        try:
          step_count = int( p.split( ' ' )[2] )
        except ValueError:
          print( '[#] Enter a number.' )
          step_count = 'ERROR'
      else:
        step_count = 1

      if step_count != 'ERROR':

        # Check range
        if not ( 0 < step_count <= 5 ):
          print( '[#] Step count out of range.' )

        # Move in given direction, run game tick, save data, and reload stage
        else:
          for i in range( step_count ):
            if ( 0 <= g_pos.x + ( 1 if p.split( ' ' )[1][0] == 'r' else -1 ) < g_world_size.x ):

              # Move in direction if air
              if get_tile( g_pos.x + ( 1 if p.split( ' ' )[1][0] == 'r' else -1 ), g_pos.y ) in AIR_BLOCKS:
                g_pos.x += ( 1 if p.split( ' ' )[1][0] == 'r' else -1 )

              # Else, try to step up one block
              elif g_pos.y > 0 and get_tile( g_pos.x + ( 1 if p.split( ' ' )[1][0] == 'r' else -1 ), g_pos.y - 1 ) in AIR_BLOCKS:
                g_pos.a( ( 1 if p.split( ' ' )[1][0] == 'r' else -1 ), -1 )

          data_save()
          tick()
          goto_room( room_scene )

  # Jump command
  elif p == 'j' or p[:2] == 'j ':

    # Get jump height
    if len( p ) > 1:
      try:
        jump_height = int( p[2:] )
      except ValueError:
        print( '[#] Enter a number.' )
        jump_height = 'ERROR'
    else:
      jump_height = 5

    if jump_height != 'ERROR':

      # Check range
      if not ( 0 < jump_height <= ( 20 if update_inv( I_HARPY_WINGS, 0, mode = 't' ) > 0 else 5 ) ):
        print( '[#] Jump height out of range.' )

      # If not on block and not on floor (unless they have wings), run game tick and reload stage
      elif g_pos.y + 1 < g_world_size.y and get_tile( g_pos.x, g_pos.y + 1 ) in AIR_BLOCKS and update_inv( I_HARPY_WINGS, 0, mode = 't' ) == 0:
        tick()
        goto_room( room_scene )

      # Jump, run game tick, save data, and reload stage
      else:
        for i in range( jump_height ):

          # Move up if possible
          if g_pos.y > 0 and get_tile( g_pos.x, g_pos.y - 1 ) in AIR_BLOCKS:
            g_pos.y -= 1

        data_save()
        tick( nofall = True )
        goto_room( room_scene )
  
  # Down command
  elif p == 'd':
  
    # Go through platform
    if g_pos.y < g_world_size.y - 1 and get_tile( g_pos.copy().a( 0, 1 ) ) == 'p':
      g_pos.a( 0, 1 )
    tick()
    goto_room( room_scene )

  # Wait
  elif p == 'w':

    tick()
    goto_room( room_scene )

  # Inventory
  elif p == 'i':
    goto_room( room_inventory )

  # Select
  elif p == 's':
    print( '[#] Must supply slot ID.' )

  elif p[:2] == 's ':

    # Make sure it matches a slot
    if p[2:] not in list( '1234567890abcdef' ):
      print( '[#] Enter a number from 0-9 or a letter from A-F.' )

    else:

      # Select slot
      g_slot = list( '1234567890abcdef' ).index( p[2:] )
      print( f'[!] Selected "{ item_meta( g_slot, c = 1 ) }".' if g_items[ g_slot ][1] > 0 else '[!] Cleared selection.' )
      goto_room( room_scene )

  # Use
  elif p == 'u':

    USABLES = [ I_SUS_EYE, I_HEALTH_POTION, I_CRYSTAL ]

    # Check if nothing is selected
    if g_items[ g_slot ][1] <= 0:
      print( '[#] You don\'t currently have an item selected.' )

    # Check if item has no function
    elif g_items[ g_slot ][ 0 ] not in USABLES:
      print( '[#] This item has no "use" functionality.' )

    # Do item-specific use actions
    else:

      if g_items[ g_slot ][ 0 ] == I_SUS_EYE:
        update_inv( I_SUS_EYE, 1, 'r' )
        start_bossfight()

      elif g_items[ g_slot ][ 0 ] == I_HEALTH_POTION:
        update_inv( I_HEALTH_POTION, 1, 'r' )
        print( f'[!] You used a healing potion. (+{ min( g_hp + 100, g_hp_max ) - g_hp } HP)' )
        g_hp = min( g_hp + 100, g_hp_max )
        goto_room( room_scene )

      elif g_items[ g_slot ][ 0 ] == I_CRYSTAL:
        if g_hp_max < 400:
          update_inv( I_CRYSTAL, 1, 'r' )
          print( '[!] You used a life crystal. (+20 MHP)' )
          g_hp_max += 20
          g_hp += 20
          goto_room( room_scene )
        else:
          print( '[#] Your health is already maxed.' )

  # Break
  elif p in ( 'b', 'p', 'z' ):
    print( '[#] Must supply direction.' )

  elif p[:2] in ( 'b ', 'p ', 'z ' ):

    # Check if it is a direction
    if p[2:] in ( 'left', 'right', 'down', 'up', 'l', 'r', 'd', 'u' ):

      # Attempt to either break or place the block
      try:
        if p[0] == 'b' or p[0] == 'z':
          try_break_block( *( V2( -1, 0 ), V2( 1, 0 ), V2( 0, 1 ), V2( 0, -1 ) )[ ( 'l', 'r', 'd', 'u' ).index( p[2] ) ].l() )
        elif p[0] == 'p':
          try_place_block( *( V2( -1, 0 ), V2( 1, 0 ), V2( 0, 1 ), V2( 0, -1 ) )[ ( 'l', 'r', 'd', 'u' ).index( p[2] ) ].l() )
        else:
          print( 'ERROR: I messed something up' )
      except MoveException as m:
        if p[0] != 'z' or m.arg == '1': raise m

      if p[0] == 'z' and p[2] in ( 'l', 'r' ):

        parse_scene_cmd( f'm { p[2:] }' )
      goto_room( room_scene )

    # If not, then the z command would have invalid arguments
    elif p[:2] == 'z':

      print( '[#] The "z" command only takes directional arguments.' )

    # Check if it's coordinates
    elif len( p[2:].split( ' ' ) ) == 2:

      try:
        p = [ int( p[2:].split( ' ' )[0] ), int( p[2:].split( ' ' )[1] ), p[0] ]
      except Exception:
        print( '[#] Enter 2 numbers.' )

      else:

        # Check range
        # Temporary variables used for easier formatting
        x_in_bounds = ( -4 <= p[0] <= 4 )
        y_in_bounds = ( -4 <= p[1] <= 4 )
        if not ( x_in_bounds and y_in_bounds ):
          print( f"[#] { '' if x_in_bounds else 'X' }{ '' if x_in_bounds or y_in_bounds else ' and ' }{ '' if y_in_bounds else 'Y' } coordinate{ '' if x_in_bounds or y_in_bounds else 's' } out of range. (Valid range: [-4, 4])" )

        # If both coordinates are valid, then continue onward
        if x_in_bounds and y_in_bounds:

          # Attempt to either break or place the block
          if p[2] == 'b':
            try_break_block( p[0], p[1] )
          else:
            try_place_block( p[0], p[1] )

    # Invalid arguments
    else:
      print( '[#] Enter either a direction or a coordinate pair.' )

  elif p == 'c' or p[0:2] == 'c ':

    # Get coordinates if they're supplied
    if len( p ) > 1:

      # Attempt cast
      try:
        chest_coords = V2( int( p[2:].split( ' ' )[0] ), int( p[2:].split( ' ' )[1] ) )
      except Exception:
        print( '[#] Enter 2 numbers.' )
        chest_coords = 'ERROR'
      else:

        # Check range
        x_in_bounds = ( -4 <= chest_coords.x <= 4 )
        y_in_bounds = ( -4 <= chest_coords.y <= 4 )
        if not ( x_in_bounds and y_in_bounds ):
          print( f"[#] { '' if x_in_bounds else 'X' }{ '' if x_in_bounds or y_in_bounds else ' and ' }{ '' if y_in_bounds else 'Y' } coordinate{ '' if x_in_bounds or y_in_bounds else 's' } out of range. (Valid range: [-4, 4])" )
          chest_coords = 'ERROR'

    # Else default to (0, 0)
    else:
      chest_coords = V2( 0, 0 )

    # If coordinates are correct, try to open chest
    if chest_coords != 'ERROR':

      if get_tile( g_pos.copy().a( chest_coords ) ) != 'c':
        print( '[#] There is not a chest at the block specified.' )

      # Success
      else:
        goto_room( room_chest, f'0,{ g_pos.copy().a( chest_coords ).x },{ g_pos.copy().a( chest_coords ).y }' )

  # Debug command (requires debug mode)
  elif p == '$' and DEBUG:
    print( '[#] Must supply a sub-command.')

  elif p[:2] == '$ ' and DEBUG:

    # Jump to position
    if p[2:] == 'jump' or p[2:] == 'shift':
      print( '[#] Must supply coordinates.' )

    elif p[2:7] == 'jump ' or p[2:8] == 'shift ':

      # Attempt casting coordinates
      try:
        dest_coords = V2( int( p[ ( 7 if p[2] == 'j' else 8 ): ].split( ' ' )[0] ), int( p[ ( 7 if p[2] == 'j' else 8 ): ].split( ' ' )[1] ) )
        if p[2] == 's':
          dest_coords.a( g_pos )
      except Exception:
        print( "[#] Invalid coordinates." )
      else:

        # Make sure coordinates are within world border
        if dest_coords.x < 0 or dest_coords.y < 0 or dest_coords.x >= g_world_size.x or dest_coords.y > g_world_size.y:
          print( 'Those coordinates are out of this world!\n(No, really)')
        else:
          g_pos = dest_coords
          data_save()
          print( f'[!] Moved player to ({ dest_coords.x }, { dest_coords.y })' )
          goto_room( room_scene )

    # Give/remove item
    elif p[2:] == 'give' or p[2:] == 'take':
      print( '[#] Must supply item info.' )

    elif p[2:7] == 'give ' or p[2:7] == 'take ':

      # Attempt casting info
      try:
        item_info = [ p[7:].split( ' ' )[0], int( p[7:].split( ' ' )[1] ) ]
      except Exception:
        print( '[#] Enter an item ID followed by a number.' )
      else:

        # Give/remove and print info
        try:

          # Filter input
          item_info[0] = 'I_' + ''.join( [ j.upper() for j in item_info[0] if j not in ( ')', '(', ' ', '.' ) ] )[ :20 ]

          if p[2] == 'g':
            exec( 'update_inv( ' + item_info[0] + ', item_info[1] )' )
            exec( 'print( f\'[!] Gave you "{ item_meta( ' + item_info[0] + ' ) }" x{ item_info[1] }\' )' )
          else:
            exec( 'amount_removed = update_inv( ' + item_info[0] + ', item_info[1], mode = \'r\' )' )
            exec( 'print( f\'[!] Removed "{ item_meta( ' + item_info[0] + ' ) }" x{ amount_removed }\' )' )
          goto_room( room_scene )
        except Exception:
          print( '[#] Invalid item ID.' )

    # Set block
    elif p[2:] == 'set':
      print( '[#] Must supply coordinates.' )

    elif p[2:6] == 'set ':

      # Attempt casting coordinates
      try:
        block_coords = g_pos.copy().a( int( p[ 6: ].split( ' ' )[0] ), int( p[ 6: ].split( ' ' )[1] ) )
      except Exception:
        print( "[#] Invalid coordinates." )
      else:

        # Make sure coordinates are within world border
        if block_coords.x < 0 or block_coords.y < 0 or block_coords.x >= g_world_size.x or block_coords.y > g_world_size.y:
          print( 'Those coordinates are out of this world!\n(No, really)')

        # Make sure they gave a block ID
        elif not ( len( p[ 6: ].split( ' ' ) ) == 3 and p[ 6: ].split( ' ' )[2] != '' ):
          print( '[#] Incorrect number of arguments.' )

        # Update the block
        else:
          g_tile_data[ xy2c( *block_coords.l(), g_world_size.x ) ] = p_def[ 6: ].split( ' ' )[2]
          data_save()
          print( f"[!] Set block to ID '{ p_def[ 6: ].split( ' ' )[2] }'" )
          goto_room( room_scene )

    # Fight monster
    elif p[2:] == 'fight':
      print( '[#] Must supply monster ID.' )

    elif p[2:8] == 'fight ':

      # Check monster ID
      if p[8:] not in Monster.TYPES:
        print( '[#] Invalid monster ID.' )
      else:
        start_fight( p[8:] )

    # Invalid input
    else:
      print( '[#] Unknown debug sub-command.' )

  # Invalid input
  else:
    print( '[#] Unknown command.' )

  return False

# Inventory Room
def room_inventory( arg = "" ):

  global g_items_extra

  # Args can be set to 1 to avoid re-printing room data
  if not ( len( arg ) > 0 and arg[0] == '1' ):
    
    # Print items in a grid-like pattern
    print_line()
    print( 'Inventory:' )
    for i in range( 16 ):
      j = i // 2 + ( i % 2 ) * 8
      item_string = f"({ '1234567890ABCDEF'[j] }) "
      item_string += ( '* ' if g_slot == j else '' ) + ( item_meta( j, c = 1 ) if g_items[j][1] != 0 else '...' )
      item_string += f"  x{ g_items[j][1] }" if g_items[j][1] != 0 else ''
      item_string = item_string[:38]
      print( item_string + ' ' * ( 40 - len( item_string ) ), end = ( '' if j < 8 else '\n' ) )
    print()

    # Print options
    if len( g_items_extra ) > 0:
      extra_item_amount = 0
      for i in g_items_extra:
        extra_item_amount += i[1]
      print( f'[H] Claim hidden items (x{ extra_item_amount } total)' )
    print( '[I] Get info' )
    print( '[M] Move item' )
    print( '[T] Trash item' )
    print( '[C] Open crafting' )
    print( '[Q] Close' )

  while True:
    p = input( '> ' ).lower()

    # Hidden items
    if p == 'h' and len( g_items_extra ) > 0:

      # Iterate through each item
      for i in g_items_extra.copy():

        # Attempt to give it to the player, and remove it from their extra items
        if update_inv( i[0], i[1], allow_stash = False ):
          g_items_extra.remove( i )

      # Show error message if at least some extra items are still there
      if len( g_items_extra ) > 0:
        print( '[#] You inventory was too full to claim every item.' )

      # Save modified items_extra and reload room
      data_save()
      goto_room( room_inventory )

    # Info
    elif p == 'i':

      # Make sure inventory isn't empty
      # Without this check, there would be a possibility of getting softlocked
      for i in range( 16 ):
        if g_items[i][1] != 0:
          break
      else:
        print( '[#] Your inventory is empty.' )
        goto_room( room_inventory, '1' )

      # Get slot:
      print( 'Enter the item you want to get info for:' )
      while True:
        p = input( '> ' ).upper()

        # Make sure it matches a slot
        if p not in list( '1234567890ABCDEF' ):
          print( '[#] Enter a number from 0-9 or a letter from A-F.' )

        # Make sure it has an item in it
        elif g_items[ list( '1234567890ABCDEF' ).index( p ) ][1] == 0:
          print( '[#] This slot is empty.' )

        # Print item info and re-show inventory
        else:
          print( "[?] Item: " + item_meta( list( '1234567890ABCDEF' ).index( p ), 0, c = 1 ) )
          print( "[?] Description:" )
          for l in item_meta( list( '1234567890ABCDEF' ).index( p ), 1, c = 1 ).split( ' ## ' ):
            print( '- ' + l )
          goto_room( room_inventory, '1' )

    # Move
    elif p == 'm':

      # Make sure inventory isn't empty
      # Without this check, there would be a possibility of getting softlocked
      for i in range( 16 ):
        if g_items[i][1] != 0:
          break
      else:
        print( '[#] Your inventory is empty.' )
        goto_room( room_inventory, '1' )

      # Get slot:
      print( 'Enter the item you want to move:' )
      old_p = ''
      while True:
        p = input( '> ' ).upper()

        # Make sure it matches a slot
        if p not in list( '1234567890ABCDEF' ):
          print( '[#] Enter a number from 0-9 or a letter from A-F.' )

        # Make sure source slot has an item in it
        elif old_p == '' and g_items[ list( '1234567890ABCDEF' ).index( p ) ][1] == 0:
          print( '[#] This slot is empty.' )

        # Set source slot and move onto getting destination slot
        elif old_p == '':
          print( 'Enter the slot you want to move it to:' )
          old_p = p

        # Move item and re-show inventory
        else:

          # Shorten indices/store swap buffer
          old_p = list( '1234567890ABCDEF' ).index( old_p )
          p = list( '1234567890ABCDEF' ).index( p )
          swap_buffer = g_items[old_p].copy()

          # Swap, print message, and re-show inventory
          update_inv( *g_items[p], mode = 's', slot = old_p )
          update_inv( *swap_buffer, mode = 's', slot = p )
          print( f'[!] Moved "{ item_meta( p, c = 1 ) }".' if g_items[old_p][1] == 0 else f'[!] Swapped "{ item_meta( p, c = 1 ) }" and "{ item_meta( old_p, c = 1 ) }"' )
          goto_room( room_inventory )

    # Trash
    elif p == 't':

      # Make sure inventory isn't empty
      # Without this check, there would be a possibility of getting softlocked
      for i in range( 16 ):
        if g_items[i][1] != 0:
          break
      else:
        print( '[#] Your inventory is empty.' )
        goto_room( room_inventory, '1' )

      # Get slot:
      print( 'Enter the item you want to trash:' )
      while True:
        p = input( '> ' ).upper()

        # Make sure it matches a slot
        if p not in list( '1234567890ABCDEF' ):
          print( '[#] Enter a number from 0-9 or a letter from A-F.' )

        # Make sure it has an item in it
        elif g_items[ list( '1234567890ABCDEF' ).index( p ) ][1] == 0:
          print( '[#] This slot is empty.' )

        # Make sure the item isn't a pickaxe
        elif g_items[ list( '1234567890ABCDEF' ).index( p ) ][0] == 2:
          print( '[#] "Copper Pickaxe" cannot be trashed!' )
          goto_room( room_inventory, '1' ) # Quit option to prevent softlock

        # Trash the item, and re-show inventory
        else:
          p = list( '1234567890ABCDEF' ).index( p )
          print( f'[!] Trashed item "{ item_meta( p, c = 1 ) }"' )
          update_inv( 0, 0, mode = 's', slot = p )
          goto_room( room_inventory )

    # Crafting
    elif p == 'c':
      goto_room( room_crafting )

    # Back
    elif p == 'q':
      goto_room( room_scene )

    # Invalid input
    else:
      print( '[#] Unknown command.' )

# Crafting room
def room_crafting( arg = '' ):

  # Store recipes object
  RECIPES = [
    { 'req': { I_WOOD: 1, I_GEL: 1 }, 'res': [ I_TORCH, 3 ] },
    { 'req': { I_WOOD: 1, I_STONE: 1 }, 'res': [ I_ARROW, 5 ] },
    { 'req': { I_ARROW: 5, I_TORCH: 1 }, 'res': [ I_F_ARROW, 5 ] },
    { 'req': { I_WOOD: 5 }, 'res': [ I_PLATFORM, 2 ] },
    { 'req': { I_WOOD: 12, I_IRON_BAR: 2 }, 'res': [ I_CHEST, 1 ] },
    { 'req': { I_IRON_ORE: 3 }, 'res': [ I_IRON_BAR, 1 ] },
    { 'req': { I_SILVER_ORE: 3 }, 'res': [ I_SILVER_BAR, 1 ] },
    { 'req': { I_GOLD_ORE: 3 }, 'res': [ I_GOLD_BAR, 1 ] },
    { 'req': { I_WOOD: 8, I_IRON_BAR: 8 }, 'res': [ I_I_SWORD, 1 ] },
    { 'req': { I_WOOD: 8, I_SILVER_BAR: 8 }, 'res': [ I_S_SWORD, 1 ] },
    { 'req': { I_WOOD: 8, I_GOLD_BAR: 8 }, 'res': [ I_G_SWORD, 1 ] },
    { 'req': { I_WOOD: 12 }, 'res': [ I_W_BOW, 1 ] },
    { 'req': { I_IRON_BAR: 6 }, 'res': [ I_I_BOW, 1 ] },
    { 'req': { I_SILVER_BAR: 6 }, 'res': [ I_S_BOW, 1 ] },
    { 'req': { I_GOLD_BAR: 30 }, 'res': [ I_G_BOW, 1 ] },
    { 'req': { I_IRON_BAR: 30 }, 'res': [ I_I_ARMOR, 1 ] },
    { 'req': { I_SILVER_BAR: 30 }, 'res': [ I_S_ARMOR, 1 ] },
    { 'req': { I_GOLD_BAR: 30 }, 'res': [ I_G_ARMOR, 1 ] },
    { 'req': { I_FEATHER: 18 }, 'res': [ I_HARPY_WINGS, 1 ] },
    { 'req': { I_LENS: 6 }, 'res': [ I_SUS_EYE, 1 ] }
  ]

  # Try extracting page from argument
  page = ( 0 if not ( len( arg ) > 1 ) else int( arg[1:] ) )

  # Args can be set to 1 to avoid re-printing room data
  if not ( len( arg ) > 0 and arg[0] == '1' ):

    # Print options
    print_line()
    print( 'Crafting:' )
    for i in range( page * 8, min( page * 8 + 8, len( RECIPES ) ) ):
      print( f"({ i % 8 + 1 }) { item_meta( RECIPES[ i ][ 'res' ][ 0 ] ) }  x{ RECIPES[ i ][ 'res' ][ 1 ] }" )
    print( f'(Page { page + 1 }/{ len( RECIPES ) // 8 + 1 })' )
    print()
    if page > 0:
      print( '[P] Previous Page' )
    if page * 8 + 8 < len( RECIPES ):
      print( '[N] Next Page' )
    print( '[I] Get ingredients' )
    print( '[C] Craft' )
    print( '[Q] Close' )

  while True:
    p = input( '> ' ).lower()

    # Previous page
    # (Only go if not on the first page of recipes)
    if p == 'p' and page > 0:
      goto_room( room_crafting, ' ' + str( page - 1 ) )

    elif p == 'p':
      print( '[#] Cannot go back any further.' )

    # Next page
    # (Only go if not on the final page of recipes)
    elif p == 'n' and page * 8 + 8 < len( RECIPES ):
      goto_room( room_crafting, ' ' + str( page + 1 ) )

    elif p == 'n':
      print( '[#] Cannot go forward any further.' )

    # Get ingredients/craft
    elif p == 'i' or p == 'c':

      i_or_c = p # Store in a temporary variable

      # Get slot
      print( 'Enter the recipe you want ' + ( 'the ingredients of' if p == 'i' else 'to use' ) + ':' )
      while True:
        p = input( '> ' ).lower()

        # Attempt cast
        try:
          p = int( p )
        except ValueError:
          print( '[#] Enter a number.' )
        else:

          # Make sure slot is within range
          if not ( 0 <= p - 1 < ( min( page * 8 + 8, len( RECIPES ) ) - ( page * 8 ) ) ):
            print( '[#] Invalid slot ID.' )
          else:
            break
      
      # Show ingredients
      if i_or_c == 'i':

        slot_num = page * 8 + ( p - 1 ) # Shortening selected slot
  
        # Print data
        print( f"Required ingredients for \"{ item_meta( RECIPES[slot_num]['res'][0] ) }\":" )
        for i in RECIPES[slot_num]['req']:
          print( f"- { item_meta( i ) } x{ RECIPES[slot_num]['req'][i] }" )
  
        # Reload room
        goto_room( room_crafting, '1' + str( page ) )

      # Alternatively, craft the item
      elif i_or_c == 'c':

        slot_num = page * 8 + ( p - 1 ) # Shortening selected slot

        # Get the quantity
        print( 'Enter the number of times you want to craft it:' )
        while True:
          p = input( '> ' )

          # Attempt cast
          try:
            p = int( p )
          except ValueError:
            print( '[#] Enter a number.' )
          else:

            # Test range
            if p == 0:
              print( '[!] Canceled crafting.' )
              goto_room( room_crafting, '1' + str( page ) )

            elif not ( 0 < p <= 2048 ):
              print( '[#] Out of range.' )

            else:
              break

        can_craft = True

        # Iterate through required materials, seeing which are missing
        for i in RECIPES[slot_num]['req']:
          if update_inv( i, 0, mode = 't' ) < RECIPES[slot_num]['req'][i] * p:
            can_craft = False
            print( f"[#] You need { RECIPES[slot_num]['req'][i] * p - update_inv( i, 0, mode = 't' ) } more \"{ item_meta( i ) }\"." )

        # Continue onward if they have all the items
        if can_craft:

          # Take the ingredients, then give them the resultant item
          for i in RECIPES[slot_num]['req']:
            update_inv( i, RECIPES[slot_num]['req'][i] * p, mode = 'r' )
          update_inv( RECIPES[slot_num]['res'][0], RECIPES[slot_num]['res'][1] * p, mode = 'p' )

          print( f"[!] You crafted \"{ item_meta( RECIPES[slot_num]['res'][0] ) }\" x{ RECIPES[slot_num]['res'][1] * p }." )

          # Reload room
          goto_room( room_crafting, '!' + str( page ) )

        else:

          # Reload room
          goto_room( room_crafting, '1' + str( page ) )

      else:
        print( 'This will never happen.' )

    # Quit
    elif p == 'q':
      goto_room( room_scene )

    # Invalid input
    else:
      print( '[#] Unknown command.' )

# Chest UI
def room_chest( arg = '' ):

  global g_items, g_tile_special

  # Make sure coordinates are supplied/valid
  if not ( len( arg.split( ',' ) ) == 3 ):
    print( 'ERROR: Chest data not supplied.' )
    goto_room( 0 )

  chest_coords = V2( int( arg.split( ',' )[1] ), int( arg.split( ',' )[2] ) )
  if f'{ chest_coords.x } : { chest_coords.y }' not in g_tile_special:
    print( 'ERROR: Chest not at block.' )
    goto_room( 0 )
  
  # Args can be set to 1 to avoid re-printing room data
  if not ( len( arg ) > 0 and arg[0] == '1' ):

    # Print items in a grid-like pattern
    print_line()
    print( 'Chest:' )
    for i in range( 10 ):
      j = i // 2 + ( i % 2 ) * 5
      item_string = f"({ '1234567890'[j] }) "
      item_string += ( item_meta( chest_slot( *chest_coords.l(), j ) ) if chest_slot( *chest_coords.l(), j, amount = True ) != 0 else '...' )
      item_string += f"  x{ chest_slot( *chest_coords.l(), j, amount = True ) }" if chest_slot( *chest_coords.l(), j, amount = True ) != 0 else ''
      item_string = item_string[:38]
      print( item_string + ' ' * ( 40 - len( item_string ) ), end = ( '' if j < 5 else '\n' ) )
    print()

    # Also print inventory for reference
    print( 'Inventory:' )
    for i in range( 16 ):
      j = i // 2 + ( i % 2 ) * 8
      item_string = f"({ '1234567890ABCDEF'[j] }) "
      item_string += ( '* ' if g_slot == j else '' ) + ( item_meta( j, c = 1 ) if g_items[j][1] != 0 else '...' )
      item_string += f"  x{ g_items[j][1] }" if g_items[j][1] != 0 else ''
      item_string = item_string[:38]
      print( item_string + ' ' * ( 40 - len( item_string ) ), end = ( '' if j < 8 else '\n' ) )
    print()

    print( '[I] Insert item' )
    print( '[T] Take item' )
    print( '[Q] Close' )

  while True:
    p = input( '> ' ).lower()

    # Insert item
    if p == 'i':

      # Make sure inventory isn't empty
      for i in range( 16 ):
        if g_items[i][1] != 0:
          break
      else:
        print( '[#] Your inventory is empty.' )
        goto_room( room_chest, '1' + arg[1:] )

      # Get slot:
      print( 'Enter the item you want to put in the chest:' )
      while True:
        p = input( '> ' ).upper()

        # Make sure it matches a slot
        if p not in list( '1234567890ABCDEF' ):
          print( '[#] Enter a number from 0-9 or a letter from A-F.' )

        # Make sure it has an item in it
        elif g_items[ list( '1234567890ABCDEF' ).index( p ) ][1] == 0:
          print( '[#] This slot is empty.' )

        else:

          # Get count
          slot_num = list( '1234567890ABCDEF' ).index( p )
          print( 'Enter how much you want to put in: ' )
          while True:
            p = input( '> ' ).lower()

            # Attempt cast
            try:
              p = abs( int( p ) )
            except ValueError:
              print( '[#] Enter a number.' )
            else:

              # Attempt to insert item (reload chest)
              if chest_modify( *chest_coords.l(), g_items[slot_num][0], min( g_items[slot_num][1], p ) ):
                g_items[slot_num][1] -= min( g_items[slot_num][1], p )
                goto_room( room_chest, '0' + arg[1:] )

              else:
                print( '[#] This chest is full.' )
                goto_room( room_chest, '1' + arg[1:] )

    # Take item
    elif p == 't':

      # Make sure chest isn't empty
      for i in range( 10 ):
        if chest_slot( *chest_coords.l(), i ) != 0:
          break
      else:
        print( '[#] This chest is empty.' )
        goto_room( room_chest, '1' + arg[1:] )

      # Get slot:
      print( 'Enter the item you want to take:' )
      while True:
        p = input( '> ' ).upper()

        # Make sure it matches a slot
        if p not in list( '1234567890' ):
          print( '[#] Enter a number from 0-9.' )

        # Make sure it has an item in it
        elif chest_slot( *chest_coords.l(), list( '1234567890' ).index( p ), amount = True ) == 0:
          print( '[#] This slot is empty.' )

        else:

          # Get count
          slot_num = list( '1234567890' ).index( p )
          print( 'Enter how much you want to take: ' )
          while True:
            p = input( '> ' ).lower()

            # Attempt cast
            try:
              p = abs( int( p ) )
            except ValueError:
              print( '[#] Enter a number.' )
            else:

              # Attempt to take item (reload chest)
              if update_inv( chest_slot( *chest_coords.l(), slot_num ), min( chest_slot( *chest_coords.l(), slot_num, amount = True ), p ) ):
                chest_slot( *chest_coords.l(), slot_num, chest_slot( *chest_coords.l(), slot_num, amount = True ) - min( chest_slot( *chest_coords.l(), slot_num, amount = True ), p ), amount = True, op = '=' )
                goto_room( room_chest, '0' + arg[1:] )

              else:
                print( '[#] Your inventory is full.' )
                goto_room( room_chest, '1' + arg[1:] )

    # Quit
    elif p == 'q':
      goto_room( room_scene )

    # Invalid input
    else:
      print( '[#] Unknown command.' )

def room_fight( arg = '' ):

  global g_monster, g_hp

  # PLAYER TURN
  if not ( len( arg ) > 0 and arg[0] == '1' ):
    print_line()
    print( f'You: { g_hp } HP' )
    print( f"{ g_monster.name.replace( '_', ' ' ).title() }: { g_monster.hp } HP" )
    allowed_inputs = g_monster.get_options( player_turn = True )
    if update_inv( I_HEALTH_POTION, 0, 't' ) >= 1:
      print( '[H] Drink health potion' )
    print( '[N] Do nothing' )
    print( '[*] Pause' )

    # Get inputs
    while True:
      p = input( '> ' ).lower()

      # Pause
      if p == '*':
        goto_room( room_pause, 'goto_room( room_fight )' )

      # Heal
      elif p == 'h' and update_inv( I_HEALTH_POTION, 0, 't' ) >= 1:
        print( '[!] You used a healing potion.' )
        print( f'[*] YOU: +{ min( g_hp + 100, g_hp_max ) - g_hp } HP' )
        g_hp = min( g_hp + 100, g_hp_max )
        g_monster.turn( 'n', player_turn = True )
        break

      # Turn
      elif p in allowed_inputs:
        g_monster.turn( p, player_turn = True )
        break

      # Invalid input
      else:
        print( '[#] Unknown command.' )

  # ENEMY TURN
  print_line()
  print( f'You: { g_hp } HP' )
  print( f"{ g_monster.name.replace( '_', ' ' ).title() }: { g_monster.hp } HP" )
  allowed_inputs = g_monster.get_options( player_turn = False )
  print( '[!] Attempt escape' )
  print( '[*] Pause' )

  # Get inputs
  while True:
    p = input( '> ' ).lower()

    # Pause
    if p == '*':
      goto_room( room_pause, 'goto_room( room_fight, \'1\' )' )

    # Escape
    elif p == '!':
      if random.randint( 1, 15 ) <= ( 5 if update_inv( I_SHACKLE, 0, mode = 't' ) == 0 else 12 ):
        print( '[!] You successfully escaped.' )
        input( '[!] Press enter to exit the fight. ' )
        goto_room( room_scene )
      else:
        print( '[!] Your attempt to escape was unsuccessful.' )
        g_monster.turn( '!', player_turn = False )
      break

    # Turn
    elif p in allowed_inputs:
      g_monster.turn( p, player_turn = False )
      break

    # Invalid input
    else:
      print( '[#] Unknown command.' )

  # Save player data
  data_save()

  goto_room( room_fight )

def room_bossfight():

  global g_monster, g_hp

  # PLAYER TURN
  print_line()
  print( f'You: { g_hp } HP' )
  print( f"Eye of Cthulhu: { g_monster.hp } HP" )
  allowed_inputs = g_monster.get_options( player_turn = True )
  print( '\n(CHOOSE A 3-MOVE COMBO)\n' )
  print( '[*] Pause' )

  # Get inputs
  while True:
    p = input( '> ' ).lower()

    # Pause
    if p == '*':
      goto_room( room_pause, 'goto_room( room_bossfight )' )

    # Turn
    elif len( p.split( ' ' ) ) == 3 and False not in [ i in allowed_inputs for i in p.split( ' ' ) ]:
      g_monster.turn( p, player_turn = True )
      break

    elif len( p.split( ' ' ) ) != 3:
      print( '[#] Enter 3 moves separated by spaces.' )

    # Invalid input
    else:
      print( '[#] Unknown command.' )

  # ENEMY TURN
  print_line()
  print( f'You: { g_hp } HP' )
  print( f"Eye of Cthulhu: { g_monster.hp } HP" )
  allowed_inputs = g_monster.get_options( player_turn = False )
  print( '[*] Pause' )

  # Get inputs
  while True:
    p = input( '> ' ).lower()

    # Pause
    if p == '*':
      goto_room( room_pause, 'goto_room( room_bossfight )' )

    # Escape
    elif p == '!':
      print( '[!] There is no escape.' )

    # Turn
    elif p in allowed_inputs:
      g_monster.turn( p, player_turn = False )
      break

    # Invalid input
    else:
      print( '[#] Unknown command.' )

  # Save player data
  data_save()

  goto_room( room_bossfight )

def room_death():

  global g_hp, g_pos, g_deaths

  g_deaths += 1

  print_line()
  time.sleep( 1 )
  for c in 'You were slain...':
    print( c, end = '', flush = True )
    time.sleep( 0.3 )

  time.sleep( 1.5 )
  print()
  
  for i in range( 5, 0, -1 ):
    print( f'Respawning in {i} second{ "s" if i != 1 else "" }.     ', end = '\r' )
    time.sleep( 1 )
  print( 'Respawning!' + ' ' * 20 )

  g_hp = g_hp_max
  g_pos = g_spawn

  goto_room( room_scene )

# Pause room
def room_pause( arg = '' ):

  # Show options
  print_line()
  print( '[Q] Return to menu' )
  print( '[X] Return to game' )

  while True:
    p = input( '> ' ).lower()

    # Quit
    if p == 'q':

      # Save data
      data_save()

      # Return
      print( '[!] Returned to menu.' )
      goto_room( room_menu )

    # Unpause
    elif p == 'x':
      print( '[!] Returned to game.' )
      if arg == '':
        goto_room( room_scene )
      else:
        exec( arg )

    # Invalid input
    else:
      print( '[#] Unknown command.' )

#
# ENTER MAIN LOOP
#
def run():

  # Load global data
  data_main_load()

  # Start in menu room
  room = room_menu
  arg = ""

  # Listen for crashes
  try:

    while True:

      # Move between rooms
      try:
        if arg == "":
          room()
        else:
          room( arg )
      except MoveException as m:
        room = m.room
        arg = m.arg
        if room == 0:
          break # Exit loop if user quit the game

  # Print crash message
  except Exception:
    print( '[CRASH]' )
    print( traceback.format_exc() )
    print( 'Oops, looks like you\'ve found a bug.' )
    print( 'Send me an email about it (macropixelyt@gmail.com), and I\'ll fix it as soon as possible.\n' )

  # Wait for input before ending program
  # (Windows consoles automatically close upon the end of a program,
  # which isn't helpful if I want to be able to read a crash message.)
  input( 'Press enter to exit.' )

run()
