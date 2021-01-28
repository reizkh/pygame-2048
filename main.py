import pygame as pg
from random import randrange, random


LEFT, UP, RIGHT, DOWN = range(4)


pg.init()
game_size = 4
cell_size = 40
spacing = 8
border_radius = 7
stages = 3
fps = 60
bg_color = pg.color.Color('#fcdea2')
border_color = pg.color.Color('#573e0c')
cell_color = pg.color.Color('#cf9c53')
light_color = pg.color.Color('#ebb567')
dark_color = pg.color.Color('#825e2b')
width = game_size * cell_size + (game_size + 1) * spacing
height = width + 15
tiles = pg.sprite.Group()
screen = pg.display.set_mode((width, height))
clock = pg.time.Clock()


class Tile(pg.sprite.Sprite):
    border_width = 1
    v = (cell_size + spacing) / stages

    def __init__(self, number, pos):
        super().__init__(tiles)
        self.change = 0
        self.power = number
        self.is_changing = False
        self.is_moving = False
        self.dying = False
        self.steps = 0
        self.direction = 0, 0

        self.rect = pg.Rect(*pos, cell_size, cell_size)
        self.image = self.update_image()

    def update_image(self):
        img = pg.surface.Surface((cell_size, cell_size), pg.SRCALPHA, 32)
        font = pg.font.Font(None, cell_size)
        rect = self.rect.move(-self.rect.x, -self.rect.y)

        text = font.render(str(2 ** self.power), True, (255, 255, 255))
        text_x = (cell_size - text.get_width()) // 2
        text_y = (cell_size - text.get_height()) // 2

        col = gradient((self.power + self.change / stages) / (game_size ** 2 + 1))

        pg.draw.rect(img, col, rect, border_radius=border_radius)
        img.blit(text, (text_x, text_y))
        return img

    def update(self, *args, **kwargs) -> None:
        if self.is_changing and not self.is_moving:
            self.change += 1
            if self.change == stages:
                self.change = 0
                self.power += 1
                self.is_changing = False
            self.image = self.update_image()

        if self.is_moving:
            if self.steps == 0:
                if self.dying:
                    if len(pg.sprite.spritecollide(self, tiles, False)) > 1:
                        self.kill()
                else:
                    self.is_moving = False
                return
            self.rect.x += self.v * self.direction[0]
            self.rect.y += self.v * self.direction[1]
            self.steps -= 1

    def move(self, direction, steps, die_ite, change):
        self.direction = direction
        self.steps = steps

        self.is_moving = True
        self.dying = die_ite
        self.is_changing = change

    def b_pos(self):
        return int((self.rect.x-spacing)/(spacing+cell_size)), int((self.rect.y-spacing)//(spacing+cell_size))


def gradient(a):
    stops = {0: (246, 209, 209),
             0.25: (226, 97, 97),
             0.6: (244, 236, 112),
             1: (237, 223, 20)}
    for i, stop in enumerate(stops.keys()):
        if a < stop:
            k = (a - list(stops.keys())[i-1]) / (stop - list(stops.keys())[i-1])
            col1 = stops[list(stops.keys())[i-1]]
            col2 = stops[stop]
            blend = (col1[0]*k + col2[0]*(1-k),
                     col1[1]*k + col2[1]*(1-k),
                     col1[2]*k + col2[2]*(1-k))
            return blend


def game_over():
    try:
        with open('record', 'rb') as file:
            best = int.from_bytes(file.read(), 'big')
    except FileNotFoundError:
        best = score

    if score >= best:
        best = score
        with open('record', 'wb') as file:
            file.write(best.to_bytes(3, 'big'))
    screen.fill(bg_color)
    ng_rect = pg.Rect((width-140)//2, 40, 140, 40)
    ng_color = cell_color
    quit_rect = pg.Rect((width-140)//2, 120, 140, 40)
    quit_color = cell_color
    font = pg.font.Font(None, 30)

    new_game = font.render('Новая игра', True, (255, 255, 255))
    new_game_x = ng_rect.centerx - new_game.get_width() // 2
    new_game_y = ng_rect.centery - new_game.get_height() // 2

    quit_game = font.render('Выйти', True, (255, 255, 255))
    quit_game_x = quit_rect.centerx - quit_game.get_width() // 2
    quit_game_y = quit_rect.centery - quit_game.get_height() // 2

    score_label = font.render(f'Счёт: {score}', True, (87, 62, 12))
    score_pos = ((width-140)//2-10, 10)
    best_label = font.render(f'Рекорд: {best}', True, (87, 62, 12))
    best_pos = ((width-140)//2-10, 90)

    while True:
        screen.fill(bg_color)
        screen.blit(score_label, score_pos)
        screen.blit(best_label, best_pos)

        pg.draw.rect(screen, ng_color, ng_rect, 0, 7)
        pg.draw.rect(screen, border_color, ng_rect, 1, 7)
        screen.blit(new_game, (new_game_x, new_game_y))

        pg.draw.rect(screen, quit_color, quit_rect, 0, 7)
        pg.draw.rect(screen, border_color, quit_rect, 1, 7)
        screen.blit(quit_game, (quit_game_x, quit_game_y))

        pg.display.flip()
        for event in pg.event.get():
            if event.type == pg.MOUSEMOTION:
                if ng_rect.collidepoint(event.pos):
                    ng_color = light_color
                else:
                    ng_color = cell_color
                if quit_rect.collidepoint(event.pos):
                    quit_color = light_color
                else:
                    quit_color = cell_color
            if event.type == pg.MOUSEBUTTONDOWN:
                if ng_rect.collidepoint(event.pos):
                    ng_color = dark_color
                else:
                    ng_color = cell_color
                if quit_rect.collidepoint(event.pos):
                    quit_color = dark_color
                else:
                    quit_color = cell_color
            if event.type == pg.MOUSEBUTTONUP:
                ng_color, quit_color = cell_color, cell_color
                if ng_rect.collidepoint(event.pos):
                    start_game()
                if quit_rect.collidepoint(event.pos):
                    exit()
            if event.type == pg.QUIT:
                exit()


def start_game():
    global board, score, tiles
    tiles = pg.sprite.Group()
    board = TwentyFortyEight(game_size, cell_size, spacing)
    score = 0
    main_loop()


def main_loop():
    next_pos, next_pow = None, None
    font = pg.font.Font(None, 25)
    score_pos = (spacing, height-20)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                exit()
            if event.type == pg.KEYDOWN:
                if any(tile.is_moving or tile.is_changing for tile in tiles):
                    break
                if next_pos is not None and next_pow is not None:
                    Tile(next_pow,
                         (spacing + next_pos[1] * (spacing + cell_size), spacing + next_pos[0] * (spacing + cell_size)))
                    next_pos, next_pow = None, None
                moves = []
                if event.key == pg.K_LEFT:
                    moves, next_pos, next_pow = board.swipe(LEFT)
                if event.key == pg.K_UP:
                    moves, next_pos, next_pow = board.swipe(UP)
                if event.key == pg.K_RIGHT:
                    moves, next_pos, next_pow = board.swipe(RIGHT)
                if event.key == pg.K_DOWN:
                    moves, next_pos, next_pow = board.swipe(DOWN)

                for move in moves:
                    for tile in tiles:
                        if tile.b_pos() == move[1]:
                            tile.move(move[0], move[3], move[5], move[4])
        board.render()
        clock.tick(fps)
        tiles.draw(screen)
        tiles.update()
        if all(not(tile.is_changing or tile.is_moving) for tile in tiles) and\
                next_pos is not None and next_pow is not None:
            Tile(next_pow, (spacing+next_pos[0]*(spacing+cell_size), spacing+next_pos[1]*(spacing+cell_size)))
            next_pos, next_pow = None, None
        text = font.render(f'Cчёт: {score}', True, border_color)
        screen.blit(text, score_pos)
        pg.display.flip()


def count_score(moves, board):
    global score
    for move in moves:
        if move[4]:
            x, y = move[2]
            score += 2**board[y][x]


class TwentyFortyEight:
    def __init__(self, size, cell_size, spacing):
        self.size = size
        self.moving = False
        self.board = [[0 for i in range(self.size)] for _ in range(self.size)]
        power = 1 if random() < 0.9 else 2
        pos = randrange(self.size), randrange(self.size)
        self.board[pos[1]][pos[0]] = power
        Tile(power, (spacing+pos[0]*(spacing+cell_size), spacing+pos[1]*(spacing+cell_size)))

        self.spacing = spacing
        self.cell_size = cell_size
        self.border_width = 1

    def swipe(self, direction):
        vectors = {LEFT: (-1, 0), UP: (0, -1), RIGHT: (1, 0), DOWN: (0, 1)}
        new_board = [[0 for i in range(self.size)] for _ in range(self.size)]
        fixed = [[0 for i in range(self.size)] for _ in range(self.size)]
        moves = []
        if direction == LEFT:
            for y in range(self.size):
                for x in range(self.size):
                    current = self.board[y][x]
                    if current == 0:
                        continue
                    for x0 in range(self.size):
                        if not fixed[y][x0]:
                            last = new_board[y][x0]
                            if last == current:
                                new_board[y][x0] += 1
                                fixed[y][x0] = True
                                moves.append((vectors[direction], (x, y), (x0, y), abs(x-x0)*stages, True, False))
                                for i in range(len(moves)-1):
                                    if moves[i][2] == (x0, y):
                                        moves[i] = moves[i][:5]+(True,)
                            elif last == 0:
                                new_board[y][x0] = current
                                moves.append((vectors[direction], (x, y), (x0, y), abs(x-x0)*stages, False, False))
                            else:
                                new_board[y][x0 + 1] = current
                                fixed[y][x0] = True
                                moves.append((vectors[direction], (x, y), (x0 + 1, y), (abs(x-x0)-1)*stages, False, False))
                            break
        elif direction == UP:
            for y in range(self.size):
                for x in range(self.size):
                    current = self.board[y][x]
                    if current == 0:
                        continue
                    for y0 in range(self.size):
                        if not fixed[y0][x]:
                            last = new_board[y0][x]
                            if last == current:
                                new_board[y0][x] += 1
                                fixed[y0][x] = True
                                moves.append((vectors[direction], (x, y), (x, y0), abs(y-y0)*stages, True, False))
                                for i in range(len(moves)-1):
                                    if moves[i][2] == (x, y0):
                                        moves[i] = moves[i][:5]+(True,)
                            elif last == 0:
                                new_board[y0][x] = current
                                moves.append((vectors[direction], (x, y), (x, y0), abs(y-y0)*stages, False, False))
                            else:
                                new_board[y0 + 1][x] = current
                                fixed[y0][x] = True
                                moves.append((vectors[direction], (x, y), (x, y0 + 1), (abs(y-y0)-1)*stages, False, False))
                            break
        elif direction == RIGHT:
            for y in range(self.size):
                for x in reversed(range(self.size)):
                    current = self.board[y][x]
                    if current == 0:
                        continue
                    for x0 in reversed(range(self.size)):
                        if not fixed[y][x0]:
                            last = new_board[y][x0]
                            if last == current:
                                new_board[y][x0] += 1
                                fixed[y][x0] = True
                                moves.append((vectors[direction], (x, y), (x0, y), abs(x-x0)*stages, True, False))
                                for i in range(len(moves)-1):
                                    if moves[i][2] == (x0, y):
                                        moves[i] = moves[i][:5]+(True,)
                            elif last == 0:
                                new_board[y][x0] = current
                                moves.append((vectors[direction], (x, y), (x0, y), abs(x-x0)*stages, False, False))
                            else:
                                new_board[y][x0 - 1] = current
                                fixed[y][x0] = True
                                moves.append((vectors[direction], (x, y), (x0 - 1, y), (abs(x-x0)-1)*stages, False, False))
                            break
        elif direction == DOWN:
            for y in reversed(range(self.size)):
                for x in range(self.size):
                    current = self.board[y][x]
                    if current == 0:
                        continue
                    for y0 in reversed(range(self.size)):
                        if not fixed[y0][x]:
                            last = new_board[y0][x]
                            if last == current:
                                new_board[y0][x] += 1
                                fixed[y0][x] = True
                                moves.append((vectors[direction], (x, y), (x, y0), abs(y-y0)*stages, True, False))
                                for i in range(len(moves)-1):
                                    if moves[i][2] == (x, y0):
                                        moves[i] = moves[i][:5]+(True,)
                            elif last == 0:
                                new_board[y0][x] = current
                                moves.append((vectors[direction], (x, y), (x, y0), abs(y-y0)*stages, False, False))
                            else:
                                new_board[y0 - 1][x] = current
                                fixed[y0][x] = True
                                moves.append((vectors[direction], (x, y), (x, y0-1), (abs(y-y0)-1)*stages, False, False))
                            break
        self.board = new_board
        power = 1 if random() < 0.9 else 2
        pos = randrange(self.size), randrange(self.size)

        while self.board[pos[1]][pos[0]]:
            pos = randrange(self.size), randrange(self.size)
        self.board[pos[1]][pos[0]] = power
        for row in self.board:
            for cell in row:
                if cell == 0:
                    count_score(moves, self.board)
                    return moves, pos, power
        game_over()

    def render(self):
        left = spacing
        top = spacing
        font = pg.font.Font(None, cell_size)
        screen.fill(bg_color)
        for x in range(self.size):
            for y in range(self.size):
                rect = pg.Rect(left, top, cell_size, cell_size)
                pg.draw.rect(screen, cell_color, rect, border_radius=border_radius)
                pg.draw.rect(screen, border_color, rect, self.border_width, border_radius=border_radius)
                top += cell_size + spacing
            top = spacing
            left += cell_size + spacing


start_game()