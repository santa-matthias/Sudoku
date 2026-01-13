import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys
import random
import time

WIDTH, HEIGHT = 540, 650
ROWS, COLS = 9, 9
CELL_SIZE = 540 // 9
BG_COLOR = (255, 255, 255)
LINE_COLOR = (0, 0, 0)
SELECTED_COLOR = (173, 216, 230)
TEXT_COLOR = (0, 0, 139)
ORIGINAL_COLOR = (0, 0, 0)
WIN_COLOR = (0, 128, 0)

class SudokuGenerator:
    def __init__(self, remove_count):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.remove_count = remove_count
    
    def get_board(self):
        """generates full solution and removes digits for puzzle"""
        self.fill_diagonal()
        self.fill_remaining(0, 3)
        self.remove_digits()
        return self.board

    def fill_diagonal(self):
        """fills the three diagonal boxes first"""
        for i in range(0, 9, 3):
            self.fill_box(i, i)

    def fill_box(self, row, col):
        """fills a 3x3 with random unique numbers (1-9)"""
        num = 0
        nums = set()
        for i in range(3):
            for j in range(3):
                while True:
                    num = random.randint(1,9)
                    if num not in nums:
                        break
                self.board[row + i][col + j] = num
                nums.add(num)

    def check_safe(self, row, col, num):
        """checks if num is valid (row/col/box)"""
        return (self.unused_in_row(row, num) and
                self.unused_in_col(col, num) and
                self.unused_in_box(row - row % 3, col - col % 3, num))

    def unused_in_row(self, i, num):
        for j in range(9):
            if self.board[i][j] == num:
                return False
        return True

    def unused_in_col(self, j, num):
        for i in range(9):
            if self.board[i][j] == num:
                return False
        return True
    
    def unused_in_box(self, row_start, col_start, num):
        for i in range(3):
            for j in range(3):
                if self.board[row_start + i][col_start + j] == num:
                    return False
        return True

    def fill_remaining(self, i, j):
        """uses recursive backtracking to solve the rest of the board"""
        if j >= 9 and i < 8:
            i += 1
            j = 0
        if i >= 9 and j >= 9:
            return True
        if i < 3:
            if j < 3:
                j = 3
        elif i < 6:
            if j == 3:
                j += 3
        elif i < 9:
            if j == 6:
                i += 1
                j = 0
                if i >= 9:
                    return True

        nums = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        random.shuffle(nums)
        for num in nums:
            if self.check_safe(i, j, num):
                self.board[i][j] = num
                if self.fill_remaining(i, j + 1):
                    return True
                self.board[i][j] = 0
        return False

    def remove_digits(self):
        """randomly removes numbers based on difficulty"""
        count = self.remove_count
        while count > 0:
            cellId = random.randint(0, 80)
            i = cellId // 9
            j = cellId % 9
            if self.board[i][j] != 0:
                count -= 1
                self.board[i][j] = 0

def check_win(board):
    """checks if board is correctly solved"""
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                return False
            
    for row in range(9):
        if len(set(board[row])) != 9:
            return False
    
    for col in range(9):
        col_vals = [board[row][col] for row in range(9)]
        if len(set(col_vals)) != 9:
            return False
    
    for row in range(0, 9, 3):
        for col in range(0, 9, 3):
            box_vals = []
            for i in range(3):
                for j in range(3):
                    box_vals.append(board[row + i][col + j])
            if len(set(box_vals)) != 9:
                return False
    return True

def format_time(secs):
    """converts seconds to MM:SS format"""
    minutes = secs // 60
    seconds = secs % 60
    return f"Zeit: {minutes:02}:{seconds:02}"

def draw_grid(win, board, orginal_board, selected):
    """draws grid lines, placed numbers and highlights selection"""
    win.fill(BG_COLOR)

    if selected:
        x, y = selected
        pygame.draw.rect(win, SELECTED_COLOR, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        
    for i in range(ROWS + 1):
        thickness = 4 if i % 3 == 0 else 1
        pygame.draw.line(win, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), thickness)
        pygame.draw.line(win, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, 540), thickness)
        
    font = pygame.font.SysFont("arial", 50)
    for i in range(ROWS):
        for j in range(COLS):
            val = board[i][j]
            if val != 0:
                color = ORIGINAL_COLOR if orginal_board[i][j] != 0 else TEXT_COLOR
                text = font.render(str(val), 1, color)
                win.blit(text, (j * CELL_SIZE + (CELL_SIZE / 2 - text.get_width() / 2),
                                i * CELL_SIZE + (CELL_SIZE / 2 - text.get_height() / 2)))

