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
			print( "Play" )
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
	
	pass

def run():
	
	data_main_load()
	menu()

run()
