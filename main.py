import os
from math import sin, cos
import random
import traceback

# Returns a number such that min <= x <= max
def clamp( n, mn, mx ):

  return min( max( n, mn ), mx )

# Returns the distance between two vector objects
def dist( a, b ):

  return ( ( a.x - b.x ) ** 2 + ( a.y - b.y ) ** 2 ) ** 0.5

# Flattens a 2D index [x, y] down to a 1D index [c]
def xy2c( x, y, w ):

  return ( y * w ) + x

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

  def __init__( self, room ):
    self.room = room

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

# Switches rooms
def goto_room( room ):
  raise MoveException( room )

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

# GLOBAL VARIABLES
DEBUG = True
g_data = {}
g_cname = ''
g_wname = ''
g_pos = V2( 0, 0 )
g_vel = V2( 0, 0 )
g_view = V2( 0, 0 )
g_world_size = V2( 0, 0 )
g_hp = 0
g_hp_max = 0
g_items = []
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
  file.write( 'items: ' )
  for i in range( 16 ):
    file.write( '0:0' + ( ',' if i != 19 else '' ) )
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

  # ..also play time
  g_play_time = int( file[2][11:] )

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
  file.write( f'player_vel: 0,0\n' )

  # Write tile data
  for j in range( size.y ):
    file.write( ''.join( g_tile_data[ ( j * size.x ):( ( j + 1 ) * size.x ) ] ) )
    file.write( '\n' )

