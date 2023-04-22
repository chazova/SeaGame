from random import randint


class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"

# a = Dot(1,2)
# b = [a]
# print(a)
# print(Dot(2, 2) in b)

class Ship:
    def __init__(self, length, start, direction):
        self.length = length
        self.start = start
        self.direction = direction
        self.lives = length
    @property
    def dots(self):
        # ship_dots = [self.start]
        ship_dots = []
        # new_x = self.start.x
        # new_y = self.start.y
        for i in range(self.length):
            new_x = self.start.x
            new_y = self.start.y
            if self.direction == 0:
                new_x += i
            elif self.direction == 1:
                new_y += i
            ship_dots.append(Dot(new_x, new_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

# ship_1 = Ship(5, Dot(1,1), 0)
# print(ship_1.dots)
# print(ship_1.shooten(Dot(2, 2)))

class Board:
    def __init__(self, size = 6, hid = False):
        self.size = size
        self.hid = hid
        self.field = [["O"] * size for _ in range(size)]
        self.busy = []
        self.ships = []
        self.count = 0

    def __str__(self):
        result = ""
        # result += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        result += " | ".join(str(_) for _ in range(self.size + 1)) + " |"
        count = 0
        for i in self.field:
            count += 1
            result += f"\n" + str(count) + " | " + " | ".join(i) + " |"
        if self.hid:
            result = result.replace("O", "■")
        return result

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))
        # return not ((0 <= d.x <= self.size) and (0 <= d.y <= self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# class AI(Player):
#     def ask(self):
#         d = Dot(randint(0, 5), randint(0, 5))
#         print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
#         return d

class AI(Player):
    def ask(self):
        d = Dot(-1, -1)
        while (d in self.enemy.busy) or d == Dot(-1, -1):
            d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(length, Dot(randint(0, self.size), randint(0, self.size)), randint(0,1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def print_boards(self):
        result_1 = ""
        result_1 += " | ".join(str(_) for _ in range(self.us.board.size + 1)) + " |" + \
                   "  " * self.size + " | ".join(str(_) for _ in range(self.us.board.size + 1)) + " |"
        count = 0
        for i, j in list(zip(self.us.board.field, self.ai.board.field)):
            count += 1
            us_res = " | ".join(i)
            ai_res = " | ".join(j)
            if self.us.board.hid:
                us_res = us_res.replace("O", "■")
            if self.ai.board.hid:
                ai_res = ai_res.replace("O", "■")
            result_1 += f"\n" + str(count) + " | " + us_res + " |" + \
                       "  " * self.size + str(count) + " | " + ai_res + " |"
        print(f"Доска пользователя:{'   ' * self.size}  Доска компьютера:")
        print(result_1)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            # print(f"Доска пользователя:{'   ' * self.size}  Доска компьютера:")
            # print(self.print_boards())
            # print("-" * 20)
            # print("Доска пользователя:")
            # print(self.us.board)
            # print("-" * 20)
            # print("Доска компьютера:")
            # print(self.ai.board)
            # print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                self.print_boards()
                print("Пользователь выиграл!")

                break

            if self.us.board.count == len(self.us.board.ships):
                print("-" * 20)
                self.print_boards()
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()

# ship_1 = Ship(5, Dot(1,1), 1, 1)
#
# board_1 = Board(size = 9)
# board_1.add_ship(ship_1)
#
# print(board_1)
