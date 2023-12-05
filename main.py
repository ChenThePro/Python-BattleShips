import tkinter as tk
import pygame
from PIL import Image, ImageTk
import random
import socket
import time
import re
import threading
import json
LETTERS = "ABCDEFGHIJ"
NUMBERS = "123456789"
PICTURES = ["Images/Background/chen.jpg", "Images/Background/chen3.jpg", "Images/Background/chen4.jpg", "Images/Background/chen5.jpg", "Images/Background/chen6.jpg", "Images/Background/chen7.jpg", "Images/Background/chen8.jpg", "Images/Background/chen9.jpg",
            "Images/Background/chen10.jpg", "Images/Background/chen11.jpg", "Images/Background/chen12.jpg", "Images/Background/chen13.jpg", "Images/Background/chen14.jpg", "Images/Background/chen15.jpg", "Images/Background/chen16.jpg", "Images/Background/chen17.jpg",
            "Images/Background/chen18.jpg", "Images/Background/chen19.jpg", "Images/Background/chen20.jpg", "Images/Background/chen21.jpg", "Images/Background/chen22.jpg", "Images/Background/chen23.jpg", "Images/Background/chen24.jpg",
            "Images/Background/chen25.jpg", "Images/Background/chen26.jpg", "Images/Background/chen27.jpg", "Images/Background/chen28.jpg", "Images/Background/chen29.jpg", "Images/Background/chen30.jpg"]
SOUNDS = ["Sounds/Background Sounds/chen1.mp3", "Sounds/Background Sounds/chen31.mp3", "Sounds/Background Sounds/chen32.mp3", "Sounds/Background Sounds/chen33.mp3", "Sounds/Background Sounds/chen34.mp3", "Sounds/Background Sounds/chen35.mp3", "Sounds/Background Sounds/chen36.mp3", "Sounds/Background Sounds/chen37.mp3",
          "Sounds/Background Sounds/chen38.mp3", "Sounds/Background Sounds/chen39.mp3", "Sounds/Background Sounds/chen40.mp3", "Sounds/Background Sounds/chen41.mp3", "Sounds/Background Sounds/chen42.mp3"]
VICTORY = ["Sounds/Victory Sounds/chen43.mp3", "Sounds/Victory Sounds/chen44.mp3", "Sounds/Victory Sounds/chen45.mp3", "Sounds/Victory Sounds/chen46.mp3", "Sounds/Victory Sounds/chen47.mp3", "Sounds/Victory Sounds/chen48.mp3", "Sounds/Victory Sounds/chen49.mp3"]
DEFEAT = ["Sounds/Defeat Sounds/chen50.mp3", "Sounds/Defeat Sounds/chen51.mp3", "Sounds/Defeat Sounds/chen52.mp3", "Sounds/Defeat Sounds/chen53.mp3", "Sounds/Defeat Sounds/chen54.mp3"]
DEFEAT_IMAGE = ["Images/Defeat Images/chen55.jpg", "Images/Defeat Images/chen56.jpg", "Images/Defeat Images/chen57.jpg", "Images/Defeat Images/chen58.jpg"]
VICTORY_IMAGE = ["Images/Victory Images/chen59.jpg", "Images/Victory Images/chen60.jpg", "Images/Victory Images/chen61.jpg", "Images/Victory Images/chen62.jpg", "Images/Victory Images/chen63.jpg", "Images/Victory Images/chen64.jpg", "Images/Victory Images/chen65.jpg",
                 "Images/Victory Images/chen66.jpg"]
IP_PATTERN = r'^(\d{1,3}\.){3}\d{1,3}$'
REC = 1024


