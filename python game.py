#Set up python game system
import pygame
from pygame.locals import *
import pickle
from os import path

#open game
pygame.init()

#Avoid dropping or delaying fps
clock = pygame.time.Clock()
fps = 60


#Window dimensions
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('SUPER HANYA')


#define score font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


#define font colours
white = (255, 255, 255)
blue = (0, 0, 255)

#Dimensions of single tile
tile_size = 30
 
#To control ending the game9
game_over = 0

#To control appearance of main menu
main_menu= True 

#To control and change levels
level=0

#to count score
score=0

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/sky.png')
Restart_img= pygame.image.load('img/restart_btn.png')
start_img= pygame.image.load('img/start_btn.png')
exit_img= pygame.image.load('img/exit_btn.png')


#function to reset level 
def reset_level(level):
	player.reset (90, screen_height - 100)
#To empty aka wipe all functions from past levels
	blob_group.empty()
	lava_group.empty()
	exit_group.empty()
	if path.exists(f'level{level}_data'):

#defines file i am targeting and put 'rb'= read binary
		pickle_in= open(f'level{level}_data','rb')

#load in levels data and create world
		world_data= pickle.load(pickle_in)
	world = World(world_data)

	return world

  

#To create button
class Button():
#To be able to function same button but different images
	def __init__(self,x,y,image):
		self.image= image
		self.rect= self.image.get_rect()
		self.rect.x = x
		self.rect.y= y
#To avoid the continous action at one click
#Default of click
		self.clicked= False

	def draw(self):
		Action=False

#To figure out mouse position
		position= pygame.mouse.get_pos()
#checking mouse and clicking conditions
		if self.rect.collidepoint(position):
#if i left clicked the mouse		
			if pygame.mouse.get_pressed()[0]==1 and self.clicked==False:
				Action=True
				self.clicked= True
#If i release the button it resets back
		if pygame.mouse.get_pressed()[0]==0:
			self.clicked= False


#To draw the button 
		screen.blit(self.image, self.rect) 
			
		return Action


#Character functions
class Player():
	def __init__(self, x, y):
#Same functions go for the reset method
		self.reset(x,y)

	def update(self, game_over):
		dx = 0
		dy = 0

#5 iterations needed to pass before changing the index of the images
		walk_cooldown = 5

#To allow measuring the rate of collision of the player with the platforms
		collision_thresh=20

#if game isn't over all of the following is happening.
		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air== False:
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
#counter goes up ONLY when i press the keys not all the time
				self.counter += 1
				self.direction = 1

#To prevent the stop of player mid animation and with wrong direction image
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0

 #To resit the position at same direction istantinsously at stop
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]

			#handle animation
#Resetting the counter back to 0 to slow down the animation every 20 iteratons            
			if self.counter > walk_cooldown:
				self.counter = 0	
				self.index += 1

 #To prevent the for loop index from running beyond range oflist
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


#add gravity
#In case of positive velocity= falling and the opposite is jumping
			self.vel_y += 1

#when velocitiy of y reaches 10, it imediately decreases by gravity.
			if self.vel_y > 10:
				self.vel_y = 10

 #As y increases, velocity of the jump increases
			dy += self.vel_y

			#check for collision
			self.in_air= True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air=False

			#check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1

			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1

			#check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1

			#check for collision with platforms
			for platform in platform_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < collision_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < collision_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction
#check collision at new position then adjust player position update player coordinates
			self.rect.x += dx
			self.rect.y += dy

#if the game over happened
		elif game_over == -1:
			self.image = self.dead_image
			draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)

			#To limit the rising of the ghost
			if self.rect.y > 70:
				self.rect.y -= 5

		#draw player onto screen
		screen.blit(self.image, self.rect)
		pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

#Ends the previous functions
		return game_over


#Creates a reset function to reset back the game after game over
	def reset(self,x,y):
		self.images_right = []
		self.images_left = []

#Responsible for displaying various images
		self.index = 0

#Responsible for walking animation
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/guy{num}.png')
			img_right = pygame.transform.scale(img_right, (30, 60))

#Instead of uploading images of player facing left, we will reflect the current images on y axis
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/ghost.png')
		self.image = self.images_right[self.index]

#Creating rectangle is very important for adding collison
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False

#Defaulting the direction without motion
		self.direction = 0

#To control infinite jumps in the air
		self.in_air= True


#World functions
class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_img = pygame.image.load('img/dirt.png')
		grass_img = pygame.image.load('img/grass.png')

#Responsible for choosing suitable tile to form homogenous world
		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
