# Won't be keeping this file long term
# I'm only putting it here as a backup

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
  if s == 'Ξ': return ( 0, 220, 0 )
  if s == '#': return ( 120, 120, 120 )
  if s == 'Ⅲ': return ( 120, 90, 0 )
  if s == '∷': return ( 0, 65, 20 )
  if s == '⩏': return ( 150, 130, 120 )
  if s == '⩎': return ( 170, 170, 190 )
  if s == '⩩': return ( 230, 190, 40 )
  return( 255, 255, 255 )

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
    self.y = self.op( self.y, a if b == 'd' else b, op )

  def u( self, a = 0, b = 0 ):
    self.x = a
    self.y = b
    return self

  def a( self, a, b = 'd' ):
    self.op2( a, b, '+' )
    return self

  def s( self, a, b = 'd' ):
    self.op2( a, b, '-' )
    return self

  def m( self, a, b = 'd' ):
    self.op2( a, b, '*' )
    return self

  def d( self, a, b = 'd' ):
    self.op2( a, b, '/' )
    return self

  def l( self ):
    return [ self.x, self.y ]

  def copy( self ):
    c = V2( self.x, self.y )
    return c

def print_progress( prog, div_this, div_total ):

  t = int( prog )
  prog += ( 1 / div_this ) * ( div_total / 2 )
  suffix = f'{ int( prog * 2 ) }% ' if prog < 50 else 'Done!'
  if prog < 50:
    if prog < 40: suffix += '(Generating initial terrain)'
    elif prog < 42.5: suffix += '(Generating ore veins)'
    elif prog < 45: suffix += '(Generating caves)'
    elif prog < 47.5: suffix += '(Generating air pockets)'
    elif prog < 50: suffix += '(Generating trees)'
  print( '[' + ( '|' * int( prog ) ) + ( '-' * ( 50 - int( prog ) ) ) + ']  ' + suffix + ( ' ' * 20 ), end = '\r' )
  return prog

def noise_top( x ):

  next_seed = random.randint( 1000, 9999 )
  random.seed( WORLD_SEED )
  s = 0
  for i in range( 12 ):
    s += random.randrange( 3, 12 ) * sin( x / random.randrange( 6, 24 ) - random.randrange( 10, 80 ) )
  random.seed( next_seed )
  return s / 4;

world_size = V2( 400, 200 )
screen_size = world_size.copy().m( 3 )
g_tile_data = ''

def generate_world():

  CAVES = True
  POCKETS = True
  TREES = True
  ORES = True

  global g_tile_data

  g_tile_data = ''
  progress = 0
  print( 'Generating World:' )

  for j in range( world_size.y ):
    for i in range( world_size.x ):
      is_stone = j >= ( world_size.y / 2 ) + noise_top( i )
      is_grass = is_stone and ( j <= ( world_size.y / 2 ) + noise_top( i ) + 3 )
      is_stone = is_stone and not is_grass
      if is_grass: g_tile_data += 'Ξ'
      elif is_stone: g_tile_data += '#'
      else: g_tile_data += ' '
    progress = print_progress( progress, world_size.y, 80 )
  g_tile_data = list( g_tile_data )

  if ORES:
    for l1 in range( 256 ):
      o = V2( random.randint( 0, world_size.x ), 0 )
      o.y = random.randint( int( ( world_size.y / 2 ) + noise_top( o.x ) ) + 10, world_size.y )
      d = 0
      c = random.choice( ( '⩏', '⩏', '⩏', '⩎', '⩎', '⩩' ) )
      for l2 in range( 64 ):
        d += random.randrange( -10, 10 ) 
        o.a( cos( d ), sin( d ) )
        g_tile_data[ xy2c( clamp( int( o.x ), 1, world_size.x - 2 ), clamp( int( o.y ), 1, world_size.y - 2 ), world_size.x ) ] = c
      progress = print_progress( progress, 128, 5 )
  else: progress = print_progress( progress, 1, 5 )

  if CAVES:
    for l1 in range( 32 ):
      o = V2( random.randint( 0, world_size.x ), random.randint( world_size.y * 0.7, world_size.y ) )
      d = 0
      s = random.randrange( 2, 4 )
      for l2 in range( 48 ):
        d += random.randrange( -10, 10 ) / 10
        o.a( cos( d ) * 2, sin( d ) * 2 )
        s += random.randrange( -10, 10 ) / 10
        s = clamp( s, 2, 4.5 )
        for j in range( max( int( o.y ) - int( s ), 1 ), min( int( o.y ) + int( s ), world_size.y - 2 ) ):
          for i in range( max( int( o.x ) - int( s ), 1 ), min( int( o.x ) + int( s ), world_size.x - 2 ) ):
            if dist( o, V2( i, j ) ) < s: g_tile_data[ xy2c( i, j, world_size.x ) ] = ' '
      progress = print_progress( progress, 32, 5 )
  else: progress = print_progress( progress, 1, 5 )

  if POCKETS:
    for l1 in range( 128 ):
      o = V2( random.randint( 0, world_size.x ), 0 )
      o.y = random.randint( int( ( world_size.y / 2 ) + noise_top( o.x ) ) + 10, world_size.y )
      d = 0
      for l2 in range( 64 ):
        d += random.randrange( -10, 10 ) 
        o.a( cos( d ), sin( d ) )
        g_tile_data[ xy2c( clamp( int( o.x ), 1, world_size.x - 2 ), clamp( int( o.y ), 1, world_size.y - 2 ), world_size.x ) ] = ' '
      progress = print_progress( progress, 128, 5 )
  else: progress = print_progress( progress, 1, 5 )

  if TREES:
    i1 = random.randint( 5, 15 )
    while i1 < world_size.x - 15:
      o = V2( i1, int( ( world_size.y / 2 ) + noise_top( i1 ) ) )
      if g_tile_data[ xy2c( o.x, o.y + 1, world_size.x ) ] == 'Ξ':
        for i2 in range( random.randint( 10, 20 ) ):
          g_tile_data[ xy2c( o.x, o.y, world_size.x ) ] = 'Ⅲ'
          o.y -= 1
          if random.randint( 0, 25 ) == 0: o.x -= 1
          if random.randint( 0, 25 ) == 0: o.x += 1
        for j in range( o.y - 4, o.y + 4 ):
          for i in range( o.x - 4, o.x + 4 ):
            if random.randint( 0, int( dist( V2( i, j ), o ) ) ) <= 1:
              g_tile_data[ xy2c( i, j, world_size.x ) ] = '∷'
      i1 += int( random.randint( 8, 15 ) * random.choice( ( 0.6, 1, 1, 4 ) ) )
    progress = print_progress( progress, 1, 5 )
  else: progress = print_progress( progress, 1, 5 )
  print()


running = True
while running:

  try:
    WORLD_SEED = random.randint( 1000, 9999 )
    generate_world()

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