class MultiPlayer:
    """ online battleships """

    def __init__(self, me, him, connection, check, root):
        """ creates an online game """
        self.me = me
        self.connection = connection
        self.him = him
        self.check = check
        self.root = root
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.title("BattleShips")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        img = Image.open(random.choice(PICTURES))
        img = img.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.background_image = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.root, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.board, self.his_board = self.create_board(250, 150), self.create_board(1170, 150)
        self.his_ships, self.put = [], []
        tk.Button(self.root, text="Back to HOME", command=self.back, font=("Impact", 30)).pack(side="bottom")
        self.label_options = tk.Label(self.root,
                                      text="Choose the ship you want to place and its first coordinate\nfor example, "
                                           "A1 or h5", font=("Impact", 15))
        self.label_options.place(x=250, y=630)
        self.options = ["", "Carrier - 5 squares", "Battleship - 4 squares", "Cruiser - 3 squares", "Submarine - 3 "
                                                                                                    "squares",
                        "Destroyer - 2 squares"]
        self.var = tk.StringVar()
        self.var.set(self.options[0])
        self.option_menu = tk.OptionMenu(self.root, self.var, *self.options)
        self.option_menu.config(width=20)
        self.option_menu.place(x=385, y=695)
        self.entry = tk.Entry(self.root, font=("Impact", 15))
        self.entry.place(x=355, y=730)
        self.label_input = tk.Button(self.root, text="Enter", fg="black", command=self.validation_place_ships,
                                     font=("Impact", 15))
        self.label_input.place(x=440, y=770)
        self.first, self.ships = "", []
        receive_thread = threading.Thread(target=self.opponent_place_ships_and_attack)
        receive_thread.daemon = True
        receive_thread.start()

    def on_closing(self):
        """ closes the window """
        self.me.close()
        self.him.close()
        self.connection.close()
        self.root.destroy()

    def opponent_place_ships_and_attack(self):
        """ opponent places ships """
        while True:
            try:
                data = self.him.recv(REC).decode()
                if not self.his_ships:
                    self.his_ships = json.loads(data)
                else:
                    if data in self.ships:
                        color = "black"
                        self.ships.remove(data)
                    else:
                        color = "cyan"
                    cell = tk.Label(self.board, width=5, height=2, bg=color, relief="raised")
                    cell.grid(row=int(data[1:]) - 1, column=ord(data[0]) - ord("A"))
                    self.entry.config(state="normal")
                    if not self.ships:
                        self.root.after(0, self.end, False)
            except Exception:
                if self.check != 2:
                    self.tech()

    def back(self):
        """ returns to the Home page """
        self.on_closing()
        MainWindow()

    def create_board(self, x, y):
        """ creates board """
        board_size = 10
        board = tk.Frame(self.root, width=board_size * 50, height=board_size * 50, bg="white")
        board.place(x=x, y=y)
        for i in range(board_size):
            for j in range(board_size):
                cell = tk.Label(board, width=5, height=2, bg="white", relief="raised")
                cell.grid(row=i, column=j)
            row_label = tk.Label(board, text=str(i + 1), width=5, height=2, bg="light gray", relief="flat")
            row_label.grid(row=i, column=board_size)
            column_label = tk.Label(board, text=chr(i + 65), width=5, height=2, bg="light gray", relief="flat")
            column_label.grid(row=board_size, column=i)
        return board

    def validation_place_ships(self):
        """ validation of input, and then, starts placing the ships """
        self.first = self.entry.get().upper()
        self.entry.delete(0, tk.END)
        if self.first not in self.ships and self.var.get() != "":
            if len(self.first) == 3 and self.first[0] in LETTERS and self.first[1] == "1" and \
                    self.first[2] == "0" or len(self.first) == 2 and self.first[0] in LETTERS and self.first[1] in \
                    NUMBERS:
                self.first_step(self.first[0], int(self.first[1:]))
        self.var.set(self.options[0])

    def first_step(self, val, val1):
        """ finds all the available options to put the ships """
        options = [""]
        num = val1
        num1 = int(self.var.get().split("-")[1][1])
        letter = val
        check = True
        if num + num1 - 1 in range(1, 11):
            head_col, head_row = ord(letter) - 65, num - 1
            tail_col, tail_row = ord(letter) - 65, num + num1 - 2
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    if chr(col + 65) + str(row + 1) in self.ships:
                        check = False
            if check:
                options.append(letter + str(num + num1 - 1))
        check = True
        if num - num1 + 1 in range(1, 11):
            head_col, head_row = ord(letter) - 65, num - 1
            tail_col, tail_row = ord(letter) - 65, num - num1
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    if chr(col + 65) + str(row + 1) in self.ships:
                        check = False
            if check:
                options.append(letter + str(num - num1 + 1))
        check = True
        if chr(ord(letter) + num1 - 1) in LETTERS:
            head_col, head_row = ord(letter) - 65, num - 1
            tail_col, tail_row = (ord(letter) - 65 + num1 - 1), num - 1
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    if chr(col + 65) + str(row + 1) in self.ships:
                        check = False
            if check:
                options.append(chr(ord(letter) + num1 - 1) + str(num))
        check = True
        if chr(ord(letter) - num1 + 1) in LETTERS:
            head_col, head_row = ord(letter) - 65, num - 1
            tail_col, tail_row = (ord(letter) - num1 + 1) - 65, num - 1
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    if chr(col + 65) + str(row + 1) in self.ships:
                        check = False
            if check:
                options.append(chr(ord(letter) - num1 + 1) + str(num))
        if len(options) == 1:
            self.var.set(self.options[0])
        else:
            self.options.remove(self.var.get())
            self.entry.config(state="disabled")
            self.label_options.config(text="Choose the last coordinate of the ship")
            self.label_options.place(x=310, y=640)
            self.option_menu["menu"].delete(0, "end")
            for option in options:
                self.option_menu["menu"].add_command(label=option, command=lambda value=option: self.var.set(value))
            self.label_input.config(command=self.second_step)

    def second_step(self):
        """ places the ships and starts over """
        if self.var.get() != "":
            head = self.first
            tail = self.var.get()
            head_col, head_row = ord(head[0]) - 65, int(head[1:]) - 1
            tail_col, tail_row = ord(tail[0]) - 65, int(tail[1:]) - 1
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    self.ships.append(chr(col + 65) + str(row + 1))
                    cell = tk.Label(self.board, width=5, height=2, bg="grey", relief="raised")
                    cell.grid(row=row, column=ord(chr(col + 65)) - ord("A"))
            self.entry.config(state="normal")
            self.option_menu["menu"].delete(0, "end")
            for option in self.options:
                self.option_menu["menu"].add_command(label=option, command=lambda value=option: self.var.set(value))
            self.var.set(self.options[0])
            self.label_options.config(text="Choose the ship you want to place and its first coordinate\nfor example, "
                                           "A1 or h5")
            self.label_options.place(x=250, y=630)
            self.label_input.config(command=self.validation_place_ships)
            if len(self.options) == 1:
                try:
                    self.connection.sendall(json.dumps(self.ships).encode())
                    self.handle_game()
                except Exception:
                    self.tech()

    def handle_game(self):
        """ the game is starting """
        self.label_options.destroy()
        self.option_menu.destroy()
        lbl = tk.Label(self.root, text="Enter coordinates to strike\n for example, b1 or B1", font=("Impact", 20))
        lbl.place(x=320, y=650)
        self.label_input.config(command=self.player_attack)
        if self.check == 1:
            self.entry.config(state="normal")
        else:
            self.entry.config(state="disabled")

    def player_attack(self):
        """ attacks the opponent """
        hit = self.entry.get().upper()
        self.entry.delete(0, tk.END)
        if hit not in self.put and self.his_ships:
            if len(hit) == 3 and hit[0] in LETTERS and hit[1] == "1" and hit[2] == "0" or len(hit) == 2 and \
                    hit[0] in LETTERS and hit[1] in NUMBERS:
                self.put.append(hit)
                try:
                    self.connection.sendall(hit.encode())
                except Exception:
                    self.tech()
                if hit in self.his_ships:
                    color = "black"
                    self.his_ships.remove(hit)
                else:
                    color = "cyan"
                cell = tk.Label(self.his_board, width=5, height=2, bg=color, relief="raised")
                cell.grid(row=int(hit[1:]) - 1, column=ord(hit[0]) - ord("A"))
                if not self.his_ships:
                    self.end(True)
                else:
                    self.entry.config(state="disabled")

    def end(self, check):
        """ End game window """
        if check:
            name, pic, sound = "Victory", random.choice(VICTORY_IMAGE), random.choice(VICTORY)
        else:
            name, pic, sound = "Defeat", random.choice(DEFEAT_IMAGE), random.choice(DEFEAT)
        for widget in self.root.winfo_children():
            widget.destroy()
        self.check = 2
        self.root.title(name)
        img = Image.open(pic)
        img = img.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        background_image = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.root, image=background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Button(self.root, text="Back to HOME", command=self.back, font=("Impact", 30)).pack(side="bottom")
        pygame.mixer.init()
        pygame.mixer.music.load(sound)
        pygame.mixer.music.play()
        self.root.mainloop()
        pygame.mixer.music.stop()
        pygame.mixer.quit()

    def tech(self):
        """  technical win """
        self.me.close()
        self.him.close()
        self.connection.close()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.title("Victory")
        img = Image.open(random.choice(VICTORY_IMAGE))
        img = img.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.background_image = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.root, image=self.background_image)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Label(self.root, text="Connection lost\nYou won!", font=("Impact", 35)).pack(pady=50)
        tk.Button(self.root, text="Back to HOME", command=self.back, font=("Impact", 30)).pack(side="bottom")
        pygame.mixer.init()
        pygame.mixer.music.load(random.choice(VICTORY))
        pygame.mixer.music.play()
        self.root.mainloop()
        pygame.mixer.music.stop()
        pygame.mixer.quit()