#To display dirt tile
				if tile == 1:
					img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
#To display grass tile
				if tile == 2:
					img = pygame.transform.scale(grass_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
#To display enemies
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size - 5)
					blob_group.add(blob)
#To display horizontal platforms
				if tile == 4:
					#To direct platforms to the direction of motion = 1 in x-axis direction
					platform = Platfrom(col_count * tile_size, row_count * tile_size ,1,0)
					platform_group.add(platform)
#To display vertical platforms
				if tile == 5:
					#To direct platforms to the direction of motion = 1 in y-axis direction
					platform = Platfrom(col_count * tile_size, row_count * tile_size ,0,1)
					platform_group.add(platform)
#To display lava
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
#To add coins
				if tile==7:
					coin= Coin(col_count*tile_size+(tile_size//2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
#To display exit level gate
				if tile==8:
					exit=Exit_gate(col_count * tile_size, row_count * tile_size-(tile_size//2) )
					exit_group.add(exit)
#To make sure the whole list 20 tiles goes through same loop
				col_count += 1
			row_count += 1


#Responsible for displaying the previously constructed tiles
	def draw(self):
		for tile in self.tile_list:


#Tuple= (tile[0]= image) and (tile[1]= rectangle)
#2 is the rectangle line thickness
			screen.blit(tile[0], tile[1])
			pygame.draw.rect(screen, (255, 255, 255), tile[1], 2)


#To create enemy
class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/blob.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
#To limit their moving in a certain direction
		self.move_counter = 0

	def update(self):
 #To create a movement to the enemies
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

#To create platforms
class Platfrom(pygame.sprite.Sprite):
#Platforms will move either horizontal or vertical based on which is 0 and which is 1 out of move_x and move_y
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/platform.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0
		self.move_x= move_x
		self.move_y= move_y


	def update(self):
 #To create a movement to the enemies
		self.rect.x += self.move_direction*self.move_x
		self.rect.y += self.move_direction*self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1

#To create lava 
class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


#To create coins
class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/coin.png')
		self.image = pygame.transform.scale(img, (tile_size//2, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x,y)


#To create exit gate 
class Exit_gate(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


#Buttons instance 
Restart_button= Button(screen_width//2- 50, screen_height//2 +100, Restart_img)
start_button= Button(screen_width//2- 280, screen_height//2 , start_img)
exit_button= Button(screen_width//2+ 50, screen_height//2, exit_img)


#To adjust player's posture above tiles
player = Player(90, screen_height - 100)

#Kind of like a list you can add enemies to
blob_group = pygame.sprite.Group()

#Lava group instance
lava_group = pygame.sprite.Group()

#Exit gate group instance
exit_group = pygame.sprite.Group()

#coin group instance
coin_group= pygame.sprite.Group()

#platform group instance
platform_group= pygame.sprite.Group()


#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)


#load in levels variable data and create worlds
if path.exists(f'level{level}_data'):
#defines file i am targeting and put 'rb'= read binary
	pickle_in= open(f'level{level}_data','rb')
#load in levels data and create world
	world_data= pickle.load(pickle_in)
world = World(world_data)


#Mainly game run and game off  switch
finished = False
while not finished:

#To activate every previously constructed function and class 
	clock.tick(fps)
	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (100, 100))
	if main_menu==True:
		if exit_button.draw():
			finished= True	
		elif start_button.draw():
			main_menu= False
	else:
		world.draw()
  
	#if game is running display all of the following
		if game_over == 0:
			blob_group.update()
			platform_group.update()
						#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, coin_group, True) :
				score += 1
			draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

		blob_group.draw(screen)
		lava_group.draw(screen)
		exit_group.draw(screen)
		coin_group.draw(screen)
		platform_group.draw(screen)
		game_over = player.update(game_over)


	#if player dies show restart button and restart same level
		if game_over== -1:
			if Restart_button.draw():
				world_data=[]
				world= reset_level(level)
				game_over=0
				score=0


	#if player won pass the level and open next level
		elif game_over==1:
			#reset game and go to next level
			level+=1
			#if player passed the maximum constructed level
			if level<=8:
				#reset level
				world_data=[]
				world= reset_level(level)
				game_over=0
			else:
				draw_text('YOU WON!', font, blue, (screen_width // 2) - 140, screen_height // 2)
			 #restart the game
				if Restart_button.draw():
					level=1
					world_data=[]
					world= reset_level(level)
					game_over=0
					score=0


#To command the game system to stop at clicking on the close control
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			finished = True

	pygame.display.update()

#close game
pygame.quit()