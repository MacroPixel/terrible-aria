import pygame
import numpy as np
from math import sin, cos
import random

class RestartException( BaseException ):
  pass

def dist( a, b ):

  return ( ( a.x - b.x ) ** 2 + ( a.y - b.y ) ** 2 ) ** 0.5

def clamp( n, mn, mx ):

  return min( max( n, mn ), mx )

def xy2c( x, y, w ):

  return ( y * w ) + x

def sym2col( s ):
  if s == ' ': return ( 0, 0, 0 )
  if s == 'g': return ( 0, 220, 0 )
  if s == 's': return ( 120, 120, 120 )
  if s == 'l': return ( 120, 90, 0 )
  if s == 'L': return ( 0, 65, 20 )
  if s == 'i': return ( 150, 130, 120 )
  if s == 'S': return ( 170, 170, 190 )
  if s == 'G': return ( 230, 190, 40 )
  if s == 'w': return ( 120, 70, 10 )
  if s == 'c': return ( 210, 150, 0 )
  if s == 'C': return ( 255, 150, 150 )
  if s == 'P': return ( 0, 0, 255 )
  return( 255, 255, 255 )

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

# Create new (empty) chest
def chest_create( x, y ):

  global g_tile_special

  g_tile_special[ str( x ) + " : " + str( y ) ] = []
  for i in range( 10 ):
    g_tile_special[ str( x ) + " : " + str( y ) ].append( [ 0, 0 ] )

def chest_modify( x, y, item_id, amount, mode = 'i' ):

  global g_tile_special

  # Insert
  if mode == 'i':

    # The same as the code for update_inv()
    for i in range( 10 ):
      if g_tile_special[ str( x ) + " : " + str( y ) ][i][0] == item_id and g_tile_special[ str( x ) + " : " + str( y ) ][i][1] > 0:
        g_tile_special[ str( x ) + " : " + str( y ) ][i][1] += amount
        return True

    for i in range( 10 ):
      if g_tile_special[ str( x ) + " : " + str( y ) ][i][1] == 0:
        g_tile_special[ str( x ) + " : " + str( y ) ][i][0] = item_id
        g_tile_special[ str( x ) + " : " + str( y ) ][i][1] = amount
        return True

    return False

  # Remove
  elif mode == 'r':

    # Try to remove
    for i in range( 10 ):
      if g_tile_special[ str( x ) + " : " + str( y ) ][i][0] == item_id:
        if g_tile_special[ str( x ) + " : " + str( y ) ][i][1] >= amount:

          g_tile_special[ str( x ) + " : " + str( y ) ][i][1] -= amount
          data_char_update( g_cname )
          return amount

        elif g_tile_special[ str( x ) + " : " + str( y ) ][i][1] > 0:

          t = g_tile_special[ str( x ) + " : " + str( y ) ][i][1]
          g_tile_special[ str( x ) + " : " + str( y ) ][i][1] = 0
          data_char_update( g_cname )
          return t

    # Failed to remove
    return 0

def chest_remove( x, y ):

  global g_tile_special

  g_tile_special.pop( f'{ x } : { y }' )

def print_progress( prog, div_this, div_total, s ):

  t = int( prog )
  prog += ( 1 / div_this ) * ( div_total / 2 )
  suffix = f'{ int( prog * 2 ) }% ' if prog < 50 else 'Done!'
  if prog < 50:
    suffix += f'({ s })'
  print( '[' + ( '|' * int( prog ) ) + ( '-' * ( 50 - int( prog ) ) ) + ']  ' + suffix + ( ' ' * 30 ), end = '\r' )
  return prog

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
I_SUS_EYE = 25
I_GRENADE = 26
I_HEALTH_POTION = 27

world_size = V2( 400, 200 )
screen_size = world_size.copy().m( 3 )
g_tile_data = ''
g_tile_special = {}

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

  # Chest rooms
  if CHESTS:

    # List of chest coords
    t1 = []

    # Each iteration creates a new chest room
    for l1 in range( CHESTS_FREQ ):

      # Basically a while loop but with a limit so it doesn't go forever if something unexpected happens
      for l2 in range( 999 ):      

        # Choose a random position underground
        o = V2( random.randint( 30, size.x - 30 ), random.randint( int( size.y * 0.7 ), size.y - 5 ) )

        # See if it's too close to another chest
        too_close = False
        for i in t1:
          if dist( o, i ) < 40: too_close = True

        # If not, place it and the room
        if not too_close:
          
          t1.append( o )
          for yy in range( o.y - 8, o.y + 2 ):
            for xx in range( o.x - 10, o.x + 11 ):
              g_tile_data[ xy2c( xx, yy, size.x ) ] = ( 'w' if xx in ( o.x - 10, o.x + 10 ) or yy in ( o.y - 8, o.y + 1 ) else ' ' ) # Place outline / air pocket
          g_tile_data[ xy2c( *o.l(), size.x ) ] = 'c' # Place chest

          # CHEST INFO
          chest_create( *o.l() )

          t = random.choice( ( ( I_SUS_EYE, 1, 1 ), ( I_HEALTH_POTION, 1, 1 ), ( I_GRENADE, 4, 7 ) ) )
          chest_modify( *o.l(), t[0], random.randint( t[1], t[2] ), mode = 'i' ) # Random item for slot 1

          t = random.choice( ( ( I_IRON_BAR, 3, 5 ), ( I_SILVER_BAR, 3, 5 ), ( I_GOLD_BAR, 3, 5 ) ) )
          chest_modify( *o.l(), t[0], random.randint( t[1], t[2] ), mode = 'i' ) # Random bar for slot 1

          t = random.choice( ( ( I_TORCH, 10, 15 ), ( I_ARROW, 15, 25 ), ( I_F_ARROW, 8, 15 ) ) )
          chest_modify( *o.l(), t[0], random.randint( t[1], t[2] ), mode = 'i' ) # Random bar for slot 1

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
  g_tile_data[ xy2c( g_pos.x, g_pos.y + 1, size.x ) ] = 'g' # Make sure the player is standing on a block

  # Set progress to 100 (in case something glitched)
  print_progress( 50, 1, 1, 'This should never print' )
  print() # Newline

running = True
while running:

  try:
    world_seed = random.randint( 1000, 9999 )
    generate_world( world_size, world_seed )
    g_tile_data[ xy2c( g_pos.x, g_pos.y, world_size.x ) ] = 'P'

    temp_array = np.zeros( ( world_size.x, world_size.y, 3 ), dtype = int )
    for j in range( world_size.y ):
      for i in range( world_size.x ):
        t = g_tile_data[ xy2c( i, j, world_size.x ) ]
        temp_array[ i, j ] = ( sym2col( t ) )

    pygame.init()
    pygame.display.set_caption( 'Worldgen Test' )
    screen = pygame.display.set_mode( screen_size.l() )

    while running:
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
            running = False
          if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            raise RestartException()
      screen.fill( ( 20, 20, 20 ) )

      temp_surf = pygame.Surface( world_size.l() )
      pygame.pixelcopy.array_to_surface( temp_surf, temp_array )
      temp_surf = pygame.transform.scale( temp_surf, screen_size.l() )
      screen.blit( temp_surf, ( 0, 0 ) )

      pygame.display.flip()
  except RestartException:
    pass