class SinglePlayer:
    """ offline battleships """

    def __init__(self, root):
        """ creates an offline game """
        self.root = root
        self.root.title("BattleShips")
        img = Image.open(random.choice(PICTURES))
        img = img.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        img = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.root, image=img)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.board, self.computer_board = self.create_board(250, 150), self.create_board(1170, 150)
        self.coordinates_board, self.computer_ships, self.all_ships, self.put = [], [], [], []
        self.computer_options = [5, 4, 3, 3, 2]
        for row in range(10):
            for col in range(10):
                coord = chr(col + 65) + str(row + 1)
                self.coordinates_board.append(coord)
                self.all_ships.append(coord)
        self.computer_place_ships()
        tk.Button(self.root, text="Back to HOME", command=self.back, font=("Impact", 30)).pack(side="bottom")
        self.label_options = tk.Label(self.root,
                                      text="Choose the ship you want to place and its first coordinate\nfor example, "
                                           "A1 or h5", font=("Impact", 15))
        self.label_options.place(x=250, y=630)
        self.options = ["", "Carrier - 5 squares", "Battleship - 4 squares", "Cruiser - 3 squares", "Submarine - 3 "
                                                                                                    "squares",
                        "Destroyer - 2 squares"]
        self.var = tk.StringVar()
        self.var.set(self.options[0])
        self.option_menu = tk.OptionMenu(self.root, self.var, *self.options)
        self.option_menu.config(width=20)
        self.option_menu.place(x=385, y=695)
        self.entry = tk.Entry(self.root, font=("Impact", 15))
        self.entry.place(x=355, y=730)
        self.label_input = tk.Button(self.root, text="Enter", fg="black", command=self.validation_place_ships,
                                     font=("Impact", 15))
        self.label_input.place(x=440, y=770)
        self.first, self.ships, self.check = "", [], 0
        self.root.mainloop()

    def computer_place_ships(self):
        """ randomly places ships """
        while self.computer_options:
            check = True
            num1 = random.choice(self.computer_options)
            head = random.choice(self.coordinates_board)
            options = []
            num = int(head[1:])
            letter = head[0]
            if num + num1 - 1 in range(1, 11):
                head_col, head_row = ord(letter) - 65, num - 1
                tail_col, tail_row = ord(letter) - 65, num + num1 - 2
                for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                    for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                        if chr(col + 65) + str(row + 1) in self.computer_ships:
                            check = False
                if check:
                    options.append(letter + str(num + num1 - 1))
            check = True
            if num - num1 + 1 in range(1, 11):
                head_col, head_row = ord(letter) - 65, num - 1
                tail_col, tail_row = ord(letter) - 65, num - num1
                for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                    for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                        if chr(col + 65) + str(row + 1) in self.computer_ships:
                            check = False
                if check:
                    options.append(letter + str(num - num1 + 1))
            check = True
            if chr(ord(letter) + num1 - 1) in LETTERS:
                head_col, head_row = ord(letter) - 65, num - 1
                tail_col, tail_row = (ord(letter) - 65 + num1 - 1), num - 1
                for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                    for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                        if chr(col + 65) + str(row + 1) in self.computer_ships:
                            check = False
                if check:
                    options.append(chr(ord(letter) + num1 - 1) + str(num))
            check = True
            if chr(ord(letter) - num1 + 1) in LETTERS:
                head_col, head_row = ord(letter) - 65, num - 1
                tail_col, tail_row = (ord(letter) - num1 + 1) - 65, num - 1
                for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                    for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                        if chr(col + 65) + str(row + 1) in self.computer_ships:
                            check = False
                if check:
                    options.append(chr(ord(letter) - num1 + 1) + str(num))
            if options:
                tail = random.choice(options)
                head_col, head_row = ord(head[0]) - 65, int(head[1:]) - 1
                tail_col, tail_row = ord(tail[0]) - 65, int(tail[1:]) - 1
                for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                    for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                        self.computer_ships.append(chr(col + 65) + str(row + 1))
                        self.coordinates_board.remove(chr(col + 65) + str(row + 1))
                self.computer_options.remove(num1)
        print(self.computer_ships)
        print(len(self.computer_ships))

    def back(self):
        """ returns to the Home page """
        self.root.destroy()
        MainWindow()

    def create_board(self, x, y):
        """ creates board """
        board_size = 10
        board = tk.Frame(self.root, width=board_size * 50, height=board_size * 50, bg="white")
        board.place(x=x, y=y)
        for i in range(board_size):
            for j in range(board_size):
                cell = tk.Label(board, width=5, height=2, bg="white", relief="raised")
                cell.grid(row=i, column=j)
            row_label = tk.Label(board, text=str(i + 1), width=5, height=2, bg="light gray", relief="flat")
            row_label.grid(row=i, column=board_size)
            column_label = tk.Label(board, text=chr(i + 65), width=5, height=2, bg="light gray", relief="flat")
            column_label.grid(row=board_size, column=i)
        return board

    def validation_place_ships(self):
        """ validation of input, and then, starts placing the ships """
        self.first = self.entry.get().upper()
        self.entry.delete(0, tk.END)
        if self.first not in self.ships and self.var.get() != "":
            if len(self.first) == 3 and self.first[0] in LETTERS and self.first[1] == "1" and \
                    self.first[2] == "0" or len(self.first) == 2 and self.first[0] in LETTERS and self.first[1] in \
                    NUMBERS:
                self.first_step(self.first[0], int(self.first[1:]))
        self.var.set(self.options[0])

    def first_step(self, val, val1):
        """ finds all the available options to put the ships """
        options = [""]
        num = val1
        num1 = int(self.var.get().split("-")[1][1])
        letter = val
        check = True
        if num + num1 - 1 in range(1, 11):
            head_col, head_row = ord(letter) - 65, num - 1
            tail_col, tail_row = ord(letter) - 65, num + num1 - 2
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    if chr(col + 65) + str(row + 1) in self.ships:
                        check = False
            if check:
                options.append(letter + str(num + num1 - 1))
        check = True
        if num - num1 + 1 in range(1, 11):
            head_col, head_row = ord(letter) - 65, num - 1
            tail_col, tail_row = ord(letter) - 65, num - num1
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    if chr(col + 65) + str(row + 1) in self.ships:
                        check = False
            if check:
                options.append(letter + str(num - num1 + 1))
        check = True
        if chr(ord(letter) + num1 - 1) in LETTERS:
            head_col, head_row = ord(letter) - 65, num - 1
            tail_col, tail_row = (ord(letter) - 65 + num1 - 1), num - 1
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    if chr(col + 65) + str(row + 1) in self.ships:
                        check = False
            if check:
                options.append(chr(ord(letter) + num1 - 1) + str(num))
        check = True
        if chr(ord(letter) - num1 + 1) in LETTERS:
            head_col, head_row = ord(letter) - 65, num - 1
            tail_col, tail_row = (ord(letter) - num1 + 1) - 65, num - 1
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    if chr(col + 65) + str(row + 1) in self.ships:
                        check = False
            if check:
                options.append(chr(ord(letter) - num1 + 1) + str(num))
        if len(options) == 1:
            self.var.set(self.options[0])
        else:
            self.options.remove(self.var.get())
            self.entry.config(state="disabled")
            self.label_options.config(text="Choose the last coordinate of the ship")
            self.label_options.place(x=310, y=640)
            self.option_menu["menu"].delete(0, "end")
            for option in options:
                self.option_menu["menu"].add_command(label=option, command=lambda value=option: self.var.set(value))
            self.label_input.config(command=self.second_step)

    def second_step(self):
        """ places the ships and starts over """
        if self.var.get() != "":
            head = self.first
            tail = self.var.get()
            head_col, head_row = ord(head[0]) - 65, int(head[1:]) - 1
            tail_col, tail_row = ord(tail[0]) - 65, int(tail[1:]) - 1
            for row in range(min(head_row, tail_row), max(head_row, tail_row) + 1):
                for col in range(min(head_col, tail_col), max(head_col, tail_col) + 1):
                    self.ships.append(chr(col + 65) + str(row + 1))
                    cell = tk.Label(self.board, width=5, height=2, bg="grey", relief="raised")
                    cell.grid(row=row, column=ord(chr(col + 65)) - ord("A"))
            self.entry.config(state="normal")
            self.option_menu["menu"].delete(0, "end")
            for option in self.options:
                self.option_menu["menu"].add_command(label=option, command=lambda value=option: self.var.set(value))
            self.var.set(self.options[0])
            self.label_options.config(text="Choose the ship you want to place and its first coordinate\nfor example, "
                                           "A1 or h5")
            self.label_options.place(x=250, y=630)
            self.label_input.config(command=self.validation_place_ships)
            if len(self.options) == 1:
                self.handle_game()

    def handle_game(self):
        """ the game is starting """
        self.entry.config(state="normal")
        self.label_options.destroy()
        self.option_menu.destroy()
        self.label_input.config(command=self.player_attack)
        tk.Label(self.root, text="Enter coordinates to strike\nfor example, b1 or B1", font=("Impact", 20)).place(x=320,
                                                                                                                  y=650)
        if self.check == 0 and random.randint(0, 1) == 0:
            self.check = 1
            self.computer_attack()

    def player_attack(self):
        """ attacks the opponent """
        hit = self.entry.get().upper()
        self.entry.delete(0, tk.END)
        if hit not in self.put:
            if len(hit) == 3 and hit[0] in LETTERS and hit[1] == "1" and hit[2] == "0" or len(hit) == 2 and \
                    hit[0] in LETTERS and hit[1] in NUMBERS:
                self.put.append(hit)
                if hit in self.computer_ships:
                    color = "black"
                    self.computer_ships.remove(hit)
                else:
                    color = "cyan"
                cell = tk.Label(self.computer_board, width=5, height=2, bg=color, relief="raised")
                cell.grid(row=int(hit[1:]) - 1, column=ord(hit[0]) - ord("A"))
                if not self.computer_ships:
                    self.end(True)
                else:
                    self.computer_attack()

    def computer_attack(self):
        """ attacks the player """
        self.entry.config(state="disabled")
        hit = random.choice(self.all_ships)
        self.all_ships.remove(hit)
        if hit in self.ships:
            color = "black"
            self.ships.remove(hit)
        else:
            color = "cyan"
        cell = tk.Label(self.board, width=5, height=2, bg=color, relief="raised")
        cell.grid(row=int(hit[1:]) - 1, column=ord(hit[0]) - ord("A"))
        self.entry.config(state="normal")
        if not self.ships:
            self.end(False)

    def end(self, check):
        if check:
            name, img, sound = "Victory", VICTORY_IMAGE, VICTORY
        else:
            name, img, sound = "Defeat", DEFEAT_IMAGE, DEFEAT
        self.root.destroy()
        self.root = tk.Tk()
        self.root.geometry("{0}x{1}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.root.title(name)
        img = Image.open(random.choice(img))
        img = img.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        img = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.root, image=img)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        pygame.mixer.init()
        pygame.mixer.music.load(random.choice(sound))
        pygame.mixer.music.play()
        tk.Button(self.root, text="Back to HOME", command=self.back, font=("Impact", 30)).pack(side="bottom")
        self.root.mainloop()
        pygame.mixer.music.stop()
        pygame.mixer.quit()


