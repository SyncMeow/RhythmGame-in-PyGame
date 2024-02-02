import pygame 
import time
import math
import choose_song

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Rhythm Game")
clock = pygame.time.Clock()

#const
TAP_KEY = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
FPS = 240
TICK = 1/FPS
TAP_SCALE = 85

#region variables
started = False
running = True
initiated = False

combo = 0

mouse = ""
last_key_status = {}

start_time = 0

drop_before_arrive = 0.45
prepare_time = 2
pixel_per_second = (515+TAP_SCALE/2) / drop_before_arrive

notes = []
showing_array = []
judgement_showing_array = []
hit_array = [False for i in range(4)] #records if the rail has hitted
pointer = 0
music_start = False

font = pygame.font.Font("freesansbold.ttf", 75)
#endregion

#region objects
perfect_judgement = pygame.image.load("./assets/imgs/perfect.png")
great_judgement = pygame.image.load("./assets/imgs/great.png")
good_judgement = pygame.image.load("./assets/imgs/good.png")
miss_judgement = pygame.image.load("./assets/imgs/miss.png")

tap = pygame.image.load("./assets/imgs/tap.png")
c_tap = pygame.image.load("./assets/imgs/c_tap.png")

hold_head = pygame.image.load("./assets/imgs/hold_head.png")
hold_body = pygame.image.load("./assets/imgs/hold_body.png")
hold_back = pygame.image.load("./assets/imgs/hold_back.png")

c_hold_head = pygame.image.load("./assets/imgs/c_hold_head.png")
c_hold_body = pygame.image.load("./assets/imgs/c_hold_body.png")
c_hold_back = pygame.image.load("./assets/imgs/c_hold_back.png")

start_menu = pygame.image.load("./assets/imgs/start_menu.png")
start_button = pygame.image.load("./assets/imgs/start_button.png")

tap = pygame.transform.scale(tap, (TAP_SCALE, TAP_SCALE))
c_tap = pygame.transform.scale(c_tap, (TAP_SCALE, TAP_SCALE))
hold_head = pygame.transform.scale(hold_head, (TAP_SCALE, TAP_SCALE))
hold_body = pygame.transform.scale(hold_body, (TAP_SCALE, TAP_SCALE))
hold_back = pygame.transform.scale(hold_back, (TAP_SCALE, TAP_SCALE))
c_hold_head = pygame.transform.scale(c_hold_head, (TAP_SCALE, TAP_SCALE))
c_hold_body = pygame.transform.scale(c_hold_body, (TAP_SCALE, TAP_SCALE))
c_hold_back = pygame.transform.scale(c_hold_back, (TAP_SCALE, TAP_SCALE))
start_menu = pygame.transform.scale(start_menu, (1200, 900))
start_button = pygame.transform.scale(start_button, (300, 300))
perfect_judgement = pygame.transform.scale(perfect_judgement, (200, 97))
great_judgement = pygame.transform.scale(great_judgement, (200, 97))
good_judgement = pygame.transform.scale(good_judgement, (200, 97))
miss_judgement = pygame.transform.scale(miss_judgement, (200, 97))
combo_text = font.render("0", True, (230, 230, 230))

white_back = pygame.Rect(0, 0, 800, 600)
border_left_line = pygame.Rect(140, 0, 10, 600)
border_right_line = pygame.Rect(650, 0, 10, 600)
judge_line = pygame.Rect(150, 505, 500, 20)
display_pressed1 = pygame.Rect(150, 505, 125, 20)
display_pressed2 = pygame.Rect(275, 505, 125, 20)
display_pressed3 = pygame.Rect(400, 505, 125, 20)
display_pressed4 = pygame.Rect(525, 505, 125, 20)
#endregion

display_selector = {0:tap, 
                    1:c_tap, 
                    2:hold_head, 
                    3:c_hold_head, 
                    4:hold_body, 
                    5:c_hold_body, 
                    6:hold_back, 
                    7:c_hold_back, 
                    11:perfect_judgement, 
                    22:great_judgement, 
                    33:good_judgement, 
                    44:miss_judgement
                    }

