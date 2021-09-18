import os

def clamp( n, min, max ):

  return min( max( n, min ), max )

class MoveException( BaseException ):

  def __init__( self, room ):
    self.room = room

class V2:

  def __init__( self, x = 0, y = 0 ):
    self.u( x, y )

  def op( self, a, b, op ):

    if op == '+': return a + b
    if op == '-': return a - b
    if op == '*': return a * b
    if op == '/': return a / b

  def op2( self, a, b, op ):

    self.x = self.op( self.x, a, op )
    self.y = self.op( self.y, a if b == 'd' else a, op )

  def u( self, a = 0, b = 0 ):
    self.x = a
    self.y = b

  def a( self, a, b = 'd' ):
    self.op2( a, b, '+' )

  def s( self, a, b = 'd' ):
    self.op2( a, b, '-' )

  def m( self, a, b = 'd' ):
    self.op2( a, b, '*' )

  def d( self, a, b = 'd' ):
    self.op2( a, b, '/' )

  def p( self ):
    return( f'[{self.x}, {self.y}]' )

def goto_room( room ):
  raise MoveException( room )

def print_line():
  print( '- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -' )

DEBUG = True
g_data = {}
g_cname = ''
g_wname = ''
g_pos = V2( 0, 0 )
g_health = 0
g_health_max = 0

def data_main_load():

  global g_data

  test = open( 'data.txt', 'a+' )
  test.seek( 0 )
  if test.read() == '':
    data_main_init()

  file = open( 'data.txt', 'r' ).read().split( '\n' )
  g_data[ 'char_list' ] = file[0][ 12: ].split( ',' )
  if g_data[ 'char_list' ] == [ '' ]:
    g_data[ 'char_list' ] = []
  g_data[ 'world_list' ] = file[1][ 8: ].split( ',' )
  if g_data[ 'world_list' ] == [ '' ]:
    g_data[ 'world_list' ] = []

def data_main_init():

  file = open( 'data.txt', 'w' )
  file.write( 'characters: \n' )
  file.write( 'worlds: \n' )

def data_main_update():

  file = open( 'data.txt', 'w' )
  file.write( 'characters: ' )
  for c in g_data[ 'char_list' ]:
    file.write( ( ',' if c != g_data[ 'char_list' ][0] else '' ) + c )
  file.write( '\nworlds: ' )
  for c in g_data[ 'world_list' ]:
    file.write( ( ',' if c != g_data[ 'world_list' ][0] else '' ) + c )

def data_char_init( name ):

  file = open( 'c_' + name + '.txt', 'w' )
  file.write( 'hp: 100,100\n' )
  file.write( 'items: ' )
  for i in range( 20 ):
    file.write( '0:0' + ( ',' if i != 19 else '' ) )
  file.write( '\nplay_time: 0' )

def data_world_init( name ):

  file = open( 'w_' + name + '.txt', 'w' )
  world_size = ( 400, 200 )

  file.write( f'player_pos: { world_size[0] // 2 },{ world_size[1] // 2}\n' )
  for j in range( world_size[1] ):
    for i in range( world_size[0] ):
      file.write( ' ' if j <= world_size[ 1 ] / 2 else '#' )
    file.write( '\n' )

def data_world_load( name ):

  global g_pos

  file = open( 'w_' + name + '.txt', 'r' ).read().split( '\n' )
  print( file[0][12:].split( ',' )[0] )
  g_pos.x = int( file[0][12:].split( ',' )[0] )
  g_pos.y = int( file[0][12:].split( ',' )[1] )

def room_menu():

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

  while True:
    p = input( '> ' ).lower()
    if p == 'p':
      goto_room( room_character_select )
      break
    elif p == 'q':
      print( 'Game closed.' )
      goto_room( 0 )
    else:
      print( '[#] Unknown command.' )

