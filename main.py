def menu():

  print( """
,--------.                         ,--. ,--.    ,--.                                  ,--.
'--.  .--'  ,---.  ,--.--. ,--.--. `--' |  |-.  |  |  ,---.  ,-----.  ,--,--. ,--.--. `--'  ,--,--.
   |  |    | .-. : |  .--' |  .--' ,--. | .-. ' |  | | .-. : '-----' ' ,-.  | |  .--' ,--. ' ,-.  |
   |  |    \   --. |  |    |  |    |  | | `-' | |  | \   --.         \ '-'  | |  |    |  | \ '-'  |
   `--'     `----' `--'    `--'    `--'  `---'  `--'  `----'          `--`--' `--'    `--'  `--`--'
                                                                                    (v1.0)

[P] Play
[Q] Quit
""")

  while True:
    p = input( "> " ).lower()
    if p == 'p':
      character_select()
      break
    elif p == 'q':
      print( "Game closed." )
      break
    else:
      print( "[ERROR] Unknown command." )

g_data = {}

def data_main_load():

  global g_data

  test = open( 'data.txt', 'a+' )
  test.seek( 0 )
  if test.read() == '':
    data_main_init()

  file = open( 'data.txt', 'r' ).read().split( '\n' )
  g_data[ 'char_list' ] = file[0][ 12: ].split( ',' )
  print( g_data[ 'char_list' ] )

def data_main_init():

  file = open( 'data.txt', 'w' )
  file.write( """characters: empty
""" )

def character_select():

  for i in range( len( g_data[ 'char_list' ] ) ):
  	print( f"[Slot { i + 1 }] { g_data[ 'char_list' ][i] }" )
  while True:
  	try:
  		p = int( input( "> " ) )
  		if not ( 0 < p <= len( g_data[ 'char_list' ] ) ):
  			print( "[ERROR] Out of range" )
	  	else:
	  		print( f"{ g_data[ 'char_list' ][ p - 1 ] }" )
	  		break
  	except: print( "[ERROR] Enter a number" )

def run():

  data_main_load()
  menu()

run()