class Tap():
    def __init__(self, note_type, drop_time, arrive_time, xcor, ycor, block, block_idx) -> None:
        self.note_type = note_type#0: tap, 1:c_tap, 2:hold, 3:c_hold
        self.drop_time = drop_time
        self.arrive_time = arrive_time
        self.xcor = xcor
        self.ycor = ycor
        self.block = block
        self.block_idx = block_idx
        self.hit = False
        self.hittime = -1
        self.show = True
    
    def ycor_update(self, time_pass):
        dropping = time_pass - self.drop_time #time since dropped
        self.ycor = -TAP_SCALE + pixel_per_second * dropping
    
    #miss > 100ms good: 50ms ~ 100ms great: 30ms ~ 50ms perfect: 30ms 
    def check_remove(self, time_pass):
        block_check = input_keys[self.block]
        hit_time_check = abs(time_pass - self.arrive_time) <= 0.12
        hit_time = abs(time_pass - self.arrive_time)
        if hit_time <= 0.12 and self.show and block_check:
            if time_pass - self.arrive_time > 0:
                print('+', end = '')
            print(f'{int(1000*(time_pass - self.arrive_time))} ms', end = ' ')
        judgement = 44
        if 0.08 < hit_time and hit_time <= 0.12:
            judgement = 33
        elif 0.04 < hit_time and hit_time <= 0.08:
            judgement = 22
        elif hit_time <= 0.04:
            judgement = 11
        
        return block_check and hit_time_check, judgement

class Hold():
    def __init__(self, 
                 note_type, 
                 head_drop_time, 
                 head_arrive_time, 
                 back_drop_time, 
                 back_arrive_time, 
                 xcor, 
                 ycor, 
                 block):
        self.note_type = note_type
        self.head_drop_time = head_drop_time
        self.head_arrive_time = head_arrive_time 
        self.back_drop_time = back_drop_time
        self.back_arrive_time = back_arrive_time
        self.xcor = xcor
        self.ycor = ycor
        self.block = block

        self.hit = False
        self.head_hittime = -1
        self.hold_process = 0
        self.show = True

        self.hold_times = 0

        print(f"arrive {self.back_arrive_time}")
        n_bodies = max(int((self.back_arrive_time - self.head_arrive_time)*pixel_per_second/TAP_SCALE), 1)
        print(n_bodies)
        self.body_ycor = [[0,0] for i in range(n_bodies)] #(pressed, ycor)
    
    def ycor_update(self, time_pass):
        dropping = time_pass - self.head_drop_time #time since dropped
        self.ycor = -TAP_SCALE + pixel_per_second * dropping
        for i in range(len(self.body_ycor)):
            self.body_ycor[i][1] = self.ycor - TAP_SCALE*(i+1)

    def check_remove(self, time_pass):
        block_check = input_keys[self.block]
        hit_time = abs(time_pass - self.head_arrive_time)
        hit_time_check = hit_time <= 0.12
        if hit_time <= 0.12 and self.show and block_check:
            print(time_pass - self.head_arrive_time)
        judgement = 44
        if 0.1 < hit_time and hit_time <= 0.12:
            judgement = 33
        elif 0.06 < hit_time and hit_time <= 0.1:
            judgement = 22
        elif hit_time <= 0.06:
            judgement = 11
        
        return block_check and hit_time_check, judgement

    def body_check(self, raw_input):
        return raw_input[self.block]

