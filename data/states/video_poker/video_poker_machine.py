import pygame as pg
from ... import tools, prepare
from ...components.labels import Blinker, Label, FunctionButton
from ...components.cards import Deck

PAYTABLE = [
    (800, 50, 25, 8, 6, 4, 3, 2, 1),
    (1600, 100, 50, 16, 12, 8, 6, 4, 2),
    (2400, 150, 75, 24, 18, 12, 9, 6, 3),
    (3200, 200, 100, 32, 24, 16, 12, 8, 4),
    (4000, 250, 125, 40, 30, 20, 15, 10, 5),
]

class PayBoard:
    def __init__(self, topleft, size):
        self.rect = pg.Rect(topleft, size)
        self.table = []
        self.lines = []

        self.font = prepare.FONTS["Saniretro"]
        self.text_size = 30
        self.line_height = 35
        self.text_color = "yellow"

        self.border_size = 5
        self. border_color =pg.Color('gold')
        self.bg_color = pg.Color('darkblue')

        self.col_space = int(self.rect.w / 6)
        self.padding = 10

        self.bet_rect = pg.Rect(( self.rect.left, self.rect.top),
                                 (self.col_space, self.rect.h))
        self.bet_rect_color = pg.Color("red")
        self.show_bet_rect = False

        self.build()

    def update_bet_rect(self, bet):
        self.bet_rect.left = self.rect.left + self.col_space * bet
        self.show_bet_rect = True
        
    def build(self):
        info_col = ('ROYAL FLUSH', 'STR. FLUSH', '4 OF A KIND', 'FULL HOUSE',
        'FLUSH','STRAIGHT', 'THREE OF A KIND', 'TWO PAIR', 'JACKS OR BETTER')
        x = x_initial = self.rect.left + self.padding
        y = y_initial = self.rect.top + self.padding
        for row in info_col:
            label = Label(self.font, self.text_size, row, self.text_color,
                                      {"topleft": (x, y)})
            self.table.append(label)
            y += self.line_height


        x += self.col_space*2 - self.padding*2
        y = y_initial
        for col in PAYTABLE:
            for row in col:
                text = str(row)
                label = Label(self.font, self.text_size, text, self.text_color,
                                      {"topright": (x, y)})
                self.table.append(label)
                y += self.line_height
            x += self.col_space
            y = y_initial

        # borders between cols
        x = self.rect.left + self.col_space
        y0 = self.rect.top
        y1 = self.rect.bottom
        for i in range(5):
            line = [(x, y0), (x, y1)]
            self.lines.append(line)
            x += self.col_space




    def draw(self, surface):
        pg.draw.rect(surface, self.bg_color, self.rect)
        if self.show_bet_rect:
            pg.draw.rect(surface, self.bet_rect_color, self.bet_rect)
        pg.draw.rect(surface, self.border_color, self.rect, self.border_size)
        for label in self.table:
            label.draw(surface)
        
        for line in self.lines:
            pg.draw.line(surface, self.border_color, line[0], line[1], self.border_size)

class CardsTable:
    def __init__(self, topleft, size):
        self.rect = pg.Rect(topleft, size)

        self.deck = Deck((20, 20), card_size=(187, 271), infinite=True)

        self.font = prepare.FONTS["Saniretro"]
        self.text_size = 30
        self.big_text_size = 100
        self.line_height = 35
        self.text_color = "white"
        self.big_text_color = "red"
        self.text_bg_color = "darkblue"

        self.held_labels = []
        

        
        self.text = "Play 1 to 5 coins"
        self.standby_label = Blinker(self.font, self.big_text_size, self.text, self.big_text_color,
                                      {"center":self.rect.center}, 700, self.text_bg_color)

        self.card_spacing = 30

        self.elapsed = 150.0


    def startup(self):
        self.hand = self.deck.make_hand()
        self.hand_len = len(self.hand)
        self.build()
        self.standby = True
        self.card_index = 0
        self.max_cards = len(self.hand)
        self.revealing = False
        self.held_cards = []

    def draw_cards(self):
        for index in range(self.hand_len):
            if index not in self.held_cards:
                self.hand[index] = self.deck.draw_card()
        self.build()
        self.revealing = True
        self.standby = False

    def build(self):
        x = self.rect.left
        y = self.rect.top  + self.line_height
        for card in self.hand:
            card.rect.left = x
            card.rect.top = y
            label = Label(self.font, self.text_size, 'held', self.text_color,
                                      {"bottom":card.rect.top, "centerx":card.rect.centerx})
            self.held_labels.append(label)
            x += self.card_spacing + card.rect.w



    def face_up_cards(self):
        for card in self.hand:
            card.face_up = True

    def toogle_held(self, index):
        if index in self.held_cards:
            self.held_cards.remove(index)
        else:
            self.held_cards.append(index)


    def get_event(self, mouse_pos):
        for index, card in enumerate(self.hand):
            if card.rect.collidepoint(mouse_pos):
                self.toogle_held(index)

    def update(self, dt):
        if self.revealing:
            self.elapsed += dt
            while self.elapsed >= 150.0:
                self.elapsed -= 150.0
                self.hand[self.card_index].face_up = True
                self.card_index += 1
                if self.card_index >= self.max_cards:
                    self.card_index = 0
                    self.revealing = False

    def draw(self, surface, dt):
        for card in self.hand:
            card.draw(surface)
        for index in self.held_cards:
            self.held_labels[index].draw(surface)
        if self.standby:
            self.standby_label.draw(surface, dt)