class MainWindow:
    """ the HOME window """

    def __init__(self):
        """ creates the HOME page """
        self.root = tk.Tk()
        self.root.title("HOME")
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}")
        img = Image.open(random.choice(PICTURES))
        img = img.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        img = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.root, image=img)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        pygame.mixer.init()
        pygame.mixer.music.load(random.choice(SOUNDS))
        pygame.mixer.music.play(loops=-1)
        welcome_label = tk.Label(self.root, text="Welcome to Battleships!\nChoose the mode you would like to play in:",
                                 font=("Impact", 35))
        welcome_label.pack(pady=50)
        singleplayer_button = tk.Button(self.root, text="Singleplayer", font=("Impact", 30),
                                        command=self.start_singleplayer)
        singleplayer_button.pack(pady=10)

        multiplayer_button = tk.Button(self.root, text="Multiplayer", font=("Impact", 30),
                                       command=self.start_multiplayer)
        multiplayer_button.pack(pady=10)
        help_button = tk.Button(self.root, text="Help", font=("Impact", 30), command=self.help_window)
        help_button.pack(side="bottom")
        singleplayer_button.place(relx=0.6, rely=0.5, anchor="center")
        multiplayer_button.place(relx=0.4, rely=0.5, anchor="center")
        self.root.mainloop()

    def start_singleplayer(self):
        """ offline game """
        for widget in self.root.winfo_children():
            widget.destroy()
        SinglePlayer(self.root)

    def start_multiplayer(self):
        """ online game """
        for widget in self.root.winfo_children():
            widget.destroy()
        Loading(self.root)

    def help_window(self):
        """ creates a help window """
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.title("Help")
        img = Image.open("Images/Help/chen2.jpg")
        img = img.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        img = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.root, image=img)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Button(self.root, text="Back to HOME", command=self.back, font=("Impact", 25)).pack(side="bottom")
        tk.Label(self.root, text="Singleplayer mode - against the computer, Multiplayer mode - against another person\n"
                                 "Instructions: place each ship in any horizontal or vertical position, but not "
                                 "diagonally.\nDo not place a ship so that any part of it over - laps\n"
                                 "letters, numbers, the edge of the grid or another ship.\n"
                                 "You and your opponent will alternate turns,\ncalling out one "
                                 "shot per turn to try and hit each other's ships",
                 font=("Impact", 25), fg="white", bg="black").pack(pady=50)
        self.root.mainloop()

    def back(self):
        """ returns to the HOME page """
        self.root.destroy()
        MainWindow()


