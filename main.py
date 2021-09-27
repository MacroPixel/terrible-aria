import os
from math import sin, cos
import random
import traceback
import time

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
  if c == 'c': return g_tmap[ 'chest' ]
  return '?'

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

# Base Monster class
class Monster:

  def __init__( self ):

    self.hp = 1
    self.name = 'MISSING'

  # Deals damage to self, allowing a random range and multiplier to be used
  def damage( self, a, b = 'NONE', m = 1, entity = 'self' ):

    global g_hp

    if b == 'NONE':
      amount = a
    else:
      amount = random.randint( a, b )

    # m (multiplier) is used for stronger weapons/armor
    amount *= m
    if entity == 'self':
      self.hp -= amount
    else:
      g_hp -= amount
    return amount

  # Checks if either entity has died
  def hp_check( self ):

    if self.hp <= 0:
      print_line()
      print( f'[!] { self.name } was killed.' )
      input( '[!] Press enter to exit the fight. ' )
      goto_room( room_scene )

    if g_hp <= 0:
      print_line()
      print( f'[!] { self.name } won.' )
      input( '[!] Press enter to exit the fight. ' )
      goto_room( room_death )

class MonsterSlime( Monster ):

  def __init__( self ):

    self.hp = 50
    self.name = 'Slime'

    self.attack = random.choice( ( 0, 1 ) )

  def get_options( self, player_turn, should_print = True ):

    # Player offensive
    if player_turn:
      print( '[S] Swing sword' )
      print( '[F] Shoot forward' )
      print( '[U] Shoot upward' )
      return ( 's', 'f', 'u' )

    # Player defensive
    else:
      print( '[B] Move backward' )
      print( '[F] Move forward' )
      print( '[S] Stay stationary' )
      return ( 'b', 'f', 's' )

  # They player's turn is defined here because it depends on the monster's behavior
  def player_turn( self, p ):

    # Swing sword
    if p == 's':

      if self.attack == 0: # Jump
        print( '[!] The enemy jumped over your sword.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Sit
        print( '[!] You attacked the enemy.' )
        print( f'[*] Enemy: -{ self.damage( 12, 24 ) } HP' )

    # Shoot forward
    elif p == 'f':

      if self.attack == 0: # Jump
        print( '[!] The enemy jumped over your arrow.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Sit
        print( '[!] The enemy stayed stationary and was hit by your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )

    # Shoot upward
    elif p == 'u':

      if self.attack == 0: # Jump
        print( '[!] The enemy jumped into your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )
      if self.attack == 1: # Sit
        print( '[!] The enemy stayed stationary, so your arrow missed.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Check if either entity died
    self.hp_check()

  # The enemy's turn to attack
  def turn( self, p ):
    
    # Move backward/forward
    if p == 'b' or p == 'f':

      # Leap
      print( '[!] The enemy leaped onto you, but you moved out of the way.' )
      print( '[*] You: NO DAMAGE' )

    # Stay still
    elif p == 's':

      # Leap
      print( '[!] The enemy leaped onto you.' )
      print( f'[*] You: -{ self.damage( 8, 20, entity = "you" ) } HP' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack = 1 - self.attack

class MonsterZombie( Monster ):

  def __init__( self ):

    self.hp = 90
    self.name = 'Zombie'

    self.attack = random.choice( ( 0, 1 ) )
    self.attack_c = 1 if self.attack == 0 else 0

  def get_options( self, player_turn, should_print = True ):

    # Player offensive
    if player_turn:
      print( '[S] Swing sword' )
      print( '[F] Shoot forward' )
      print( '[U] Shoot upward' )
      return ( 's', 'f', 'u' )

    # Player defensive
    else:
      print( '[B] Move backward' )
      print( '[F] Move forward' )
      print( '[J] Jump' )
      return ( 'b', 'f', 'j' )

  # They player's turn is defined here because it depends on the monster's behavior
  def player_turn( self, p ):

    # Swing sword
    if p == 's':

      if self.attack == 0: # Jump
        print( '[!] The enemy jumped over your sword.' )
        print( f'[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Move back
        print( '[!] The enemy moved backward, but was still hit by your sword.' )
        print( f'[*] Enemy: -{ self.damage( 12, 24 ) } HP' )

    # Shoot forward
    elif p == 'f':

      if self.attack == 0: # Jump
        print( '[!] The enemy jumped over your arrow.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Move back
        print( '[!] The enemy moved backward, but was still hit by your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )

    # Shoot upward
    elif p == 'u':

      if self.attack == 0: # Jump
        print( '[!] The enemy jumped into your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )
      if self.attack == 1: # Move back
        print( '[!] The enemy moved backward, so your arrow missed.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack_c += 1
    if self.attack_c % 3 == 0:
      self.attack = 1 - self.attack

  # The enemy's turn to attack
  def turn( self, p ):
    
    # Move backward
    if p == 'b':

      if self.attack == 0: # Jump
        print( '[!] You moved backward, and the enemy jumped into you.' )
        print( f'[*] You: -{ self.damage( 12, 20, entity = "you" ) } HP' )
      if self.attack == 1: # Arm
        print( '[!] The enemy swung its arm, but you moved out of its reach.' )
        print( '[*] You: NO DAMAGE' )

    # Move forward
    elif p == 'f':

      if self.attack == 0: # Jump
        print( '[!] You run past the enemy while it was jumping.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 1: # Arm
        print( '[!] The enemy swing its arm, and you walked into it.' )
        print( f'[*] You: -{ self.damage( 6, 12, entity = "you" ) } HP' )

    # Jump
    elif p == 'j':

      if self.attack == 0: # Jump
        print( '[!] You and the enemy both jumped forward.' )
        print( f'[*] You: -{ self.damage( 10, 16, entity = "you" ) } HP' )
      if self.attack == 1: # Arm
        print( '[!] The enemy swung its arm, and you jumped over it.' )
        print( '[*] You: NO DAMAGE' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack_c += 1
    if self.attack_c % 3 == 0:
      self.attack = 1 - self.attack

class MonsterDemonEye( Monster ):

  def __init__( self ):

    self.hp = 70
    self.name = 'Demon Eye'

    self.attack = random.choice( ( 0, 1 ) )
    self.attack_c = 0
    self.attack_0 = self.attack

  def get_options( self, player_turn, should_print = True ):

    # Player offensive
    if player_turn:
      print( '[S] Jump and swing sword (*)' )
      print( '[R] Shoot rightward' )
      print( '[L] Shoot leftward' )
      return ( 's', 'r', 'l' )

    # Player defensive
    else:
      print( '[B] Move backward' )
      print( '[R] Move rightward' )
      print( '[L] Move leftward' )
      print( '[J] Jump (*)' )
      return ( 'b', 'r', 'l', 'j' )

  # They player's turn is defined here because it depends on the monster's behavior
  def player_turn( self, p ):

    # Jump and swing sword
    if p == 's':

      # Random chance
      if random.choice( ( True, False ) ):
        print( '[!] You jumped and hit the enemy with your sword.' )
        print( f'[*] Enemy: -{ self.damage( 12, 24 ) } HP' )
      else:
        print( '[!] You jumped, but barely missed the enemy.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Shoot rightward
    elif p == 'r':

      if self.attack == 0: # Fly right
        print( '[!] The enemy flew rightward and was hit by your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )
      if self.attack == 1: # Fly left
        print( '[!] The enemy flew leftward, so you arrow missed.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Shoot leftward
    elif p == 'l':

      if self.attack == 0: # Fly right
        print( '[!] The enemy flew rightward, so your arrow missed.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Fly left
        print( '[!] The enemy flew leftward and was hit by your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack_c += 1
    self.attack = ( self.attack_0 ) if ( self.attack_c % 6 in ( 0, 2, 3 ) ) else ( 1 - self.attack_0 )

  # The enemy's turn to attack
  def turn( self, p ):
    
    # Move backward
    if p == 'b':

      if self.attack == 0: # From front
        print( '[!] You moved backward, and the enemy flew into you.' )
        print( f'[*] You: -{ self.damage( 10, 18, entity = "you" ) } HP' )
      if self.attack == 1: # From side
        print( '[!] The enemy flew in from the side, and you dodged its attack.' )
        print( '[*] You: NO DAMAGE' )

    # Move rightward
    elif p == 'r':

      if self.attack == 0: # From front
        print( '[!] The enemy flew in from the front, and you dodged its attack.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 1: # From side
        print( '[!] You moved rightward, and the enemy flew into you.' )
        print( f'[*] You: -{ self.damage( 10, 18, entity = "you" ) } HP' )

    # Move leftward
    elif p == 'l':

      if self.attack == 0: # From front
        print( '[!] The enemy flew in from the front, and you dodged its attack.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 1: # From side
        print( '[!] You moved leftward, and the enemy flew into you.' )
        print( f'[*] You: -{ self.damage( 10, 18, entity = "you" ) } HP' )

    # Jump
    elif p == 'j':

      # Random chance
      if random.choice( ( True, False ) ):
        print( f'[!] The enemy flew in from the { "front" if self.attack == 0 else "side" }, and you jumped over it.' )
        print( '[*] You: NO DAMAGE' )
      else:
        print( f'[!] The enemy flew in from the { "front" if self.attack == 0 else "side" }, and you didn\'t jump over it in time.' )
        print( f'[*] You: -{ self.damage( 10, 18, entity = "you" ) } HP' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack_c += 1
    self.attack = ( self.attack_0 ) if ( self.attack_c % 6 in ( 0, 2, 3 ) ) else ( 1 - self.attack_0 )

class MonsterCaveBat( Monster ):

  def __init__( self ):

    self.hp = 40
    self.name = 'Cave Bat'

    self.attack = random.choice( ( 0, 1, 2 ) )
    self.attack_c = self.attack
    self.attack_0 = self.attack

  def get_options( self, player_turn, should_print = True ):

    # Player offensive
    if player_turn:
      print( '[S] Jump and swing sword' )
      print( '[F] Shoot forward' )
      print( '[R] Shoot rightward' )
      return ( 's', 'f', 'r' )

    # Player defensive
    else:
      print( '[J] Jump' )
      print( '[S] Stay stationary' )
      return ( 'j', 's' )

  # They player's turn is defined here because it depends on the monster's behavior
  def player_turn( self, p ):

    # Jump and swing sword
    if p == 's':

      if self.attack == 0: # Hover
        print( '[!] The enemy didn\'t move, so you jumped and hit it with your sword.' )
        print( f'[*] Enemy: -{ self.damage( 12, 24 ) } HP' )
      if self.attack == 1: # Fly sideways
        print( '[!] You jumped towards the enemy, but it flew sideways.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 2: # Fly upward
        print( '[!] You jumped towards the enemy, but it flew further away.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Shoot forward
    elif p == 'f':

      if self.attack == 0: # Hover
        print( '[!] The enemy didn\'t move, so your arrow hit it.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )
      if self.attack == 1: # Fly sideways
        print( '[!] You shot at the enemy, but it flew sideways.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 2: # Fly upward
        print( '[!] The enemy flew further away, but was still hit by your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )

    # Shoot rightward
    elif p == 'r':

      if self.attack == 0: # Hover
        print( '[!] The enemy didn\'t move, so your arrow flew to its right.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Fly sideways
        print( '[!] The enemy flew rightward into your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )
      if self.attack == 2: # Fly upward
        print( '[!] The enemy flew further away, and your arrow flew to its right.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack_c += ( 1 if self.attack_0 != 1 else -1 )
    self.attack = self.attack_c % 3

  # The enemy's turn to attack
  def turn( self, p ):
    
    # Jump
    if p == 'j':

      if self.attack == 0: # Missed
        print( '[!] The enemy flew towards you, but it missed.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 1: # Low attack
        print( '[!] You jumped, and the enemy flew under you.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 2: # High attack
        print( '[!] The enemy flew over you, and you jumped into it.' )
        print( f'[*] You: -{ self.damage( 10, 18, entity = "you" ) } HP' )

    # Stay stationary
    elif p == 's':

      if self.attack == 0: # Missed
        print( '[!] The enemy flew towards you, but it missed.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 1: # Low attack
        print( '[!] The enemy flew into you.' )
        print( f'[*] You: -{ self.damage( 10, 18, entity = "you" ) } HP' )
      if self.attack == 2: # High attack
        print( '[!] The enemy flew over you.' )
        print( '[*] You: NO DAMAGE' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack_c += ( 1 if self.attack_0 != 1 else -1 )
    self.attack = self.attack_c % 3

class MonsterSkeleton( Monster ):

  def __init__( self ):

    self.hp = 120
    self.name = 'Skeleton'

    self.attack = random.choice( ( 0, 1, 2, 3 ) )
    self.attack_c = 0
    self.attack_0 = self.attack

  def get_options( self, player_turn, should_print = True ):

    # Player offensive
    if player_turn:
      print( '[S] Swing sword (*)' )
      print( '[J] Jump and swing sword' )
      print( '[U] Shoot upward' )
      print( '[R] Shoot rightward' )
      print( '[L] Shoot leftward' )
      return ( 's', 'j', 'u', 'r', 'l' )

    # Player defensive
    else:
      print( '[J] Jump' )
      print( '[B] Move backward' )
      return ( 'j', 'b' )

  # They player's turn is defined here because it depends on the monster's behavior
  def player_turn( self, p ):

    # Swing sword
    if p == 's':

      if self.attack == 0: # Deflect
        print( '[!] You swung your sword at the enemy, but it absorbed your attack.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Jump
        if random.choice( ( True, False ) ):
          print( '[!] The enemy was about to jump, but you hit it with your sword.' )
          print( f'[*] Enemy: -{ self.damage( 12, 24 ) } HP' )
        else:
          print( '[!] You swung your sword at the enemy, but it jumped over it.' )
          print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 2: # Move rightward
        print( '[!] You swung your sword at the enemy, but it moved rightward.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 3: # Move leftward
        print( '[!] You swung your sword at the enemy, but it moved leftward.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Jump and swing sword
    if p == 'j':

      if self.attack == 0: # Deflect
        print( '[!] The enemy remained stationary, so you jumped over it.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Jump
        print( '[!] The enemy jumped, so you jumped and hit it with your sword.' )
        print( f'[*] Enemy: -{ self.damage( 16, 28 ) } HP' )
      if self.attack == 2: # Move rightward
        print( '[!] You jumped and swung, but the enemy dodged rightward.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 3: # Move leftward
        print( '[!] You jumped and swung, but the enemy dodged leftward.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Shoot upward
    if p == 'u':

      if self.attack == 0: # Deflect
        print( '[!] The enemy remained stationary, so your arrow missed it.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Jump
        print( '[!] The enemy jumped and was hit by your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )
      if self.attack == 2: # Move rightward
        print( '[!] You shot your arrow upward, but the enemy moved rightward.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 3: # Move leftward
        print( '[!] You shot your arrow upward, but the enemy moved leftward.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Shoot rightward
    if p == 'r':

      if self.attack == 0: # Deflect
        print( '[!] The enemy remained stationary, so your arrow missed it.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Jump
        print( '[!] You shot your arrow rightward, but the enemy jumped.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 2: # Move rightward
        print( '[!] The enemy moved rightward into your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )
      if self.attack == 3: # Move leftward
        print( '[!] You shot your arrow rightward, but the enemy moved leftward.' )
        print( '[*] Enemy: NO DAMAGE' )

    # Shoot leftward
    if p == 'l':

      if self.attack == 0: # Deflect
        print( '[!] The enemy remained stationary, so your arrow missed it.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 1: # Jump
        print( '[!] You shot your arrow leftward, but the enemy jumped.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 2: # Move rightward
        print( '[!] You shot your arrow leftward, but the enemy moved rightward.' )
        print( '[*] Enemy: NO DAMAGE' )
      if self.attack == 3: # Move leftward
        print( '[!] The enemy moved leftward into your arrow.' )
        print( f'[*] Enemy: -{ self.damage( 8, 16 ) } HP' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack_c += 1
    self.attack = ( ( 0, 1, 2, 3, 2, 1 )[ self.attack_c % 6 ] + self.attack_0 ) % 4

  # The enemy's turn to attack
  def turn( self, p ):
    
    # Jump
    if p == 'j':

      if self.attack == 0: # Charge toward
        print( '[!] The enemy charged toward you, and you jumped over it.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 1: # Jump on
        print( '[!] You and the enemy both jumped towards each other.' )
        print( f'[*] You: -{ self.damage( 18, 28, entity = "you" ) } HP' )
      if self.attack == 2: # Throw bone
        print( '[!] The enemy threw a bone at you, and you jumped over it.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 3: # Throw bone upward
        print( '[!] The enemy threw a bone upward, and you jumped into it.' )
        print( f'[*] You: -{ self.damage( 8, 18, entity = "you" ) } HP' )
    
    # Move backward
    if p == 'b':

      if self.attack == 0: # Charge toward
        print( '[!] The enemy charged toward you, and you didn\t back up far enough.' )
        print( f'[*] You: -{ self.damage( 20, 40, entity = "you" ) } HP' )
      if self.attack == 1: # Jump on
        print( '[!] The enemy tried to jump on you, but you moved backwards.' )
        print( '[*] You: NO DAMAGE' )
      if self.attack == 2: # Throw bone
        print( '[!] The enemy threw a bone, and it hit you.' )
        print( f'[*] You: -{ self.damage( 8, 18, entity = "you" ) } HP' )
      if self.attack == 3: # Throw bone upward
        print( '[!] The enemy threw a bone upward, and it missed you.' )
        print( '[*] You: NO DAMAGE' )

    # Check if either entity died
    self.hp_check()

    # Progress attack
    self.attack_c += 1
    self.attack = ( ( 0, 1, 2, 3, 2, 1 )[ self.attack_c % 6 ] + self.attack_0 ) % 4

# Switches rooms
def goto_room( room, arg = '' ):
  raise MoveException( room, arg )

# Prints line
def print_line():
  print( '- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -' )

# Prints the worldgen progress
# I don't think it's important to explain what the arguments do
def print_progress( prog, div_this, div_total, s ):

  t = int( prog )
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
  s = 0
  for i in range( 12 ):
    s += random.randrange( 3, 12 ) * sin( x / random.randrange( 6, 24 ) - random.randrange( 10, 80 ) )
  random.seed( next_seed )
  return s / 4;

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
I_ACORN = 25
I_GRENADE = 26
I_BOMB = 27

ITEM_META = [
  [ 'NULL', 'An item you shouldn\'t have' ],
  [ 'Copper Shortsword', 'Better than nothing!' ],
  [ 'Copper Pickaxe', 'The best pick in the game. (Also the only pick in the game).' ],
  [ 'Grass', 'Not useful for much, but you\'ll acquire it anyway.' ],
  [ 'Stone', 'The most prevalent material in the world.' ],
  [ 'Wood', 'A reliable building block.' ],
  [ 'Iron Ore', 'An ore.' ],
  [ 'Silver Ore', 'An ore.' ],
  [ 'Gold Ore', 'An ore.' ],
  [ 'Iron Bar', 'A bar.' ],
  [ 'Silver Bar', 'A bar.' ],
  [ 'Gold Bar', 'A bar.' ],
  [ 'Wooden Sword', 'Description' ],
  [ 'Iron Sword', 'Description' ],
  [ 'Silver Sword', 'Description' ],
  [ 'Golden Sword', 'Description' ],
  [ 'Wooden Bow', 'Description' ],
  [ 'Iron Bow', 'Description' ],
  [ 'Silver Bow', 'Description' ],
  [ 'Golden Bow', 'Description' ],
  [ 'Torch', 'Description' ],
  [ 'Arrow', 'Description' ],
  [ 'Flaming Arrow', 'Description' ],
  [ 'Wooden Platform', 'Description' ],
  [ 'Chest', 'Description' ],
  [ 'Acorn', 'Description' ],
  [ 'Grenade', 'Description' ],
  [ 'Bomb', 'Description' ]
]

# GLOBAL CONSTANTS
DEBUG = True
SHOW_PROG = False
AIR_BLOCKS = [ ' ', 'l', 'L' ]
ITEM_BLOCKS = { 'g': I_GRASS, 's': I_STONE, 'w': I_WOOD, 'i': I_IRON_ORE, 'S': I_SILVER_ORE, 'G': I_GOLD_ORE }
MONSTERS = [ 'slime', 'zombie', 'demon_eye', 'cave_bat' ]

# GLOBAL VARIABLES
g_data = {}
g_cname = ''
g_wname = ''
g_pos = V2( 0, 0 )
g_view = V2( 0, 0 )
g_world_size = V2( 0, 0 )
g_seed = 0
g_hp = 0
g_hp_max = 0
g_items = []
g_slot = 0
g_play_time = 0
g_tile_data = []
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
  'chest': '©'
}
g_monster = 0

# Initialize the data file if it doesn't exist
def data_main_init():

  file = open( 'data.txt', 'w', encoding = 'utf-8' )
  file.write( 'characters: \n' )
  file.write( 'worlds: \n' )
  file.write( 'blocks: player=Δ;air= ;grass=~;stone=#;log=];leaves=*;iron=&;silver=$;gold=%;wood==;chest=©' )

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
  t = file[2][ 8: ].split( ';' )
  for s in t:
    g_tmap[ s.split( '=' )[0] ] = ( s.split( '=' )[1] if len( s.split( '=' ) ) != 3 else '=' )

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
  t = ''
  for b in g_tmap:
    t += ';' + b + '=' + g_tmap[b]
  file.write( '\nblocks: ' + t[1:] )

# Initialize a character file upon creation
def data_char_init( name ):

  # Open/write to file
  file = open( 'c_' + name + '.txt', 'w' )
  file.write( 'hp: 100,100\n' )
  file.write( 'items: 1:1,2:1,' ) # Defaults to sword/pickaxe
  for i in range( 14 ):
    file.write( '0:0' + ( ',' if i != 15 else '' ) )
  file.write( '\nplay_time: 0' )

# Load a character file with a given name
def data_char_load( name ):

  global g_hp, g_hp_max, g_items, g_play_time

  # Split file into statements/read HP data
  file = open( 'c_' + name + '.txt', 'r' ).read().split( '\n' )
  g_hp = int( file[0][4:].split( ',' )[0] )
  g_hp_max = int( file[0][4:].split( ',' )[1] )

  # Setup item array
  g_items = []
  t = file[1][7:].split( ',' )
  for i in range( 16 ):
    g_items.append( [ int( t[i].split( ':' )[0] ), int( t[i].split( ':' )[1] ) ] )

  update_inv( 0, 0, mode = '!' ) # Properly organizes inventory

  # ..also play time
  g_play_time = int( file[2][11:] )

# Write back to the character file if something changed
def data_char_update( name ):

  file = open( 'c_' + name + '.txt', 'w' )

  # Write HP data
  file.write( f'hp: { g_hp },{ g_hp_max }\n' )

  # Write item array
  file.write( 'items: ' )
  for i in range( 16 ):
    file.write( f'{ g_items[i][0] }:{ g_items[i][1] }' + ( ',' if i != 15 else '' ) )
  file.write( '\nplay_time: 0' )

def generate_world( size, seed ):

  # WORLDGEN PARAMETERS
  CAVES = True
  CAVES_FREQ = 32
  POCKETS = True
  POCKETS_FREQ = 128
  TREES = True
  ORES = True
  ORES_FREQ = 128

  global g_tile_data, g_pos

  # Clean slate
  g_tile_data = ''
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
    t = int( ( size.y / 2 ) + noise_top( i, seed ) )

    # 4 blocks of grass
    for j in range( t, t + 4 ):
      g_tile_data[ xy2c( i, j, size.x ) ] = 'g'

    # And everything under it is stone
    for j in range( t + 4, size.y ):
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

      progress = print_progress( progress, ORES_FREQ, 40, 'Generating ore veins' ) # Update progress
  else:
    progress = print_progress( progress, 1, 40, 'Generating ore veins' ) # Autofill progress if skipped

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

      progress = print_progress( progress, CAVES_FREQ, 20, 'Generating caves' ) # Update progress

  else:
    progress = print_progress( progress, 1, 20, 'Generating caves' ) # Autofill progress if skipped

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

        # Continue upward for a random height [10, 20]
        for i2 in range( random.randint( 10, 20 ) ):

          # Place down a log and move vector upward
          g_tile_data[ xy2c( o.x, o.y, size.x ) ] = 'l'
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

      # Choose how far to move before creating another tree
      i1 += int( random.randint( 8, 15 ) * random.choice( ( 0.6, 1, 1, 4 ) ) )

    progress = print_progress( progress, 1, 5, 'Generating trees' ) # Update progress
  else:
    progress = print_progress( progress, 1, 5, 'Generating trees' ) # Autofill progress if skipped

  # Lastly, position the player
  g_pos = V2( size.x // 2, int( ( size.y / 2 ) + noise_top( size.x // 2, seed ) ) - 1 )
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
  file.write( f'size: { size.x },{ size.y }\n')
  file.write( f'seed: { seed }\n')
  file.write( f'player_pos: { g_pos.x },{ g_pos.y }\n' )

  # Write tile data
  for j in range( size.y ):
    file.write( ''.join( g_tile_data[ ( j * size.x ):( ( j + 1 ) * size.x ) ] ) )
    file.write( '\n' )

# Load a world file with a given name
def data_world_load( name ):

  global g_pos, g_world_size, g_seed, g_tile_data, g_show_help, g_slot

  # Split file into statements
  file = open( 'w_' + name + '.txt', 'r' ).read().split( '\n' )

  # Read basic positional data
  g_world_size = V2( int( file[0][6:].split( ',' )[0] ), int( file[0][6:].split( ',' )[1] ) )
  g_seed = int( file[1][6:] )
  g_pos = V2( int( file[2][12:].split( ',' )[0] ), int( file[2][12:].split( ',' )[1] ) )

  # Read tile data
  g_tile_data = "";
  for j in range( g_world_size.y ):
    g_tile_data += file[3 + j]
  g_tile_data = list( g_tile_data )

  g_show_help = True # Shows a help message on your first turn in the world
  g_slot = 0 # Reset selected slot

# Write back to the world file if something changed
def data_world_update( name ):

  file = open( 'w_' + name + '.txt', 'w' )

  # Write non-tile data
  file.write( f'size: { g_world_size.x },{ g_world_size.y }\n')
  file.write( f'seed: { g_seed }\n')
  file.write( f'player_pos: { g_pos.x },{ g_pos.y }\n' )

  # Write tile data
  for j in range( g_world_size.y ):
    file.write( ''.join( g_tile_data[ ( j * g_world_size.x ):( ( j + 1 ) * g_world_size.x ) ] ) )
    file.write( '\n' )

# All room functions should be passed into the goto_room() function as a pointer object
# The starting room
def room_menu():

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

  # Keep looping until a valid input is provided
  while True:
    p = input( '> ' ).lower()

    # Play
    if p == 'p':
      goto_room( room_character_select )

    # Quit
    elif p == 'q':
      print( '[!] Game was closed.' )
      goto_room( 0 )

    # Error handling
    else:
      print( '[#] Unknown command.' )

# Character selection room
def room_character_select():

  global g_cname, g_data

  # Print options
  print_line()
  print( 'Characters:' )
  for i in range( len( g_data[ 'char_list' ] ) ):
    print( f'[{ i + 1 }] { g_data[ "char_list" ][i] }' )
  print( '[C] Create new character' )
  print( '[D] Delete chracter' )
  print( '[Q] Back' )

  while True:

    p = input( '> ' ).lower()

    # Create character
    if p == 'c':
      goto_room( room_character_create )

    # Back
    elif p == 'q':
      goto_room( room_menu )

    # Delete character
    elif p == 'd':

      # Get index
      print( 'Enter the character slot would like to delete:' )
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

            # Store name in a temp variable so I don't have to retype this mess ↓
            t = g_data[ 'char_list' ][ p - 1 ]

            # Make sure they actually want to
            print( f'Are you sure you want to delete character "{ t }"?' )
            print( 'Type "yes" to proceed.' )
            if input( '> ' ).lower() == 'yes':

              # Delete character file and update character list in data.txt
              print( '[!] Character deleted.' )
              if os.path.exists( 'c_' + t + '.txt' ):
                os.remove( 'c_' + t + '.txt' )
              g_data[ 'char_list' ].pop( p - 1 )
              data_main_update()

            # Re-show character list
            goto_room( room_character_select )

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
def room_character_create():

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
      goto_room( room_character_select )

# World selection room
def room_world_select():

  global g_wname, g_data

  # Print options
  print_line()
  print( 'Worlds:' )
  for i in range( len( g_data[ 'world_list' ] ) ):
    print( f'[{ i + 1 }] { g_data[ "world_list" ][i] }' )
  print( '[C] Create new world' )
  print( '[D] Delete world' )
  print( '[Q] Back' )

  while True:

    p = input( '> ' ).lower()

    # Create world
    if p == 'c':
      goto_room( room_world_create )

    # Back
    elif p == 'q':
      goto_room( room_character_select )

    # Delete world
    elif p == 'd':

      # Get index
      print( 'Enter the world slot would like to delete:' )
      while True:
        p = input( '> ' )

        # Attempt cast
        try:
          p = int( p )
        except ValueError:
          print( '[#] Must supply a number.' )

        else:

          print( p )

          # Too large/too small
          if not ( 0 < p <= len( g_data[ 'world_list' ] ) ):
            print( '[#] Out of range.' )

          else:

            # Store name in a temp variable so I don't have to retype this mess ↓
            t = g_data[ 'world_list' ][ p - 1 ]

            # Make sure they actually want to
            print( f'Are you sure you want to delete world "{ t }"?' )
            print( 'Type "yes" to proceed.' )
            if input( '> ' ).lower() == 'yes':

              # Delete world file and update world list in data.txt
              print( '[!] World deleted.' )
              if os.path.exists( 'w_' + t + '.txt' ):
                os.remove( 'w_' + t + '.txt' )
              g_data[ 'world_list' ].pop( p - 1 )
              data_main_update()

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

    # Continue to other options
    else:
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

  global g_pos, g_view, g_tile_data, g_show_help, g_slot, g_monster

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
      t = ''
      for i in range( g_view.x, g_view.x + 61 ):
        if i == g_pos.x and j == g_pos.y:
          t += g_tmap[ 'player' ] + ' '
        else:
          t += char2tile( g_tile_data[ xy2c( i, j, g_world_size.x ) ] ) + ' '
      print( t )

    # Show help options if loaded in for first time
    if g_show_help:
      print( '[H] Help' )
      print( '[H <command name>] Help with a specific command' )
      g_show_help = False

  while True:
    p_def = input( '> ' )
    p = p_def.lower()

    # Show generic help info
    if p == 'h':
      print( '[H] Show this screen' )
      print( '[H <command name>] Help with a specific command' )
      print( '[M] Move in direction' )
      print( '[J] Jump' )
      print( '[W] Wait' )
      print( '[I] Inventory' )
      print( '[S] Select Item' )
      print( '[B] Break' )
      print( '[P] Break' )
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
      elif p[2:] == 'b':
        print( '[?] Syntax: b <x> <y>' )
        print( '[?] Breaks the block x units right of the player and y units below the player.' )
        print( '[?] (Maximum is 4 blocks away in any direction.)' )
        print( '[?] Syntax: b <direction>' )
        print( '[?] Breaks the block 1 unit away from the player in the specified direction.' )
        print( '[?] (Accepted directions are "left", "right", "up", and "down".)' )
      elif p[2:] == 'p':
        print( '[?] Syntax: p <x> <y>' )
        print( '[?] Places the selected block x units right of the player and y units below the player.' )
        print( '[?] (Maximum is 4 blocks away in any direction.)' )
        print( '[?] Syntax: p <direction>' )
        print( '[?] Places the selected block 1 unit away from the player in the specified direction.' )
        print( '[?] (Accepted directions are "left", "right", "up", and "down".)' )
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
        print( '[?] Syntax: $ execute <code>' )
        print( '[?] Effect: Sends code to the Python interpreter.' )
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

          # Attempt cast
        try:
          if len( p.split( ' ' ) ) >= 3:
            int( p.split( ' ' )[2] )
        except Exception:
          print( '[#] Enter a number.' )

        else:

          # Get step count (defaulting to 1)
          t = 1 if len( p.split( ' ' ) ) <= 2 else int( p.split( ' ' )[2] )

          # Check range
          if not ( 0 < t <= 5 ):
            print( '[#] Step count out of range.' )

          # Move in given direction, run game tick, save data, and reload stage
          else:
            for i in range( t ):
              if ( 0 <= g_pos.x + ( 1 if p.split( ' ' )[1][0] == 'r' else -1 ) < g_world_size.x ):
                if get_tile( g_pos.x + ( 1 if p.split( ' ' )[1][0] == 'r' else -1 ), g_pos.y ) in AIR_BLOCKS:
                  g_pos.x += ( 1 if p.split( ' ' )[1][0] == 'r' else -1 )
            data_world_update( g_wname )
            tick()
            goto_room( room_scene )

    # Jump command
    elif p == 'j' or p[:2] == 'j ':

      # Get step number
      if len( p ) > 1:
        try:
          t = int( p[2:] )
        except ValueError:
          print( '[#] Enter a number.' )
          t = 'ERROR'
      else:
        t = 5

      if t != 'ERROR':

        # Check range
        if not ( 0 < t <= 5 ):
          print( '[#] Jump height out of range.' )

        # If not on block and not on floor, run game tick and reload stage
        elif g_pos.y + 1 < g_world_size.y and get_tile( g_pos.x, g_pos.y + 1 ) in AIR_BLOCKS:
          tick()
          goto_room( room_scene )

        # Jump, run game tick, save data, and reload stage
        else:
          for i in range( t ):
            if g_pos.y > 0 and get_tile( g_pos.x, g_pos.y - 1 ) in AIR_BLOCKS:
              g_pos.y -= 1
          data_world_update( g_wname )
          tick( nofall = True )
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

    # Break
    elif p == 'b':
      print( '[#] Must supply direction.' )

    elif p[:2] == 'b ' or p[:2] == 'p ':

      # Check if it is a direction
      if p[2:] in ( 'left', 'right', 'down', 'up', 'l', 'r', 'd', 'u' ):

        # Attempt to either break or place the block
        if p[0] == 'b':
          try_break_block( *( V2( -1, 0 ), V2( 1, 0 ), V2( 0, 1 ), V2( 0, -1 ) )[ ( 'l', 'r', 'd', 'u' ).index( p[2] ) ].l() )
        elif p[0] == 'p':
          try_place_block( *( V2( -1, 0 ), V2( 1, 0 ), V2( 0, 1 ), V2( 0, -1 ) )[ ( 'l', 'r', 'd', 'u' ).index( p[2] ) ].l() )
        else:
          print( 'ERROR: I messed something up' )

      # Check if it's coordiantes
      elif len( p[2:].split( ' ' ) ) == 2:

        try:
          p = [ int( p[2:].split( ' ' )[0] ), int( p[2:].split( ' ' )[1] ), p[0] ]
        except ValueError:
          print( '[#] Enter 2 numbers.' )

        else:

          # Check range
          # Temporary variables used for easier formatting
          t1 = ( -4 <= p[0] <= 4 )
          t2 = ( -4 <= p[1] <= 4 )
          if not ( t1 and t2 ):
            print( f"[#] { '' if t1 else 'X' }{ '' if t1 or t2 else ' and ' }{ '' if t2 else 'Y' } coordinate{ '' if t1 or t2 else 's' } out of range. (Valid range: [-4, 4].)" )

          # If both coordinates are valid, then continue onward
          if t1 and t2:

            # Attempt to either break or place the block
            if p[2] == 'b':
              try_break_block( p[0], p[1] )
            else:
              try_place_block( p[0], p[1] )

      # Invalid arguments
      else:
        print( '[#] Enter either a direction or a coordinate pair.' )

    # Debug command (requires debug mode)
    elif p == '$' and DEBUG:
      print( '[#] Must supply a sub-command.')

    elif p[:2] == '$ ' and DEBUG:

      # Jump to position
      if p[2:] == 'jump' or p[2:] == 'shift':
        print( '[#] Must supply coordinates.' )

      elif p[2:7] == 'jump ' or p[2:8] == 'shift ':

        # Attempt casting coordiantes
        try:
          t = V2( int( p[ ( 7 if p[2] == 'j' else 8 ): ].split( ' ' )[0] ), int( p[ ( 7 if p[2] == 'j' else 8 ): ].split( ' ' )[1] ) )
          if p[2] == 's':
            t.a( g_pos )
        except Exception:
          print( "[#] Invalid coordinates." )
        else:

          # Make sure coordinates are within world border
          if t.x < 0 or t.y < 0 or t.x >= g_world_size.x or t.y > g_world_size.y:
            print( 'Those coordinates are out of this world!\n(No, really)')
          else:
            g_pos = t
            data_world_update( g_wname )
            print( f'[!] Moved player to ({ t.x }, { t.y })' )
            goto_room( room_scene )

      # Give/remove item
      elif p[2:] == 'give' or p[2:] == 'take':
        print( '[#] Must supply item info.' )

      elif p[2:7] == 'give ' or p[2:7] == 'take ':

        # Attempt casting info
        try:
          t = ( int( p[7:].split( ' ' )[0] ), int( p[7:].split( ' ' )[1] ) )
        except Exception:
          print( '[#] Enter 2 numbers.' )
        else:

          # Give/remove and print info
          if p[2] == 'g':
            update_inv( *t )
            print( f'[!] Gave you "{ item_meta( t[0] ) }" x{ t[1] }' )
          else:
            print( f"[!] Removed \"{ item_meta( t[0] ) }\" x{ update_inv( *t, mode = 'r' ) }" )
          goto_room( room_scene )

      # Set block
      elif p[2:] == 'set':
        print( '[#] Must supply coordinates.' )

      elif p[2:6] == 'set ':

        # Attempt casting coordiantes
        try:
          t = g_pos.copy().a( int( p[ 6: ].split( ' ' )[0] ), int( p[ 6: ].split( ' ' )[1] ) )
        except Exception:
          print( "[#] Invalid coordinates." )
        else:

          # Make sure coordinates are within world border
          if t.x < 0 or t.y < 0 or t.x >= g_world_size.x or t.y > g_world_size.y:
            print( 'Those coordinates are out of this world!\n(No, really)')

          # Make sure they gave a block ID
          elif not ( len( p[ 6: ].split( ' ' ) ) == 3 and p[ 6: ].split( ' ' )[2] != '' ):
            print( '[#] Incorrect number of arguments.' )

          # Update the block
          else:
            g_tile_data[ xy2c( *t.l(), g_world_size.x ) ] = p_def[ 6: ].split( ' ' )[2]
            data_world_update( g_wname )
            print( f"[!] Set block to ID '{ p_def[ 6: ].split( ' ' )[2] }'" )
            goto_room( room_scene )

      # Fight monster
      elif p[2:] == 'fight':
        print( '[#] Must supply monster ID.' )

      elif p[2:8] == 'fight ':

        # Check monster ID
        if p[8:] not in MONSTERS:
          print( '[#] Invalid monster ID.' )
        else:
          start_fight( p[8:] )

      # Execute code
      elif p[2:] == 'execute':
        print( '[#] Must supply code.' )

      elif p[2:10] == 'execute ':

        exec( p[10:] )

      # Invalid input
      else:
        print( '[#] Unknown debug sub-command.' )

    # Invalid input
    else:
      print( '[#] Unknown command.' )

# Allow time to move forward a little bit
# Includes gravity, monster movements, etc.
def tick( nofall = False ):

  global g_pos

  # Move player 5 blocks downward
  if not nofall:
    for i in range( 5 ):
      if g_pos.y + 1 < g_world_size.y and get_tile( g_pos.copy().a( 0, 1 ) ) in AIR_BLOCKS:
        g_pos.y += 1

  data_world_update( g_wname )

# Modify the inventory
# Modes = pickup, remove, or set
def update_inv( item_id, amount, mode = 'p', slot = 0 ):

  global g_items

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
        break

    else:

      # Then find empty slot
      for i in range( 16 ):
        if g_items[i][1] == 0:
          g_items[i][0] = item_id
          g_items[i][1] = amount
          break

  # Removal mode
  # (Returns the # of items that were able to be removed)
  elif mode == 'r':

    # Try to remove
    for i in range( 16 ):
      if g_items[i][0] == item_id:
        if g_items[i][1] >= amount:

          g_items[i][1] -= amount
          data_char_update( g_cname )
          return amount

        elif g_items[i][1] > 0:

          t = g_items[i][1]
          g_items[i][1] = 0
          data_char_update( g_cname )
          return t

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
  data_char_update( g_cname )

# Break a block
def break_block( x, y ):

  global g_tile_data

  # Make sure it's within the world boundaries
  if not ( 0 <= x < g_world_size.x ): return
  if not ( 0 <= y < g_world_size.y ): return

  # Store what the block was, then change it
  t = g_tile_data[ xy2c( x, y, g_world_size.x ) ]
  g_tile_data[ xy2c( x, y, g_world_size.x ) ] = ' '
  data_world_update( g_wname ) # Save data

  # Return what the block was
  return t

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
    data_world_update( g_wname ) # Save data
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
    t = break_block( g_pos.x + x, g_pos.y + y )

    # break_block() returns the ID of the block that was broken, which is stored in t
    # If possible, this block is put in the player's inventory
    if t in ITEM_BLOCKS:
      update_inv( ITEM_BLOCKS[ t ], 1 )

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
    t = place_block( g_pos.x + x, g_pos.y + y )

    # place_block() returns whether the attempt was successful, which is stored in t
    # If successful, one block is removed from the player's inventory
    if t:
      update_inv( g_items[ g_slot ][0], 1, 'r' )

    # Performing a game tick prevents the player from floating above it like a cartoon character
    tick()
    goto_room( room_scene ) # We can now reload the room

# Inventory Room
def room_inventory( arg = "" ):

  # Args can be set to 1 to avoid re-printing room data
  if not ( len( arg ) > 0 and arg[0] == '1' ):
    
    # Print items in a grid-like pattern
    print_line()
    print( 'Inventory:' )
    for i in range( 16 ):
      j = i // 2 + ( i % 2 ) * 8
      t = f"({ '1234567890ABCDEF'[j] }) "
      t += ( '* ' if g_slot == j else '' ) + ( item_meta( j, c = 1 ) if g_items[j][1] != 0 else '...' )
      t += f"  x{ g_items[j][1] }" if g_items[j][1] != 0 else ''
      t = t[:38]
      print( t + ' ' * ( 40 - len( t ) ), end = ( '' if j < 8 else '\n' ) )
    print()

    # Print options
    print( '[I] Get info' )
    print( '[M] Move item' )
    print( '[T] Trash item' )
    print( '[C] Open crafting' )
    print( '[Q] Close' )

  while True:
    p = input( '> ' ).lower()

    # Info
    if p == 'i':

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
          print( "[?] Description: " + item_meta( list( '1234567890ABCDEF' ).index( p ), 1, c = 1 ) )
          goto_room( room_inventory, '1' )

    # Move
    if p == 'm':

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
      t = ''
      while True:
        p = input( '> ' ).upper()

        # Make sure it matches a slot
        if p not in list( '1234567890ABCDEF' ):
          print( '[#] Enter a number from 0-9 or a letter from A-F.' )

        # Make sure source slot has an item in it
        elif t == '' and g_items[ list( '1234567890ABCDEF' ).index( p ) ][1] == 0:
          print( '[#] This slot is empty.' )

        # Set source slot and move onto getting destination slot
        elif t == '':
          print( 'Enter the slot you want to move it to:' )
          t = p

        # Move item and re-show inventory
        else:

          # Shorten indices/store swap buffer
          t = list( '1234567890ABCDEF' ).index( t )
          p = list( '1234567890ABCDEF' ).index( p )
          swap_buffer = g_items[t].copy()

          # Swap, print message, and re-show inventory
          update_inv( *g_items[p], mode = 's', slot = t )
          update_inv( *swap_buffer, mode = 's', slot = p )
          print( f'[!] Moved "{ item_meta( p, c = 1 ) }".' if g_items[t][1] == 0 else f'[!] Swapped "{ item_meta( p, c = 1 ) }" and "{ item_meta( t, c = 1 ) }"' )
          goto_room( room_inventory )

    # Trash
    if p == 't':

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
    if p == 'q':
      goto_room( room_scene )

    # Invalid input
    else:
      print( '[#] Unknown command.' )

# Crafting room
def room_crafting( arg = '' ):

  # Store recipes object
  RECIPES = [
    { 'req': { I_IRON_ORE: 3 }, 'res': [ I_IRON_BAR, 1 ] },
    { 'req': { I_SILVER_ORE: 3 }, 'res': [ I_SILVER_BAR, 1 ] },
    { 'req': { I_GOLD_ORE: 3 }, 'res': [ I_GOLD_BAR, 1 ] },
    { 'req': { I_WOOD: 20 }, 'res': [ I_W_SWORD, 1 ] },
    { 'req': { I_WOOD: 8, I_IRON_BAR: 8 }, 'res': [ I_I_SWORD, 1 ] },
    { 'req': { I_WOOD: 8, I_SILVER_BAR: 8 }, 'res': [ I_S_SWORD, 1 ] },
    { 'req': { I_WOOD: 8, I_GOLD_BAR: 8 }, 'res': [ I_G_SWORD, 1 ] },
    { 'req': { I_WOOD: 12 }, 'res': [ I_W_BOW, 1 ] },
    { 'req': { I_IRON_BAR: 6 }, 'res': [ I_I_BOW, 1 ] },
    { 'req': { I_SILVER_BAR: 6 }, 'res': [ I_S_BOW, 1 ] },
    { 'req': { I_GOLD_BAR: 6 }, 'res': [ I_G_BOW, 1 ] }
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

      t = p # Store in a temporary variable

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
      if t == 'i':

        t = page * 8 + ( p - 1 ) # Shortening selected slot
  
        # Print data
        print( f"Required ingredients for \"{ item_meta( RECIPES[t]['res'][0] ) }\":" )
        for i in RECIPES[t]['req']:
          print( f"- { item_meta( i ) } x{ RECIPES[t]['req'][i] }" )
  
        # Reload room
        goto_room( room_crafting, '1' + str( page ) )

      # Alternatively, craft the item
      elif t == 'c':

        t = page * 8 + ( p - 1 ) # Shortening selected slot

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
        for i in RECIPES[t]['req']:
          if update_inv( i, 0, mode = 't' ) < RECIPES[t]['req'][i] * p:
            can_craft = False
            print( f"[#] You need { RECIPES[t]['req'][i] * p - update_inv( i, 0, mode = 't' ) } more \"{ item_meta( i ) }\"." )

        # Continue onward if they have all the items
        if can_craft:

          # Take the ingredients, then give them the resultant item
          for i in RECIPES[t]['req']:
            update_inv( i, RECIPES[t]['req'][i] * p, mode = 'r' )
          update_inv( RECIPES[t]['res'][0], RECIPES[t]['res'][1] * p, mode = 'p' )

          print( f"[!] You crafted \"{ item_meta( RECIPES[t]['res'][0] ) }\" x{ RECIPES[t]['res'][1] * p }." )

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

def start_fight( monster_id ):
  
  global g_monster
  if monster_id == 'slime': g_monster = MonsterSlime()
  if monster_id == 'zombie': g_monster = MonsterZombie()
  if monster_id == 'demon_eye': g_monster = MonsterDemonEye()
  if monster_id == 'cave_bat': g_monster = MonsterCaveBat()
  else: g_monster = MonsterSlime()
  
  print_line()
  input( f'You encountered a { g_monster.name }! ' )
  
  goto_room( room_fight )

def room_fight():

  global g_monster

  # PLAYER TURN
  print_line()
  print( f'You: { g_hp } HP' )
  print( f'{ g_monster.name }: { g_monster.hp } HP' )
  allowed_inputs = g_monster.get_options( player_turn = True )
  print( '[*] Pause' )

  # Get inputs
  while True:
    p = input( '> ' ).lower()

    # Pause
    if p == '*':
      goto_room( room_pause, 'goto_room( room_fight )' )

    # Turn
    elif p in allowed_inputs:
      g_monster.player_turn( p )
      break

    # Invalid input
    else:
      print( '[#] Unknown command.' )

  # ENEMY TURN
  print_line()
  print( f'You: { g_hp } HP' )
  print( f'{ g_monster.name }: { g_monster.hp } HP' )
  allowed_inputs = g_monster.get_options( player_turn = False )
  print( '[*] Pause' )

  # Get inputs
  while True:
    p = input( '> ' ).lower()

    # Pause
    if p == '*':
      goto_room( room_pause, 'goto_room( room_fight )' )

    # Turn
    elif p in allowed_inputs:
      g_monster.turn( p )
      break

    # Invalid input
    else:
      print( '[#] Unknown command.' )

  goto_room( room_fight )

def room_death():

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

  # Wait for input before ending program
  # (Windows consoles automatically close upon the end of a program,
  # which isn't helpful if I want to be able to read a crash message.)
  input( 'Press enter to exit.' )

run()