# Load a world file with a given name
def data_world_load( name ):

  global g_pos, g_vel, g_world_size, g_tile_data, g_show_help

  # Split file into statements
  file = open( 'w_' + name + '.txt', 'r' ).read().split( '\n' )

  # Read basic positional data
  g_world_size = V2( int( file[0][6:].split( ',' )[0] ), int( file[0][6:].split( ',' )[1] ) )
  g_pos = V2( int( file[2][12:].split( ',' )[0] ), int( file[2][12:].split( ',' )[1] ) )
  g_vel = V2( int( file[3][12:].split( ',' )[0] ), int( file[3][12:].split( ',' )[1] ) )

  # Read tile data
  g_tile_data = "";
  for j in range( g_world_size.y ):
    g_tile_data += file[4 + j]
  g_tile_data = list( g_tile_data )

  g_show_help = True # Shows a help message on your first turn in the world

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
    elif p == 'd' or p[0:2] == 'd ':

      # Forgot index
      if len( p ) <= 2:
        print( '[#] Must supply character index.' )

      # Attempt cast
      try:
        int( p[2:] )
      except ValueError:
        print( '[#] Must supply a number.' )

      else:

        # Too large/too small
        if not ( 0 < int( p[2:] ) <= len( g_data[ 'char_list' ] ) ):
          print( '[#] Out of range.' )

        else:

          # Store name in a temp variable so I don't have to retype this mess ↓
          t = g_data[ 'char_list' ][ int( p[2:] ) - 1 ]

          # Make sure they actually want to
          print( f'Are you sure you want to delete character "{ t }"?' )
          print( 'Type "yes" to proceed.' )
          if input( '> ' ).lower() == 'yes':

            # Delete character file and update character list in data.txt
            print( '[!] Character deleted.' )
            if os.path.exists( 'c_' + t + '.txt' ):
              os.remove( 'c_' + t + '.txt' )
            g_data[ 'char_list' ].pop( int( p[2:] ) - 1 )
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
    elif p == 'd' or p[0:2] == 'd ':

      # Forgot index
      if len( p ) <= 2:
        print( '[#] Must supply world index.' )

      # Attempt cast
      try:
        int( p[2:] )
      except ValueError:
        print( '[#] Must supply a number.' )

      else:

        # Too large/too small
        if not ( 0 < int( p[2:] ) <= len( g_data[ 'world_list' ] ) ):
          print( '[#] Out of range.' )

        else:

          # Store name in a temp variable so I don't have to retype this mess ↓
          t = g_data[ 'world_list' ][ int( p[2:] ) - 1 ]

          # Make sure they actually want to
          print( f'Are you sure you want to delete world "{ t }"?' )
          print( 'Type "yes" to proceed.' )
          if input( '> ' ).lower() == 'yes':

            # Delete world file and update world list in data.txt
            print( '[!] World deleted.' )
            if os.path.exists( 'w_' + t + '.txt' ):
              os.remove( 'w_' + t + '.txt' )
            g_data[ 'world_list' ].pop( int( p[2:] ) - 1 )
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
def room_scene():

  global g_pos, g_view, g_show_help

  # Set view position, setting it offset (-30, -20) from the player pos,
  # then ensuring it stays within the world border
  g_view = g_pos.copy()
  g_view.x = clamp( g_pos.x - 30, 0, g_world_size.x - 61 )
  g_view.y = clamp( g_pos.y - 20, 0, g_world_size.y - 41 )

  # Print HP
  print_line()
  print( f'HP: { g_hp }/{ g_hp_max }' )
  print()

  # Display world
  # (The code to do this is surprisingly short, eh?)
  for j in range( g_view.y, g_view.y + 41 ):
    for i in range( g_view.x, g_view.x + 61 ):
      if i == g_pos.x and j == g_pos.y:
        print( g_tmap[ 'player' ], end = ' ' )
      else:
        print( char2tile( g_tile_data[ xy2c( i, j, g_world_size.x ) ] ), end = " " )
    print()

  # Show help options if loaded in for first time
  if g_show_help:
    print( '[H] Help' )
    print( '[H <command name>] Help with a specific command' )
    g_show_help = False

  while True:
    p = input( '> ' ).lower()

    # Show generic help info
    if p == 'h':
      print( '[H] Show this screen' )
      print( '[H <command name>] Help with a specific command' )
      print( '[*] Bring up the pause menu' )
      print( '[M] Move in direction' )

    # Show specific help info
    elif p[0:2] == 'h ':
      if p[2:] == 'h':
        print( '[?] Syntax: h' )
        print( '[?] Effect: Shows a list of valid commands.' )
        print( '[?] Syntax: h <command>' )
        print( '[?] Effect: Shows help for a specific command.' )
        print( '[?] (I mean, you clearly already know how this works...)' )
      elif p[2:] == 'm':
        print( '[?] Syntax: m <direction> <steps>' )
        print( '[?] Effect: Moves the specified number of steps in the given direction.' )
      elif p[2:] == '*':
        print( '[?] Syntax: *' )
        print( '[?] Effect: Brings up the pause menu.' )
      else:
        print( f'[#] Unknown command "{ p[2:] }".' )

    # Pause game
    elif p == '*':
      print( '[!] Game was paused.' )
      goto_room( room_pause )

    # Move command (without necessary arguments)
    elif p == 'm':
      print( '[#] Must supply a direction.' )

    # Move command
    elif p[:5] == 'move ' or p[:2] == 'm ':

      # Make sure direction is valid
      if p.split( ' ' )[1] not in ( 'right', 'r', 'left', 'l' ):
        print( '[#] Invalid direction. (Accepts: "right", "left", "r", "l")')

      else:

          # Attempt cast
          try:
            int( p.split( ' ' )[2] )
          except ValueError:
            print( '[#] Enter a number.' )

          else:

            # Get step count (defaulting to 1)
            t1 = 1 if len( p.split( ' ' ) ) <= 2 else int( p.split( ' ' )[2] )

            # Check range
            if not ( 0 < t1 < 10 ):
              print( '[#] Step count out of range.' )

            # Move in given direction and reload stage
            else:
              for i in range( t1 ):
                if g_tile_data[ xy2c( g_pos.x + ( 1 if p.split( ' ' )[1][0] == 'r' else -1 ), g_pos.y, g_world_size.x ) ] in [ ' ', 'l' ]:
                  g_pos.x += ( 1 if p.split( ' ' )[1][0] == 'r' else -1 )
              goto_room( room_scene )

    # Invalid input
    else:
      print( '[#] Unknown command.' )

def run_tick():

  global g_pos, g_vel

# Pause room
def room_pause():

  # Show options
  print_line()
  print( '[Q] Return to menu' )
  print( '[X] Return to game' )

  while True:
    p = input( '> ' ).lower()

    # Quit
    if p == 'q':
      print( '[!] Returned to menu.')
      goto_room( room_menu )

    # Unpause
    elif p == 'x':
      print( '[!] Returned to game.')
      goto_room( room_scene )

    # Invalid input
    else:
      print( '[#] Unknown command.')

#
# ENTER MAIN LOOP
#
def run():

  # Load global data
  data_main_load()

  # Start in menu room
  room = room_menu

  # Listen for crashes
  try:

    while True:

      # Move between rooms
      try:
        room()
      except MoveException as m:
        room = m.room
        if room == 0:
          break # Exit loop if user quit the game

  # Print crash message
  except Exception:
    print( '[CRASH] ' )
    print( traceback.format_exc() )

  # Wait for input before ending program
  # (Windows consoles automatically close upon the end of a program,
  # which isn't helpful if I want to be able to read a crash message.)
  input( 'Press enter to exit.' )

run()