class Machine:
    def __init__(self, topleft, size):
        self.rect = pg.Rect(topleft, size)
        
        self.font = prepare.FONTS["Saniretro"]
        self.text_size = 30
        self.text_color = "white"
        self.padding = 25

        self.buttons = []
        self.btn_width = self.btn_height = 100
        self.btn_padding = 35
        self.info_labels = []

        self.max_bet = 5
        self.bet = 0
        self.credits = 20
        self.coins = 0

        self.build()

    def startup(self):
        self.cards_table.startup()


    def build(self):
        x, y = self.rect.topleft
        w, h = self.rect.size

        # calculate pay board position
        x += self.padding
        y += self.padding
        w -= self.padding*2
        h = 330
        self.pay_board = PayBoard((x,y), (w,h))

        # use in info labels
        self.label_x1 = x 
        self.label_x2 = w

        # calculate cards table position position
        y += self.padding + self.pay_board.rect.h
        h = 300
        self.cards_table = CardsTable((x,y), (w,h))

        y = self.cards_table.rect.bottom + self.padding*2
        self.label_y = y # use in info labels

        # buttons
        y += self.padding + self.btn_padding
        button_list = [('bet', self.bet_one, None), ('held', self.make_held, (0,)), 
                        ('held', self.make_held, (1,)), ('held', self.make_held, (2,)),
                        ('held', self.make_held, (3,)), ('held', self.make_held, (4,)), 
                        ('bet max', self.bet_max, None), ('draw', self.draw_cards, None)]
        for text, func, args in button_list:
            label = Label(self.font, self.text_size, text, self.text_color, {})
            button = FunctionButton(x, y, self.btn_width, self.btn_height, label, func, args)
            self.buttons.append(button)
            x += self.btn_width + self.btn_padding


    def bet_one(self):
        if self.credits > 0:
            if self.bet < self.max_bet:
                self.bet += 1
                if self.coins < self.max_bet:
                    self.coins += 1
                else:
                    self.coins = 1
                self.credits -= 1
            else:
                self.bet = 1
                self.coins = 1
                self.credits += 4
        self.pay_board.update_bet_rect(self.coins)

    
    def bet_max(self):
        if self.credits > 0:
            aux = self.max_bet - self.coins
            self.bet += aux
            self.coins += aux
            self.credits -= aux
        self.pay_board.update_bet_rect(self.coins)

    
    def make_last_bet(self):
        """ """
        if self.credits > 0 and self.coins > 0:
            if self.credits >= self.coins:
                self.bet = self.coins
                self.credits -= self.bet            
                self.bet = 0
            else:
                self.bet = self.credits
                self.coins = self.credits
                self.credits = 0
            self.pay_board.update_bet_rect(self.coins)

    
    def draw_cards(self):
        if self.bet > 0:
            self.cards_table.draw_cards()
            self.bet = 0
        else:
            self.make_last_bet()
            self.cards_table.draw_cards()
            self.bet = 0

            

    def test(self):
        print("Hello world")

    def make_held(self, index):
        self.cards_table.toogle_held(index)
    



    def get_event(self, mouse_pos):
        self.cards_table.get_event(mouse_pos)
        for button in self.buttons:
            button.get_event(mouse_pos)

    def update(self, dt):
        # game info labels
        self.info_labels = []
        credit_text = 'Credit {}'.format(self.credits)
        label = Label(self.font, self.text_size, credit_text, self.text_color, 
                        {"topright": (self.label_x2, self.label_y)})
        self.info_labels.append(label)
        coins_text = "Coins in {}".format(self.coins)
        label = Label(self.font, self.text_size, coins_text, self.text_color, 
                        {"topleft": (self.label_x1, self.label_y)})
        self.info_labels.append(label)

        self.cards_table.update(dt)


    def draw(self, surface, dt):
        self.pay_board.draw(surface)
        self.cards_table.draw(surface, dt)
        for label in self.info_labels:
            label.draw(surface)
        for button in self.buttons:
            button.draw(surface)


