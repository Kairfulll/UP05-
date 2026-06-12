import tkinter as tk
from tkinter import messagebox
import random
import time
import os

class Minesweeper:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Сапёр")
        self.root.resizable(False, False)

        # Настройки уровней сложности
        self.levels = {
            "Новичок": (9, 9, 10),
            "Любитель": (16, 16, 40),
            "Эксперт": (16, 30, 99)
        }

        self.current_level = "Новичок"
        self.rows, self.cols, self.mines_count = self.levels[self.current_level]

        self.board = []          # логическое поле: -1 = мина, 0-8 = цифры
        self.revealed = []       # открыта ли ячейка
        self.flags = []          # стоит ли флажок
        self.first_click = True
        self.game_over = False
        self.start_time = None
        self.timer_running = False
        self.mines_left = self.mines_count

        self.buttons = []
        self.game_frame = None
        self.menu_frame = None

        self.create_main_menu()

    def create_main_menu(self):
        if self.menu_frame:
            self.menu_frame.destroy()

        self.menu_frame = tk.Frame(self.root, padx=50, pady=50)
        self.menu_frame.pack()

        # Заголовок
        title = tk.Label(self.menu_frame, text="САПЁР", font=("Arial", 48, "bold"))
        title.pack(pady=30)

        # Кнопки уровней
        for level_name in self.levels.keys():
            size = f"({self.levels[level_name][0]}x{self.levels[level_name][1]})"
            btn = tk.Button(
                self.menu_frame,
                text=f"{level_name} {size}",
                font=("Arial", 16),
                width=30,
                height=2,
                relief="raised",
                bd=4,
                command=lambda l=level_name: self.start_game(l)
            )
            btn.pack(pady=12)
        # Кнопка рекордов
        records_btn = tk.Button(
            self.menu_frame,
            text="📊 Рекорды",
            font=("Arial", 14),
            width=20,
            command=self.show_records
        )
        records_btn.pack(pady=20)

    def start_game(self, level):
        self.current_level = level
        self.menu_frame.destroy()  # скрываем главное меню

        # Создаём игровые виджеты
        self.create_game_widgets()
        self.new_game()

    def create_game_widgets(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.mines_label = tk.Label(top_frame, text=f"Мины: {self.mines_count:03d}", 
                                   font=("Arial", 16, "bold"), width=10, relief="sunken", bd=2)
        self.mines_label.pack(side=tk.LEFT, padx=20)

        self.new_game_btn = tk.Button(top_frame, text="😊", font=("Arial", 24), width=3, height=1, command=self.return_to_menu)
        self.new_game_btn.pack(side=tk.LEFT)

        self.timer_label = tk.Label(top_frame, text="00:00", 
                                   font=("Arial", 16, "bold"), width=10, relief="sunken", bd=2)
        self.timer_label.pack(side=tk.RIGHT, padx=20)

        # Игровое поле
        self.game_frame = tk.Frame(self.root, bg="gray")
        self.game_frame.pack(pady=10, padx=10)

    def return_to_menu(self):
        # Удаляем игровое поле
        if hasattr(self, 'game_frame') and self.game_frame:
            self.game_frame.destroy()
            self.game_frame = None

        # Удаляем ВСЮ верхнюю панель и все остальные фреймы кроме меню
        for widget in list(self.root.winfo_children()):
            # Удаляем все фреймы кроме будущего главного меню
            if isinstance(widget, tk.Frame):
                widget.destroy()

        # Сбрасываем ссылки
        self.mines_label = None
        self.timer_label = None
        self.new_game_btn = None

        self.create_main_menu()

    def new_game(self):
        self.rows, self.cols, self.mines_count = self.levels[self.current_level]
        self.mines_left = self.mines_count
        self.first_click = True
        self.game_over = False
        self.start_time = None
        self.timer_running = False
        self.update_mines_label()

        for widget in self.game_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flags = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        for i in range(self.rows):
            row_buttons = []
            for j in range(self.cols):
                btn = tk.Button(
                    self.game_frame,
                    width=2,
                    height=1,
                    font=("Arial", 10, "bold"),
                    bg="#c0c0c0",
                    relief="raised",
                    bd=3
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                btn.bind("<Button-1>", lambda e, x=i, y=j: self.left_click(x, y))
                btn.bind("<Button-3>", lambda e, x=i, y=j: self.right_click(x, y))
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.new_game_btn.config(text="😊")
        self.timer_label.config(text="00:00")
        self.create_widgets()
        self.new_game()

    def create_widgets(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

              # Счётчик мин
        self.mines_label = tk.Label(top_frame, text=f"Мины: {self.mines_count:03d}", 
                                   font=("Arial", 16, "bold"), width=10, relief="sunken", bd=2)
        self.mines_label.pack(side=tk.LEFT, padx=20)

        # Кнопка новой игры
        self.new_game_btn = tk.Button(top_frame, text="😊", font=("Arial", 24), width=3, height=1, command=self.new_game)
        self.new_game_btn.pack(side=tk.LEFT)

        # Таймер
        self.timer_label = tk.Label(top_frame, text="00:00", 
                                   font=("Arial", 16, "bold"), width=10, relief="sunken", bd=2)
        self.timer_label.pack(side=tk.RIGHT, padx=20)
               # Игровое поле
        self.game_frame = tk.Frame(self.root, bg="gray")
        self.game_frame.pack(pady=10, padx=10)
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Игра", menu=game_menu)
        game_menu.add_command(label="Новая игра", command=self.new_game)
        game_menu.add_command(label="Рекорды", command=self.show_records)
        game_menu.add_separator()
        game_menu.add_command(label="Выход", command=self.root.quit)

        level_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Сложность", menu=level_menu)
        for level in self.levels.keys():
            level_menu.add_command(label=level, command=lambda l=level: self.change_level(l))
    def new_game(self):
        self.rows, self.cols, self.mines_count = self.levels[self.current_level]
        self.mines_left = self.mines_count
        self.first_click = True
        self.game_over = False
        self.start_time = None
        self.timer_running = False
        self.update_mines_label()

        # Очистка старого поля
        for widget in self.game_frame.winfo_children():
            widget.destroy()

        self.buttons = []
        self.board = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.revealed = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        self.flags = [[False for _ in range(self.cols)] for _ in range(self.rows)]

        # Создание кнопок
        for i in range(self.rows):
            row_buttons = []
            for j in range(self.cols):
                btn = tk.Button(
                    self.game_frame,
                    width=2,
                    height=1,
                    font=("Arial", 10, "bold"),
                    bg="#c0c0c0",
                    relief="raised",
                    bd=3
                )
                btn.grid(row=i, column=j, padx=1, pady=1)
                btn.bind("<Button-1>", lambda e, x=i, y=j: self.left_click(x, y))
                btn.bind("<Button-3>", lambda e, x=i, y=j: self.right_click(x, y))
                row_buttons.append(btn)
            self.buttons.append(row_buttons)

        self.new_game_btn.config(text="😊")
        self.timer_label.config(text="00:00")

    def change_level(self, level):
        if level != self.current_level:
            self.current_level = level
            self.new_game()

    def place_mines(self, first_x, first_y):
        positions = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        # Убираем первую нажатую ячейку и её соседей, чтобы первый клик всегда был безопасным
        safe_positions = [(first_x, first_y)]
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = first_x + dx, first_y + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    safe_positions.append((nx, ny))
        
        # Удаляем безопасные позиции из списка возможных позиций для мин
        for pos in safe_positions:
            if pos in positions:
                positions.remove(pos)
        
        # Проверяем, достаточно ли позиций для размещения мин
        if len(positions) < self.mines_count:
            # Если недостаточно, уменьшаем количество мин
            self.mines_count = len(positions)
        
        mine_positions = random.sample(positions, self.mines_count)
        
        for x, y in mine_positions:
            self.board[x][y] = -1
        
        # Подсчёт чисел
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == -1:
                    continue
                count = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = i + dx, j + dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols and self.board[nx][ny] == -1:
                            count += 1
                self.board[i][j] = count

    def get_neighbors(self, x, y):
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    neighbors.append((nx, ny))
        return neighbors

    def flood_fill(self, x, y):
        if self.revealed[x][y] or self.flags[x][y]:
            return

        self.revealed[x][y] = True
        btn = self.buttons[x][y]
        btn.config(relief="sunken", bg="#e0e0e0", state="disabled")

        if self.board[x][y] > 0:
            colors = ["", "blue", "green", "red", "darkblue", "darkred", "darkgreen", "black", "gray"]
            btn.config(text=str(self.board[x][y]), fg=colors[self.board[x][y]])
            return

        # Если 0 — открываем соседей
        for nx, ny in self.get_neighbors(x, y):
            self.flood_fill(nx, ny)

    def left_click(self, x, y):
        if self.game_over or self.flags[x][y] or self.revealed[x][y]:
            return

        if self.first_click:
            self.first_click = False
            self.place_mines(x, y)
            self.start_time = time.time()
            self.timer_running = True
            self.update_timer()

        if self.board[x][y] == -1:
            self.game_over = True
            self.reveal_all_mines()
            self.new_game_btn.config(text="😵")
            self.show_game_over_window("Поражение", "Вы подорвались на мине!", "😵")
            return

        self.flood_fill(x, y)

        if self.check_win():
            self.game_over = True
            self.timer_running = False
            self.new_game_btn.config(text="😎")
            self.show_game_over_window("Победа!", f"Вы выиграли за {self.get_time()} секунд!", "😎")
            self.save_record()

    def right_click(self, x, y):
        if self.game_over or self.revealed[x][y]:
            return

        btn = self.buttons[x][y]

        if self.flags[x][y]:
            self.flags[x][y] = False
            btn.config(text="", bg="#c0c0c0")
            self.mines_left += 1
        else:
            self.flags[x][y] = True
            btn.config(text="🚩", bg="#ff9999")
            self.mines_left -= 1

        self.update_mines_label()

    def reveal_all_mines(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] == -1:
                    btn = self.buttons[i][j]
                    if not self.flags[i][j]:
                        btn.config(text="💣", bg="red", relief="sunken")
                    else:
                        btn.config(bg="#ff9999")

    def check_win(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.board[i][j] != -1 and not self.revealed[i][j]:
                    return False
        return True

    def update_mines_label(self):
        self.mines_label.config(text=f"Мины: {max(0, self.mines_left):03d}")

    def update_timer(self):
        if not self.timer_running or self.game_over:
            return
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        self.root.after(1000, self.update_timer)

    def get_time(self):
        if self.start_time:
            return int(time.time() - self.start_time)
        return 0

    def save_record(self):
        try:
            with open("records.txt", "a", encoding="utf-8") as f:
                f.write(f"{self.get_time()}:{self.current_level}\n")
        except:
            pass

    def show_records(self):
        try:
            with open("records.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            lines = []

        records = {}
        for line in lines:
            if line.strip():
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    t = int(parts[0])
                    level = parts[1]
                    if level not in records or t < records[level]:
                        records[level] = t

        text = "Лучшие результаты:\n\n"
        for lvl in ["Новичок", "Любитель", "Эксперт"]:
            text += f"{lvl}: {records.get(lvl, '—')} сек\n"

        win = tk.Toplevel(self.root)
        win.title("Рекорды")
        tk.Label(win, text=text, font=("Arial", 12), justify=tk.LEFT).pack(pady=20, padx=20)
        tk.Button(win, text="Закрыть", command=win.destroy).pack(pady=10)

    def show_game_over_window(self, title, message, emoji):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.resizable(False, False)
        win.grab_set()  # модальное окно

        tk.Label(win, text=emoji, font=("Arial", 60)).pack(pady=10)
        tk.Label(win, text=message, font=("Arial", 14)).pack(pady=5)
        
        if "Победа" in title:
            tk.Label(win, text=f"Время: {self.get_time()} сек", font=("Arial", 12, "bold")).pack(pady=5)

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=15)

        # Кнопка "Новая игра"
        tk.Button(btn_frame, text="Новая игра", 
                  font=("Arial", 12),
                  width=12,
                  command=lambda: [win.destroy(), self.new_game()]).pack(side=tk.LEFT, padx=8)
        
        # Кнопка "Главное меню" вместо "Закрыть"
        tk.Button(btn_frame, text="Главное меню", 
                  font=("Arial", 12),
                  width=12,
                  command=lambda: [win.destroy(), self.return_to_menu()]).pack(side=tk.LEFT, padx=8)
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    game = Minesweeper()
    game.run()