class Loading:
    """ The loading screen """

    def __init__(self, root):
        """ creates the window """
        self.root = root
        self.root.title("Loading Screen")
        img = Image.open("Images/Loading Screen/chen67.jpg")
        img = img.resize((self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        img = ImageTk.PhotoImage(img)
        background_label = tk.Label(self.root, image=img)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
        tk.Label(self.root, text="Enter your port, your friend's port, and his IP, for example: 700-600-127.0.0.1",
                 font=("Impact", 30)).pack(pady=50)
        self.lbl = tk.Label(self.root, text="", font=("Impact", 35))
        self.lbl.pack(pady=50)
        self.lbl.pack_forget()
        self.entry = tk.Entry(self.root, font=("Impact", 30))
        self.entry.pack(pady=10)
        tk.Button(self.root, text="Enter", command=self.submit, font=("Impact", 30)).pack(pady=10)
        tk.Button(self.root, text="Back to HOME", command=self.back, font=("Impact", 30)).pack(side="bottom")
        self.root.mainloop()

    def back(self):
        """ returns to the HOME page """
        self.root.destroy()
        MainWindow()

    def submit(self):
        """ checks the given input """
        value = self.entry.get()
        self.entry.delete(0, tk.END)
        lst = value.split("-")
        if len(lst) == 3:
            if lst[2].lower() == "localhost" or lst[2] == "127.0.0.1":
                if int(lst[0]) in range(0, 65536) and int(lst[1]) in range(0, 65536) and lst[0] != lst[1]:
                    my_port = int(lst[0])
                    his_port = int(lst[1])
                    his_ip = lst[2]
                    my_ip = "localhost"
                    self.lbl.pack()
                    self.lbl.config(text="connecting to: {} / {}".format(his_ip, his_port))
                    self.next(my_port, his_port, his_ip, my_ip)
            elif re.match(IP_PATTERN, lst[2]):
                ip_components = lst[2].split('.')
                if all(0 <= int(c) <= 255 for c in ip_components) and int(lst[0]) in range(0, 65536) and int(lst[1]) in\
                        range(0, 65536):
                    my_port = int(lst[0])
                    his_port = int(lst[1])
                    his_ip = lst[2]
                    my_ip = socket.gethostbyname(socket.gethostname())
                    self.lbl.pack()
                    self.lbl.config(text="connecting to: {} / {}".format(his_ip, his_port))
                    self.next(my_port, his_port, his_ip, my_ip)

    def next(self, my_port, his_port, his_ip, my_ip):
        """ starts the connection """
        try:
            me = socket.socket()
            me.bind((my_ip, my_port))
        except Exception:
            pass
        receive_thread = threading.Thread(target=self.second, args=(his_ip, his_port, me))
        receive_thread.daemon = True
        receive_thread.start()

    def second(self, his_ip, his_port, me):
        """ final stage of connection """
        me.listen(1)
        while True:
            try:
                him = socket.socket()
                him.connect((his_ip, his_port))
                break
            except ConnectionRefusedError:
                time.sleep(0)
        connection, address = me.accept()
        num = random.randint(0, 999999)
        connection.sendall(str(num).encode())
        num1 = int(him.recv(REC).decode())
        if num > num1:
            check = 1
        else:
            check = 0
        MultiPlayer(me, him, connection, check, self.root)


if __name__ == "__main__":
    MainWindow()