def load_chart(song):
    pygame.mixer.music.load(f"./songs/{song}/music.wav")

    with open(f"./songs/{song}/chart.txt", "r") as f:
        for i in f:
            if "&" in i:
                break 
            atime, pos = i.split(' ')[0], i.split(' ')[1]
            head_arrive_time = round(int(atime)/1000, 4)
            tmp_array = []
            for n in pos.split(','):
                is_multipress = len(pos.split(',')) > 1
                if ';' in n:
                    xcor, back_arrive_time = int(n.split(';')[0]), int(n.split(';')[1])                                                        
                    back_arrive_time = round(back_arrive_time/1000, 4)

                    tmp_array.append((2+is_multipress, 
                                    int(xcor), 
                                    back_arrive_time + prepare_time, 
                                    round(back_arrive_time - drop_before_arrive + prepare_time, 4)
                                    ))
                else:
                    tmp_array.append((0+is_multipress, int(n), -1, -1))

            notes.append((head_arrive_time+ prepare_time,
                        round(head_arrive_time - drop_before_arrive + prepare_time, 4), 
                        tmp_array))

def collidepoint(pos, x1, y1, x2, y2):
    return x1 <= pos[0] and pos[0] <= x2 and y1 <= pos[1] and pos[1] <= y2

def pygame_events():
    global running 
    global mouse
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.mixer.music.stop()
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = "down"
        if event.type != pygame.MOUSEBUTTONDOWN:
            mouse = ""
    
    for i in range(4):
        hit_array[i] = False
    
def draw_back():
    pygame.draw.rect(screen, (0, 0, 0), white_back)
    pygame.draw.rect(screen, (120, 120, 120), border_left_line)
    pygame.draw.rect(screen, (120, 120, 120), border_right_line)

    pygame.draw.rect(screen, (170, 170, 170), judge_line)

    pygame.draw.line(screen, (255, 255, 255), (275, 0),(275, 600))
    pygame.draw.line(screen, (255, 255, 255), (400, 0),(400, 600))
    pygame.draw.line(screen, (255, 255, 255), (525, 0),(525, 600))
    
def background_display(time_pass, mouse_pos):
    global started
    global start_time
    global start_button
    global music_start
    if started:
        if not music_start and abs(time_pass-prepare_time) <= 5*TICK:
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play()
            music_start = True
        draw_back()
    else:
        screen.blit(start_menu, (0,0))
        screen.blit(start_button, (370, 30))
        if collidepoint(mouse_pos, 370, 30, 370+300, 30+300):
            if mouse == "down":
                started = True
                target = choose_song.main()
                load_chart(target)
                time.sleep(0.5)
                start_time = time.time()

def draw_press(keys):
    if keys[TAP_KEY[0]]:
        pygame.draw.rect(screen, (150, 150, 150), display_pressed1)
    if keys[TAP_KEY[1]]:
        pygame.draw.rect(screen, (150, 150, 150), display_pressed2)
    if keys[TAP_KEY[2]]:
        pygame.draw.rect(screen, (150, 150, 150), display_pressed3)
    if keys[TAP_KEY[3]]:
        pygame.draw.rect(screen, (150, 150, 150), display_pressed4)

def showingArray_appending(time_pass):
    global showing_array
    global pointer 
    coresponding_location = [150, 275, 400, 525]
    while pointer < len(notes) and abs(time_pass - notes[pointer][1]) <= 5*TICK:
        #print(notes[pointer][1], time_pass)
        new_notes = []
        for i in range(len(notes[pointer][2])):
            (note_type, xcor, back_arrive_time, back_drop_time) = notes[pointer][2][i]
            if note_type in [0, 1]:
                new_notes.append(Tap(note_type, 
                                    notes[pointer][1], 
                                    notes[pointer][0], 
                                    coresponding_location[xcor] + (125-TAP_SCALE)/2, 
                                    -TAP_SCALE + pixel_per_second*(time_pass - notes[pointer][1]), 
                                    TAP_KEY[xcor],
                                    xcor
                                    ))
            elif note_type in [2, 3]:
                new_notes.append(Hold(note_type, 
                                    notes[pointer][1], 
                                    notes[pointer][0], 
                                    back_arrive_time,
                                    back_drop_time,
                                    coresponding_location[xcor] + (125-TAP_SCALE)/2, 
                                    -TAP_SCALE + pixel_per_second*(time_pass - notes[pointer][1]), 
                                    TAP_KEY[xcor]
                                    ))

        showing_array.append(new_notes)
        pointer += 1