def room_character_select():

  global g_cname, g_data

  print_line()
  print( 'Characters:' )
  for i in range( len( g_data[ 'char_list' ] ) ):
    print( f'[{ i + 1 }] { g_data[ "char_list" ][i] }' )
  print( '[C] Create new character' )
  print( '[D][#] Delete chracter #' )
  print( '[Q] Back' )
  while True:
    try:
      p = input( '> ' ).lower()
      if p == 'c':
        goto_room( room_character_create )
      elif p == 'q':
        goto_room( room_menu )
      elif p == 'd' or p[0:2] == 'd ':

        try:
          if len( p ) <= 2:
            print( '[#] Must supply character index.' )
          elif not ( 0 < int( p[2:] ) <= len( g_data[ 'char_list' ] ) ):
            print( '[#] Out of range.' )
          else:
            t = g_data[ 'char_list' ][ int( p[2:] ) - 1 ]
            print( f'Are you sure you want to delete character "{ t }"?' )
            print( 'Type "yes" to proceed.' )
            if input( '> ' ) == 'yes':
              print( '[!] Character deleted.' )
              if os.path.exists( 'c_' + t + '.txt' ):
                os.remove( 'c_' + t + '.txt' )
              g_data[ 'char_list' ].pop( int( p[2:] ) - 1 )
              data_main_update()
            goto_room( room_character_select )
        except ValueError:
          print( '[#] Must supply a number.' )
      else:
        p = int( p )
        if not ( 0 < p <= len( g_data[ 'char_list' ] ) ):
          print( '[#] Out of range' )
        else:
          print( f'[!] Selected character "{ g_data[ "char_list" ][ p - 1 ] }"' )
          g_cname = g_data[ 'char_list' ][ p - 1 ]
          goto_room( room_world_select )
    except ValueError: print( '[#] Unknown command.' )

def room_character_create():

  global g_data

  print_line()
  print( 'Enter a name:' )
  while True:
    name = input( '> ' )
    if not ( 0 < len( name ) <= 16 ):
      print( '[#] Name must be between 1 and 16 characters long.' )
    elif name in g_data[ 'char_list' ]:
      print( '[#] This character already exists.' )
    else:
      g_data[ 'char_list' ].append( name )
      data_main_update()
      data_char_init( name )
      break

  goto_room( room_character_select )

def room_world_select():

  global g_wname, g_data

  print_line()
  print( 'Worlds:' )
  for i in range( len( g_data[ 'world_list' ] ) ):
    print( f'[{ i + 1 }] { g_data[ "world_list" ][i] }' )
  print( '[C] Create new world' )
  print( '[D][#] Delete world #' )
  print( '[Q] Back' )

  while True:
    try:
      p = input( '> ' ).lower()
      if p == 'c':
        goto_room( room_world_create )
      elif p == 'q':
        goto_room( room_character_select )
      elif p == 'd' or p[0:2] == 'd ':
        try:
          if len( p ) <= 2:
            print( '[#] Must supply world index.' )
          elif not ( 0 < int( p[2:] ) <= len( g_data[ 'world_list' ] ) ):
            print( '[#] Out of range.' )
          else:
            t = g_data[ 'world_list' ][ int( p[2:] ) - 1 ]
            print( f'Are you sure you want to delete world "{ t }"?' )
            print( 'Type "yes" to proceed.' )
            if input( '> ' ) == 'yes':
              print( '[!] World deleted.' )
              if os.path.exists( 'w_' + t + '.txt' ):
                os.remove( 'w_' + t + '.txt' )
              g_data[ 'world_list' ].pop( int( p[2:] ) - 1 )
              data_main_update()
            goto_room( room_world_select )
        except ValueError:
          print( '[#] Must supply a number.' )
      else:
        p = int( p )
        if not ( 0 < p <= len( g_data[ 'world_list' ] ) ):
          print( '[#] Out of range' )
        else:
          print( f'[!] Selected world "{ g_data[ "world_list" ][ p - 1 ] }"' )
          g_wname = g_data[ 'world_list' ][ p - 1 ]
          data_world_load( g_wname )
          goto_room( room_scene )
    except ValueError: print( '[#] Unknown command.' )

def room_world_create():

  global g_data

  print_line()
  print( 'Enter a name:' )
  while True:
    name = input( '> ' )
    if not ( 0 < len( name ) <= 16 ):
      print( '[#] Name must be between 1 and 16 characters long.' )
    elif name in g_data[ 'char_list' ]:
      print( '[#] This world already exists.' )
    else:
      g_data[ 'world_list' ].append( name )
      data_main_update()
      data_world_init( name )
      goto_room( room_world_select )

def room_scene():

  print_line()
  print( 'Position:', g_pos.p() )
  print( f'Health: { g_health }/{ g_health_max }' )
  input()

def run():

  data_main_load()

  room = room_menu
  while True:
    try:
      room()
    except MoveException as m:
      room = m.room
      if room == 0: break

  if DEBUG: input( 'Press enter to exit.' )

run()
