class MoveException( BaseException ):

  def __init__( self, room ):
    self.room = room

def move( room ):
  raise MoveException( room )

def print_line():
  print( "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -" )

DEBUG = True
g_data = {}
g_cname = ""
g_wname = ""

def data_main_load():

  global g_data

  test = open( 'data.txt', 'a+' )
  test.seek( 0 )
  if test.read() == '':
    data_main_init()

  file = open( 'data.txt', 'r' ).read().split( '\n' )
  g_data[ 'char_list' ] = file[0][ 12: ].split( ',' )

def data_main_init():

  file = open( 'data.txt', 'w' )
  file.write( """characters: empty
""" )

def data_main_update():

  file = open( 'data.txt', 'w' )
  file.write( "characters: " )
  for c in g_data[ 'char_list' ]:
    file.write( ( ',' if c != g_data[ 'char_list' ][0] else '' ) + c )

def room_menu():

  print_line()
  print( """

,--------.                         ,--. ,--.    ,--.                                  ,--.
'--.  .--'  ,---.  ,--.--. ,--.--. `--' |  |-.  |  |  ,---.  ,-----.  ,--,--. ,--.--. `--'  ,--,--.
   |  |    | .-. : |  .--' |  .--' ,--. | .-. ' |  | | .-. : '-----' ' ,-.  | |  .--' ,--. ' ,-.  |
   |  |    \   --. |  |    |  |    |  | | `-' | |  | \   --.         \ '-'  | |  |    |  | \ '-'  |
   `--'     `----' `--'    `--'    `--'  `---'  `--'  `----'          `--`--' `--'    `--'  `--`--'
                                                                                    (v1.0)

[P] Play
[Q] Quit""")

  while True:
      p = input( "> " ).lower()
      if p == 'p':
        move( room_character_select )
        break
      elif p == 'q':
        print( "Game closed." )
        move( 0 )
      else:
        print( "[ERROR] Unknown command." )

def room_character_select():

  global g_cname, g_data

  print_line()
  print( 'Characters:')
  for i in range( len( g_data[ 'char_list' ] ) ):
  	print( f"[{ i + 1 }] { g_data[ 'char_list' ][i] }" )
  print( "[C] Create new character" )
  print( "[D][#] Delete chracter #" )
  print( "[Q] Back" )
  while True:
    try:
      p = input( "> " ).lower()
      if p == 'c':
        move( room_character_create )
      elif p == 'q':
        move( room_menu )
      elif p[0:2] == 'd ':
        if len( p ) <= 2:
          print( "[ERROR] Must supply character name." )
        elif p[2:] not in g_data[ 'char_list' ]:
          print( "[ERROR] Character does not exist." )
        else:
          g_data[ 'char_list' ].remove( p[2:] )
      else:
        print( p )
        p = int( p )
        if not ( 0 < p <= len( g_data[ 'char_list' ] ) ):
          print( "[ERROR] Out of range" )
        else:
          print( f"Selected character \"{ g_data[ 'char_list' ][ p - 1 ] }\"" )
          break
    except ValueError: print( "[ERROR] Unknown command." )

  g_cname = g_data[ 'char_list' ][ p - 1 ]

def room_character_create():

  global g_data

  print_line()
  print( "Enter a name:" )
  while True:
    name = input( "> " )
    if not ( 0 < len( name ) <= 16 ):
      print( "[ERROR] Name must be between 1 and 17 characters long." )
    elif name in g_data[ 'char_list' ]:
      print( "[ERROR] This character already exists." )
    else:
      g_data[ 'char_list' ].append( name )
      data_main_update()
      break

  move( room_character_select )

def run():

  data_main_load()
  
  room = room_menu
  while True:
    try:
      room()
    except MoveException as m:
      room = m.room
      if room == 0: break

  if DEBUG: input( "Press enter to exit." )

run()
