import random
from tkinter import Tk, Label, Button, Canvas, Entry
import numpy


class MyFirstGUI:
    def __init__(self, master):
        self.master = master
        self.canvas = Canvas(self.master, width=550, height=550)
        self.chance_card_move_to = [0, 5, 11, 24, 30, 39]
        self.default_move_count = 100

        # Variables for statistics
        self.position_landed_count = [0] * 40

        # Constants
        self.chance_card_out_jail_card = "Get out of jail card"
        self.chance_card_collect_money = "Collect money card"
        self.chance_card_advance_on_board = "Advance somewhere on board card"
        self.chance_card_pay_money = "Pay money card"
        self.chance_card_go_jail_card = "Go to jail card"
        self.monopoly_board_dictionary = [
            "Start",
            "Mediterranean Avenue",
            "Community Chest",
            "Baltic Avenue",
            "Income Tax",
            "Reading Railroad",
            "Oriental Avenue",
            "Chance",
            "Vermont Avenue",
            "Connecticut Avenue",
            "Jail Visiting",
            "St. Charles Place",
            "Electric Company",
            "State Avenue",
            "Virginia Avenue",
            "Pennsylvania Railroad",
            "St. James Place",
            "Community Chest",
            "Tennessee Avenue",
            "New York Avenue",
            "Free Parking"
            "Kentucky Avenue",
            "Chance",
            "Indiana Avenue",
            "Illinois Avenue",
            "B. & O. Railroad",
            "Atlantic Avenue",
            "Ventnor Avenue",
            "Water Works",
            "Marvin Gardens",
            "Go to Jail",
            "Pacific Avenue",
            "North Carolina Avenue",
            "Community Chest",
            "Pennsylvania Avenue",
            "Short Line",
            "Chance",
            "Park Place",
            "Luxury Tax",
            "Boardwalk",
        ]

        master.title("A simple GUI")
        master.geometry("553x600")
        master.resizable(0, 0)

        self.greet_button = Button(master, text="Start Simulation", command=self.greet)
        self.greet_button.pack()
        self.greet_button.place(x=10, y=560)

        self.close_button = Button(master, text="Close", command=master.quit)
        self.close_button.pack()
        self.close_button.place(x=480, y=560)

        self.entry = Entry(master)
        self.entry.pack()
        self.entry.place(x=150, y=560)

    # Simulates a dice roll in Monopoly
    # the result is the sum of rolling two dices
    # if a roll yields dices with equal numbers then the dices are rolled again the sum is added to the total result
    def dice_roll(self):
        total = 0
        dice_one = random.randint(1, 6)
        dice_two = random.randint(1, 6)
        total += dice_one + dice_two
        equal_dices = False

        while dice_one == dice_two:
            equal_dices = True
            dice_one = random.randint(1, 6)
            dice_two = random.randint(1, 6)
            total += dice_one + dice_two

        return equal_dices, total

    # Simulates a chance card draw in Monopoly
    # 1/16 chance of get out of jail
    # 1/16 chance of go to jail
    # 3/16 chance of collect money
    # 3/16 chance of pay money
    # 8/16 chance of advance on board
    def draw_chance_card(self):
        card_index = random.randint(1, 16)
        if card_index == 1:
            return self.chance_card_out_jail_card
        if card_index == 2:
            return self.chance_card_go_jail_card
        if 3 <= card_index <= 5:
            return self.chance_card_collect_money
        if 6 <= card_index <= 8:
            return self.chance_card_pay_money
        if 9 <= card_index <= 16:
            return self.chance_card_advance_on_board

    def simulate_turn(self, current_position, is_jailed, rounds_in_jail, has_fail_free):
        equal_dices, roll = self.dice_roll()
        if has_fail_free:
            is_jailed = False
        if is_jailed and (equal_dices or rounds_in_jail >= 2):
            return current_position, False, 0, has_fail_free
        if is_jailed:
            return current_position, True, rounds_in_jail + 1, has_fail_free

        next_position = (current_position + roll) % 40
        self.position_landed_count[next_position] = self.position_landed_count[next_position] + 1

        # Handle chance card (goes to random position based on variable chance_card_move_to)
        if next_position == 7 or next_position == 22 or next_position == 36:
            draw_chance = self.draw_chance_card()
            if draw_chance == self.chance_card_go_jail_card:
                is_jailed = True
                next_position = 10
                self.position_landed_count[next_position] = self.position_landed_count[next_position] + 1
            elif draw_chance == self.chance_card_advance_on_board:
                go_to_index = random.randint(0, 5)
                next_position = self.chance_card_move_to[go_to_index]
                self.position_landed_count[next_position] = self.position_landed_count[next_position] + 1
            elif draw_chance == self.chance_card_out_jail_card:
                has_fail_free = True

        # Handle go to prison position
        if next_position == 30:
            is_jailed = True
            next_position = 10
            self.position_landed_count[next_position] = self.position_landed_count[next_position] + 1

        return next_position, is_jailed, 0, has_fail_free

    def simulate_game(self, move_count):
        current_position = 0
        current_move = 0
        is_jailed = False
        rounds_in_jail = 0
        has_fail_free = False

        while current_move < move_count:
            current_position, is_jailed, rounds_in_jail, has_fail_free = self.simulate_turn(current_position, is_jailed, rounds_in_jail, has_fail_free)
            # print("---> Round: ", current_move)
            # print("Current position: ", current_position)
            # print("Is Jailed: ", is_jailed)
            # print("Rounds in Jail: ", rounds_in_jail)
            current_move = current_move + 1

    def greet(self):
        # Reset variables for statistics
        self.position_landed_count = [0] * 40

        # Check how many simulation are to be run
        simulation_count = int(self.entry.get())
        if simulation_count == '':
            simulation_count = 1

        # Simulation start
        current_simulation = 0
        while current_simulation < simulation_count:
            self.simulate_game(self.default_move_count)
            current_simulation = current_simulation + 1

        position_landed_count = [x * 100 for x in self.position_landed_count]
        position_landed_count = [x / (simulation_count * self.default_move_count) for x in position_landed_count]
        print(position_landed_count)
        print(sum(position_landed_count))
        print(numpy.amax(position_landed_count))

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        minimum = numpy.amin(self.position_landed_count)
        maximum = numpy.amax(self.position_landed_count)

        for x in range(0, 10):
            normalized = int(((self.position_landed_count[x] - minimum) / (maximum - minimum)) * 255)
            color = '#%02x%02x%02x' % (255 - normalized, 255 - normalized, 255 - normalized)
            self.canvas.create_rectangle(500 - (x * 50), 500, 550 - (x * 50), 550, fill=color, outline='white')
        for x in range(0, 10):
            normalized = int(((self.position_landed_count[10 + x] - minimum) / (maximum - minimum)) * 255)
            color = '#%02x%02x%02x' % (255 - normalized, 255 - normalized, 255 - normalized)
            self.canvas.create_rectangle(0, 500 - (x * 50), 50, 550 - (x * 50), fill=color, outline='white')
        for x in range(0, 10):
            normalized = int(((self.position_landed_count[20 + x] - minimum) / (maximum - minimum)) * 255)
            color = '#%02x%02x%02x' % (255 - normalized, 255 - normalized, 255 - normalized)
            self.canvas.create_rectangle(x * 50, 0, 50 + x * 50, 50, fill=color, outline='white')
        for x in range(0, 10):
            normalized = int(((self.position_landed_count[30 + x] - minimum) / (maximum - minimum)) * 255)
            color = '#%02x%02x%02x' % (255 - normalized, 255 - normalized, 255 - normalized)
            self.canvas.create_rectangle(500, x * 50, 550, 50 + x * 50, fill=color, outline='white')

        self.canvas.pack()
        self.canvas.place(x=0, y=0)


print("Drawing")
root = Tk()
my_gui = MyFirstGUI(root)
root.mainloop()