def draw_bottom_text(win, play_time, won):
    """renders instructions, timer and victory message"""
    font = pygame.font.SysFont("arial", 20)
    text = font.render("Drücke: E (Einfach), M (Mittel), S (Schwer)", 1, (0, 0, 0))
    win.blit(text, (20, 560))

    time_text = font.render(format_time(play_time), 1, (0, 0, 0))
    win.blit(time_text, (WIDTH - 120, 560))
    text_undo = font.render("Z (Zurück)", 1, (0, 0, 0))
    win.blit(text_undo, (92, 580))

    if won:
        large_font = pygame.font.SysFont("arial", 60)
        won_text = large_font.render("GESCHAFFT!", 1, WIN_COLOR)
        win.blit(won_text, (WIDTH / 2 - won_text.get_width() / 2, 590))

def generate_new_board(difficulty):
    """handles difficulty and inits board"""
    if difficulty == "EINFACH": remove = 30
    elif difficulty == "MITTEL": remove = 38
    else: remove = 45

    generator = SudokuGenerator(remove)
    board = generator.get_board()

    original = [row[:] for row in board]
    return board, original
    
def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SUDOKU")

    board, original_board = generate_new_board("MITTEL")

    selected = None
    running = True
    won = False
    history = []

    start_time = time.time()
    play_time = 0

    while running:
        if not won:
            play_time = round(time.time() - start_time)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if pos[1] < 540:
                    selected = (pos[0] // CELL_SIZE, pos[1] // CELL_SIZE)
                else:
                    selected = None
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    board, original_board = generate_new_board("EINFACH")
                    selected = None
                    won = False
                    start_time = time.time()
                    history = []
                if event.key == pygame.K_m:
                    board, original_board = generate_new_board("MITTEL")
                    selected = None
                    won = False
                    start_time = time.time()
                    history = []
                if event.key == pygame.K_s:
                    board, original_board = generate_new_board("SCHWER")
                    selected = None
                    won = False
                    start_time = time.time()
                    history = []
                if event.key == pygame.K_z:
                    if history:
                        last_row, last_col, last_val = history.pop()
                        board[last_row][last_col] = last_val
                
                if selected:
                    col, row = selected
                    if event.key == pygame.K_LEFT and col > 0:
                        selected = (col - 1, row)
                    if event.key == pygame.K_RIGHT and col < 8:
                        selected = (col + 1, row)
                    if event.key == pygame.K_UP and row > 0:
                        selected = (col, row - 1)
                    if event.key == pygame.K_DOWN and row < 8:
                        selected = (col, row + 1)
                    
                if selected and not won:
                    col, row = selected
                    if original_board[row][col] == 0:
                        input_num = None
                        if event.key == pygame.K_1 or event.key == pygame.K_KP_1: input_num = 1
                        if event.key == pygame.K_2 or event.key == pygame.K_KP_2: input_num = 2
                        if event.key == pygame.K_3 or event.key == pygame.K_KP_3: input_num = 3
                        if event.key == pygame.K_4 or event.key == pygame.K_KP_4: input_num = 4
                        if event.key == pygame.K_5 or event.key == pygame.K_KP_5: input_num = 5
                        if event.key == pygame.K_6 or event.key == pygame.K_KP_6: input_num = 6
                        if event.key == pygame.K_7 or event.key == pygame.K_KP_7: input_num = 7
                        if event.key == pygame.K_8 or event.key == pygame.K_KP_8: input_num = 8
                        if event.key == pygame.K_9 or event.key == pygame.K_KP_9: input_num = 9
                        if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE: input_num = 0

                        if input_num is not None:
                            if board[row][col] != input_num:
                                history.append((row, col, board[row][col]))
                                board[row][col] = input_num
                        
                        if check_win(board):
                            won = True
            
        draw_grid(win, board, original_board, selected)
        draw_bottom_text(win, play_time, won)
        pygame.display.update()
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()