def note_displaying(time_pass):
    global showing_array
    global combo
            
    for new_notes in showing_array:
        for one_note in new_notes:
            if one_note.show:
                if type(one_note) == Tap:
                    one_note.ycor_update(time_pass)
                    show_type = display_selector[one_note.note_type]
                    screen.blit(show_type, (one_note.xcor, one_note.ycor))
                elif type(one_note) == Hold:
                    one_note.ycor_update(time_pass)
                    if not one_note.hit:
                        screen.blit(display_selector[one_note.note_type], (one_note.xcor, one_note.ycor))
                    
                    for i in one_note.body_ycor:
                        if i[0]:
                            continue
                        if i == len(one_note.body_ycor)-1:
                            screen.blit(display_selector[one_note.note_type], (one_note.xcor, one_note.back_ycor))
                        else:
                            screen.blit(display_selector[one_note.note_type], (one_note.xcor, i[1]))
                    
            if one_note.ycor >= 900 and one_note.show:
                if type(one_note) == Hold:
                    if one_note.body_ycor[-1][1] >= 900:
                        one_note.show = False
                else:
                    one_note.show = False
                combo = 0
                print(combo)
                judgement_showing_array.append((44, one_note.xcor, 80))
                print("miss")

def note_remove(time_pass, raw_input):
    global combo
    global hit_array
    corresponding_judgement = {11:"perfect", 22:"great", 33:"good", 44:"miss"}

    for new_notes in showing_array:
        for one_note in new_notes:
            can_remove, judgement_code = one_note.check_remove(time_pass)
            if type(one_note) == Hold:
                if can_remove and not one_note.hit:
                    one_note.hit = True
                    judgement_showing_array.append((judgement_code, one_note.xcor, 60))
                    print(corresponding_judgement[judgement_code])

                if raw_input[one_note.block]:
                    for i, t in enumerate(one_note.body_ycor):
                        if not t[0] and t[1] <= 525:
                            one_note.body_ycor[i] = [1, t[1]]
                            one_note.hold_times += 1
            else:
                if can_remove and not one_note.hit:
                    if judgement_code == 44:
                        combo = 0
                    else:
                        combo += 1
                    print(combo)
                    judgement_showing_array.append((judgement_code, one_note.xcor, 60))#60*TICK
                    one_note.show = False
                    print(corresponding_judgement[judgement_code])

def judgement_displaying(time_pass):
    for i, (jud, xcor, remain) in enumerate(judgement_showing_array):
        if remain == 0: 
            continue
        judgement_type = display_selector[jud]
        screen.blit(judgement_type, (xcor-62, 400))
        judgement_showing_array[i] = (jud, xcor, remain-1)

def combo_displaying():
    if started:
        combo_text = font.render(f"{combo}", True, (230, 230, 230))
        
        if combo != 0:
            screen.blit(combo_text, (400 - (20*math.ceil(math.log10(combo))), 150))
        else:
            screen.blit(combo_text, (380, 150))

def input_handler(input_keys):
    global last_key_status

    return_keys = {}
    for i in TAP_KEY:
        return_keys[i] = input_keys[i]
    
    if last_key_status:
        for k in TAP_KEY:
            if last_key_status[k] and return_keys[k]:
                return_keys[k] = False
    
    last_key_status = input_keys

    return return_keys

while running:
    time_pass = time.time() - start_time
    mouse_pos = pygame.mouse.get_pos()
    raw_input = pygame.key.get_pressed()
    input_keys = input_handler(raw_input)

    pygame_events()
    background_display(time_pass, mouse_pos)
    draw_press(raw_input)
    showingArray_appending(time_pass)
    note_displaying(time_pass)
    note_remove(time_pass, raw_input)
    judgement_displaying(time_pass)
    combo_displaying()

    pygame.display.update()
    clock.tick(FPS)
