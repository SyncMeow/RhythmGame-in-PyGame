import os
import pygame
import time

pygame.init()

screen = pygame.display.set_mode((800,600))
clock = pygame.time.Clock()

background = pygame.image.load('./assets/imgs/bg_choose.png')
background = pygame.transform.scale(background, (800,600))
transparent = pygame.image.load('./assets/imgs/transparent.png')
transparent = pygame.transform.scale(transparent, (800,400))

FPS=240
WIDTH=800
HEIGHT=600
BLOCK_SIZE = 300
LEFT_BOUND = BLOCK_SIZE/2
RIGHT_BOUND = 800 - BLOCK_SIZE*3/2

cur_index = 0
cur_song = None
delay = 0.2
last_press_time = 0
moveing_rate = 0

end_phase = False

button_clicked=False
WHITE=((255,255,255))

class Song(pygame.sprite.Sprite):
    def __init__(self, x, y, name, cover, track):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.cover = cover
        self.image = pygame.transform.scale(self.cover, (BLOCK_SIZE, BLOCK_SIZE))
        self.track = track
        self.rect =  self.image.get_rect()
        self.rect.center = (x,y)
    
    def update(self,x):  
        self.rect.x += x
        

all_sprites = pygame.sprite.Group()

songs = os.listdir("./songs")
song_list = []
for i, song_name in enumerate(songs):
    xcor = -BLOCK_SIZE + i * 1.5 * BLOCK_SIZE
    cover = pygame.image.load(f'./songs/{song_name}/bg.png')
    track = f"./songs/{song_name}/music.wav"
    tmpSong = Song(xcor, 300, song_name, cover, track)
    song_list.append(tmpSong)

all_sprites.add(song_list)
show_init=True
running=True

def update_background():
    screen.fill((255, 255, 255))
    screen.blit(background, background.get_rect())
    screen.blit(transparent, (0,100))

def pygame_events():
    global cur_index
    global last_press_time
    global moveing_rate
    global end_phase

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            pygame.mixer.quit()
            pygame.quit()

        if pygame.mouse.get_pressed()[0]:
            end_phase = True
        #exit
        
        if time.time() - last_press_time >= delay:
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                cur_index = max(cur_index - 1, 0)
                last_press_time = time.time()
            elif pygame.key.get_pressed()[pygame.K_RIGHT]:
                cur_index = min(cur_index + 1, len(song_list)-1)
                last_press_time = time.time()
        
        all_sprites.update(400 - song_list[cur_index].rect.x - BLOCK_SIZE/2)


def music_play():
    global cur_song
    if song_list[cur_index].track != cur_song:
        cur_song = song_list[cur_index].track
        pygame.mixer.music.load(song_list[cur_index].track)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play()


def main():
    while running:
        update_background()
        pygame_events()

        if end_phase:
            return song_list[cur_index].name
        
        all_sprites.draw(screen)
        music_play()
        
        pygame.display.update()
        clock.tick(FPS)
    
