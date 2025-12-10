#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suite de jeux Tkinter :
- Pierre-Feuille-Ciseaux (best of 3)
- Tic-Tac-Toe
- Dames (Checkers)
- Sudoku
- Fullscreen, Dark/Light mode
"""

import tkinter as tk
from tkinter import messagebox
import random

#####################
# Themes
#####################
DARK = {'bg': '#222', 'fg': '#f5f5f5', 'button_bg': '#333', 'button_fg': '#f5f5f5'}
LIGHT = {'bg': '#f5f5f5', 'fg': '#222', 'button_bg': '#ddd', 'button_fg': '#222'}


#####################
# Helper Styled Button
#####################
def styled_button(parent, text, command, width=20, height=2, font=None):
    b = tk.Button(parent, text=text, command=command, width=width, height=height, font=font,
                  relief='flat', bd=0, bg='#333', fg='#f5f5f5', activebackground='#555', activeforeground='#fff')
    b.bind("<Enter>", lambda e: b.config(bg='#555'))
    b.bind("<Leave>", lambda e: b.config(bg='#333'))
    return b


#####################
# Themed Frame
#####################
class ThemedFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.theme['bg'])
        self.controller = controller

    def update_theme(self, theme):
        self.config(bg=theme['bg'])
        for w in self.winfo_children():
            self._update_widget(w, theme)

    def _update_widget(self, widget, theme):
        # Stop trying to re-color the TicTacToe board buttons, they use custom colors
        if isinstance(self, TicTacToeFrame) and widget in [self.board_container, self.game_container]:
            widget.config(bg=theme['bg'])
            for c in widget.winfo_children():
                self._update_widget(c, theme)
            return

        if isinstance(widget, tk.Label):
            widget.config(bg=theme['bg'], fg=theme['fg'])
        elif isinstance(widget, tk.Button):
            # Only update style buttons, ignore the TicTacToe board buttons' background
            if 'relief' in widget.config() and widget['relief'] == 'flat':
                widget.config(bg=theme['button_bg'], fg=theme['button_fg'])
            else:
                # Standard Buttons (like Checkers squares) need background updated
                widget.config(bg=theme['button_bg'])

        elif isinstance(widget, tk.Entry):
            widget.config(bg=theme['bg'], fg=theme['fg'])
        elif isinstance(widget, tk.Frame):
            widget.config(bg=theme['bg'])
            for c in widget.winfo_children():
                self._update_widget(c, theme)


#####################
# Main App
#####################
class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Suite de jeux")
        self.geometry("900x640")
        self.fullscreen = False
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.end_fullscreen)

        self.is_dark = True
        self.theme = DARK if self.is_dark else LIGHT
        self.bind_all("<Control-d>", lambda e: self.toggle_theme())

        container = tk.Frame(self, bg=self.theme['bg'])
        container.pack(fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        # All frames must be defined as classes inheriting from ThemedFrame
        for F in (MainMenu, RPSFrame, TicTacToeFrame, CheckersFrame, SudokuFrame):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('MainMenu')

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()
        # Ensure theme is applied every time a frame is shown
        frame.update_theme(self.theme)

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.attributes("-fullscreen", self.fullscreen)

    def end_fullscreen(self, event=None):
        self.fullscreen = False
        self.attributes("-fullscreen", False)

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.theme = DARK if self.is_dark else LIGHT
        for f in self.frames.values():
            f.update_theme(self.theme)


#####################
# Main Menu
#####################
class MainMenu(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Label(self, text="SUITE DE JEUX", font=("Helvetica", 28, 'bold')).pack(pady=16)

        btns = [("Pierre-Feuille-Ciseaux", "RPSFrame"),
                ("Tic-Tac-Toe", "TicTacToeFrame"),
                ("Dames", "CheckersFrame"),
                ("Sudoku", "SudokuFrame")]

        for t, fname in btns:
            b = styled_button(self, t, lambda n=fname: controller.show_frame(n))
            b.pack(pady=6)

        styled_button(self, text="Plein écran (F11)", command=controller.toggle_fullscreen, width=28, height=1).pack(
            pady=6)
        styled_button(self, text="Quitter", command=self.quit_app, width=28, height=1).pack(pady=12)

    def quit_app(self):
        if messagebox.askyesno("Quitter", "Voulez-vous vraiment quitter ?"):
            self.controller.destroy()


#####################
# Rock Paper Scissors
#####################
class RPSFrame(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Label(self, text="Pierre-Feuille-Ciseaux", font=("Helvetica", 18, 'bold')).pack(pady=8)

        mode_frame = tk.Frame(self)
        mode_frame.pack(pady=6)

        tk.Label(mode_frame, text="Mode:").pack(side='left')

        self.mode_var = tk.StringVar(value="computer")

        # Use simple tk.Radiobutton for simplicity inside the mode_frame
        tk.Radiobutton(mode_frame, text="Vs Computer", variable=self.mode_var, value="computer").pack(side='left')
        tk.Radiobutton(mode_frame, text="Vs Player", variable=self.mode_var, value="player").pack(side='left')

        self.info_label = tk.Label(self, text="Choisissez votre coup :")
        self.info_label.pack(pady=6)

        self.btn_frame = tk.Frame(self)
        self.btn_frame.pack(pady=6)

        self.choices = ("Pierre", "Feuille", "Ciseaux")
        self.player_choice = None
        self.score_you = 0
        self.score_comp = 0

        self.score_label = tk.Label(self, text=self._score_text())
        self.score_label.pack(pady=6)

        self.result_label = tk.Label(self, text="", font=(None, 12))
        self.result_label.pack(pady=6)

        self.update_buttons()

        ctrl = tk.Frame(self)
        ctrl.pack(pady=10)

        styled_button(ctrl, text="Réinitialiser score", command=self.reset_score, width=15, height=1).pack(side='left',
                                                                                                           padx=6)
        styled_button(ctrl, text="Retour", command=lambda: controller.show_frame('MainMenu'), width=15, height=1).pack(
            side='left', padx=6)

    def _score_text(self):
        return f"Score — Joueur1: {self.score_you}  Joueur2/Ordi: {self.score_comp} (First to 3 wins)"

    def update_buttons(self):
        for b in self.btn_frame.winfo_children():
            b.destroy()
        for choice in self.choices:
            b = styled_button(self.btn_frame, choice, lambda c=choice: self.play(c), width=10, height=1)
            b.pack(side='left', padx=6)

    def play(self, choice):
        mode = self.mode_var.get()
        if mode == "computer":
            comp = random.choice(self.choices)
            winner = self.decide(choice, comp)
            text = f"Tu as joué: {choice} — Ordi: {comp}. "
        else:
            if self.player_choice is None:
                self.player_choice = choice
                self.info_label.config(text="Joueur 2, choisissez votre coup :")
                return
            else:
                comp = choice
                winner = self.decide(self.player_choice, comp)
                text = f"Joueur1: {self.player_choice} — Joueur2: {comp}. "
                self.player_choice = None
                self.info_label.config(text="Choisissez votre coup :")

        if winner == 'tie':
            text += "Égalité."
        elif winner == 'player':
            text += "Joueur1 gagne ce round !"
            self.score_you += 1
        else:
            text += "Joueur2 gagne ce round !" if mode == "player" else "Ordi gagne ce round !"
            self.score_comp += 1

        self.result_label.config(text=text)
        self.score_label.config(text=self._score_text())

        if self.score_you >= 3:
            messagebox.showinfo("Victoire", "Joueur 1 gagne la partie !")
            self.reset_score()
        elif self.score_comp >= 3:
            messagebox.showinfo("Victoire", "Joueur 2/Ordinateur gagne la partie !")
            self.reset_score()

    def decide(self, p1, p2):
        wins = {"Pierre": "Ciseaux", "Feuille": "Pierre", "Ciseaux": "Feuille"}
        if p1 == p2: return "tie"
        return "player" if wins[p1] == p2 else "computer"

    def reset_score(self):
        self.score_you = 0
        self.score_comp = 0
        self.score_label.config(text=self._score_text())
        self.result_label.config(text='Scores réinitialisés.')


#####################
# Tic-Tac-Toe (CORRECTED AND INTEGRATED)
#####################
class TicTacToeFrame(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.mode = None
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.buttons = []
        self.game_active = False
        self.winning_line = []

        # --- UI Containers ---
        self.menu_container = tk.Frame(self, bg=controller.theme['bg'])
        self.game_container = tk.Frame(self, bg=controller.theme['bg'])

        self._build_menu_ui()
        self._build_game_ui()

        self.show_main_menu()

    # --- UI Builders ---
    def _build_menu_ui(self):
        tk.Label(self.menu_container, text="Select Game Mode", font=("Helvetica", 18, 'bold'),
                 bg=self.controller.theme['bg'], fg=self.controller.theme['fg']).pack(pady=20)

        styled_button(self.menu_container, text="Player vs. Player",
                      command=lambda: self.start_game("PvP"),
                      font=("Helvetica", 14), width=20, height=2).pack(pady=10)

        styled_button(self.menu_container, text="Player vs. Computer (AI)",
                      command=lambda: self.start_game("PvE"),
                      font=("Helvetica", 14), width=20, height=2).pack(pady=10)

    def _build_game_ui(self):
        self.status_label = tk.Label(self.game_container, text="", font=("Helvetica", 16, 'bold'))
        self.status_label.grid(row=0, column=0, columnspan=3, pady=10)

        self.board_container = tk.Frame(self.game_container)
        self.board_container.grid(row=1, column=0, columnspan=3)

        for r in range(3):
            row = []
            for c in range(3):
                button = tk.Button(self.board_container, text="", font=("Helvetica", 24, 'bold'),
                                   width=4, height=2, bg="#EEEEEE",
                                   command=lambda row=r, col=c: self.on_button_click(row, col))
                button.grid(row=r, column=c, padx=2, pady=2)
                row.append(button)
            self.buttons.append(row)

        styled_button(self.game_container, text="New Game", command=self.reset_game, font=("Helvetica", 12)).grid(row=2,
                                                                                                                  column=0,
                                                                                                                  columnspan=3,
                                                                                                                  pady=15)
        styled_button(self.game_container, text="Back to Menu", command=self.show_main_menu,
                      font=("Helvetica", 12)).grid(row=3, column=0, columnspan=3, pady=5)

    def update_theme(self, theme):
        super().update_theme(theme)
        self.menu_container.config(bg=theme['bg'])
        self.game_container.config(bg=theme['bg'])
        self.board_container.config(bg=theme['bg'])
        self._update_widget(self.status_label, theme)

    # --- Game Flow ---
    def show_main_menu(self):
        self.game_container.pack_forget()
        self.menu_container.pack(padx=20, pady=40)
        self.update_theme(self.controller.theme)

    def start_game(self, mode):
        self.mode = mode
        self.menu_container.pack_forget()
        self.game_container.pack()
        self._initialize_game_state()

        if self.mode == "PvE" and self.current_player == "X":
            self.controller.after(500, self.ai_move)

    def reset_game(self):
        self._initialize_game_state()
        if self.mode == "PvE" and self.current_player == "X":
            self.controller.after(500, self.ai_move)

    def _initialize_game_state(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.game_active = True
        self.winning_line = []
        self.status_label.config(text=f"Player {self.current_player}'s turn")

        for r in range(3):
            for c in range(3):
                btn = self.buttons[r][c]
                btn.config(text="", state=tk.NORMAL, bg="#EEEEEE",
                           disabledforeground='blue', fg='blue')
        self.update_theme(self.controller.theme)

    # --- Interaction and Logic ---
    def on_button_click(self, r, c):
        if not self.game_active or self.board[r][c] != "":
            return

        self._make_move(r, c)

        if self.mode == "PvE" and self.game_active:
            self.controller.after(500, self.ai_move)

    def _make_move(self, r, c):
        player = self.current_player

        self.board[r][c] = player
        btn = self.buttons[r][c]
        btn_fg = 'blue' if player == 'X' else 'red'

        btn.config(text=player,
                   fg=btn_fg,
                   state=tk.DISABLED,
                   disabledforeground=btn_fg)

        if self.check_winner(r, c):
            self.status_label.config(text=f"Player {player} wins!")
            self.highlight_winner()
            self.game_active = False
            return True
        elif self.check_draw():
            self.status_label.config(text="It's a draw!")
            self.game_active = False
            return True
        else:
            self.switch_player()
            return False

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.status_label.config(text=f"Player {self.current_player}'s turn")

    def highlight_winner(self):
        for r, c in self.winning_line:
            self.buttons[r][c].config(bg="#A8DF8E")

    # --- Minimax AI Logic ---
    def ai_move(self):
        if not self.game_active:
            return

        best_score = -float('inf')
        best_move = None

        for r in range(3):
            for c in range(3):
                if self.board[r][c] == "":
                    self.board[r][c] = "O"
                    score = self.minimax(self.board, 0, False)
                    self.board[r][c] = ""

                    if score > best_score:
                        best_score = score
                        best_move = (r, c)

        if best_move:
            r, c = best_move
            self._make_move(r, c)

    def minimax(self, board, depth, is_maximizing):
        if self.evaluate_board(board, "O"): return 10 - depth
        if self.evaluate_board(board, "X"): return -10 + depth
        if all(board[r][c] != "" for r in range(3) for c in range(3)): return 0

        if is_maximizing:
            best_score = -float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        board[r][c] = "O"
                        score = self.minimax(board, depth + 1, False)
                        board[r][c] = ""
                        best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('inf')
            for r in range(3):
                for c in range(3):
                    if board[r][c] == "":
                        board[r][c] = "X"
                        score = self.minimax(board, depth + 1, True)
                        board[r][c] = ""
                        best_score = min(score, best_score)
            return best_score

    def evaluate_board(self, board, player):
        lines = (
            [(r, c) for c in range(3)] for r in range(3)
        )
        lines = list(lines) + list(
            [(r, c) for r in range(3)] for c in range(3)
        ) + [
                    [(i, i) for i in range(3)],
                    [(i, 2 - i) for i in range(3)]
                ]

        for line in lines:
            if all(board[r][c] == player for r, c in line):
                return True
        return False

    def check_winner(self, last_r, last_c):
        player = self.board[last_r][last_c]
        if all(self.board[last_r][c] == player for c in range(3)):
            self.winning_line = [(last_r, c) for c in range(3)]
            return True
        if all(self.board[r][last_c] == player for r in range(3)):
            self.winning_line = [(r, last_c) for r in range(3)]
            return True
        if last_r == last_c and all(self.board[i][i] == player for i in range(3)):
            self.winning_line = [(i, i) for i in range(3)]
            return True
        if last_r + last_c == 2 and all(self.board[i][2 - i] == player for i in range(3)):
            self.winning_line = [(i, 2 - i) for i in range(3)]
            return True
        return False

    def check_draw(self):
        return all(self.board[r][c] != "" for r in range(3) for c in range(3))


#####################
# Checkers
#####################
class CheckersFrame(ThemedFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

        self.size = 8
        self.turn = 'r'  # 'r' for red (bottom player), 'b' for black (top player)
        self.selected = None

        tk.Label(self, text="Dames (Checkers)", font=("Helvetica", 18, 'bold')).pack(pady=8)

        self.turn_label = tk.Label(self, text=f"Turn: {'Red' if self.turn == 'r' else 'Black'}", font=("Helvetica", 14))
        self.turn_label.pack()

        self.board_frame = tk.Frame(self)
        self.board_frame.pack()

        self.reset_board()

        styled_button(self, text="Reset Game", command=self.reset_board, width=15, height=1).pack(pady=5)
        styled_button(self, text="Retour", command=lambda: controller.show_frame('MainMenu'), width=15, height=1).pack(
            pady=10)

    # --- Setup and UI Methods ---
    def reset_board(self):
        for w in self.board_frame.winfo_children():
            w.destroy()

        self.board = [['' for _ in range(self.size)] for _ in range(self.size)]
        self.squares = []

        for r in range(self.size):
            row = []
            for c in range(self.size):
                # NOTE: Checkers squares use fixed light/dark colors independent of theme
                color = '#555555' if (r + c) % 2 != 0 else '#FFFFFF'
                piece_text = ''

                if r < 3 and (r + c) % 2 != 0:
                    piece_text = 'b'
                if r > 4 and (r + c) % 2 != 0:
                    piece_text = 'r'

                b = tk.Button(
                    self.board_frame,
                    text=piece_text.upper(),
                    width=4, height=2,
                    bg=color,
                    fg='red' if piece_text.lower() == 'r' else 'blue',
                    command=lambda x=r, y=c: self.select(x, y),
                    relief=tk.RAISED
                )
                b.grid(row=r, column=c)
                row.append(b)
                self.board[r][c] = piece_text
            self.squares.append(row)

        self.selected = None
        self.turn = 'r'
        self.update_turn_display()

    def update_buttons(self):
        for r in range(self.size):
            for c in range(self.size):
                b = self.squares[r][c]
                piece = self.board[r][c]

                color = '#555555' if (r + c) % 2 != 0 else '#FFFFFF'
                b.config(bg=color, relief=tk.RAISED)

                if piece:
                    display_text = piece.upper()
                    piece_color = 'red' if piece.lower() == 'r' else 'blue'
                    b.config(text=display_text, fg=piece_color)
                else:
                    b.config(text='', fg='black')

        if self.selected:
            sr, sc = self.selected
            if (sr + sc) % 2 != 0:
                self.squares[sr][sc].config(bg='yellow', relief=tk.SUNKEN)

    def update_turn_display(self):
        color_name = 'Red' if self.turn == 'r' else 'Black'
        location = "Bottom" if self.turn == 'r' else 'Top'
        self.turn_label.config(text=f"Turn: {color_name} ({location})")

    # --- Move Validation Helpers ---
    def get_available_jumps(self, turn):
        jumps = []
        for r in range(self.size):
            for c in range(self.size):
                piece = self.board[r][c]
                if piece and piece.lower() == turn:
                    for dr in [-2, 2]:
                        for dc in [-2, 2]:
                            er, ec = r + dr, c + dc

                            if 0 <= er < self.size and 0 <= ec < self.size and self.board[er][ec] == '' and (
                                    er + ec) % 2 != 0:
                                mr, mc = (r + er) // 2, (c + ec) // 2
                                mid_piece = self.board[mr][mc]

                                if mid_piece and mid_piece.lower() != turn:
                                    is_king = piece.isupper()
                                    is_forward_jump = (turn == 'r' and dr < 0) or (turn == 'b' and dr > 0)

                                    if is_king or is_forward_jump:
                                        jumps.append(((r, c), (er, ec)))
        return jumps

    def get_specific_jumps(self, r, c):
        piece = self.board[r][c]
        if not piece: return []

        turn = piece.lower()
        jumps = []
        is_king = piece.isupper()

        for dr in [-2, 2]:
            for dc in [-2, 2]:
                er, ec = r + dr, c + dc

                if 0 <= er < self.size and 0 <= ec < self.size and self.board[er][ec] == '':
                    mr, mc = (r + er) // 2, (c + ec) // 2
                    mid_piece = self.board[mr][mc]

                    if mid_piece and mid_piece.lower() != turn:
                        is_forward_jump = (turn == 'r' and dr < 0) or (turn == 'b' and dr > 0)
                        if is_king or is_forward_jump:
                            jumps.append((er, ec))
        return jumps

    # --- Core Game Logic ---
    def select(self, r, c):
        piece = self.board[r][c]

        if self.selected is None:
            if piece and piece.lower() == self.turn:
                self.selected = (r, c)
                self.update_buttons()

        else:
            sr, sc = self.selected

            if (r, c) == self.selected or (piece and piece.lower() == self.turn):
                self.selected = (r, c) if (r, c) != self.selected else None
                self.update_buttons()
                return

            if self.attempt_move(sr, sc, r, c):
                pass

            if self.selected is not None and self.selected == (sr, sc):
                self.selected = None

            self.update_buttons()

    def attempt_move(self, sr, sc, er, ec):
        piece = self.board[sr][sc]

        if self.board[er][ec] != '' or (er + ec) % 2 == 0:
            return False

        available_jumps = self.get_available_jumps(self.turn)
        is_jump = abs(er - sr) == 2 and abs(ec - sc) == 2

        if available_jumps and not is_jump:
            return False

        dr = er - sr
        dc = ec - sc
        is_king = piece.isupper()

        # Execute Jump
        if is_jump:
            current_piece_jumps_to_dest = [j for j in available_jumps if j[0] == (sr, sc) and j[1] == (er, ec)]
            if current_piece_jumps_to_dest:
                mr, mc = (sr + er) // 2, (sc + ec) // 2

                self.board[er][ec] = piece
                self.board[sr][sc] = ''
                self.board[mr][mc] = ''

                self.check_for_king(er, ec)

                next_jumps = self.get_specific_jumps(er, ec)

                if next_jumps:
                    self.selected = (er, ec)
                    return True

                self.turn = 'b' if self.turn == 'r' else 'r'
                self.selected = None
                self.update_turn_display()
                return True

        # Execute Normal Move
        elif abs(dr) == 1 and abs(dc) == 1 and not available_jumps:
            is_forward_move = (self.turn == 'r' and dr < 0) or (self.turn == 'b' and dr > 0)

            if is_king or is_forward_move:
                self.board[er][ec] = piece
                self.board[sr][sc] = ''

                self.check_for_king(er, ec)

                self.turn = 'b' if self.turn == 'r' else 'r'
                self.selected = None
                self.update_turn_display()
                return True

        return False

    def check_for_king(self, r, c):
        piece = self.board[r][c]

        if piece == 'r' and r == 0:
            self.board[r][c] = 'R'

        elif piece == 'b' and r == self.size - 1:
            self.board[r][c] = 'B'


#####################
# Sudoku
#####################
class SudokuFrame(ThemedFrame):
    PUZZLE = [
        [5, 3, '', '', 7, '', '', '', ''],
        [6, '', '', 1, 9, 5, '', '', ''],
        ['', 9, 8, '', '', '', '', 6, ''],
        [8, '', '', '', 6, '', '', '', 3],
        [4, '', '8', '', 3, '', '', '', 1],
        [7, '', '', 2, '', '', '', 6, ''],
        ['', '6', '', '', '', '', 2, 8, ''],
        ['', '', '', '4', 1, 9, '', '', 5],
        ['', '', '', '', 8, '', '', 7, 9]
    ]

    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        tk.Label(self, text="Sudoku", font=("Helvetica", 18, 'bold')).pack(pady=8)
        self.board_frame = tk.Frame(self)
        self.board_frame.pack()
        self.entries = []
        for r in range(9):
            row = []
            for c in range(9):
                e = tk.Entry(self.board_frame, width=2, font=("Helvetica", 16), justify='center')
                e.grid(row=r, column=c, padx=2, pady=2)
                val = self.PUZZLE[r][c]
                if val != '':
                    e.insert(0, str(val))
                    e.config(state='disabled')
                row.append(e)
            self.entries.append(row)
        styled_button(self, text="Vérifier solution", command=self.check_solution, width=15, height=1).pack(pady=6)
        styled_button(self, text="Retour", command=lambda: controller.show_frame('MainMenu'), width=15, height=1).pack(
            pady=6)

    def check_solution(self):
        # NOTE: This is a placeholder check and does not implement actual Sudoku validation
        try:
            for r in range(9):
                for c in range(9):
                    v = self.entries[r][c].get()
                    if not v.isdigit() or not 1 <= int(v) <= 9:
                        raise ValueError
            messagebox.showinfo("Bravo", "Sudoku rempli (superficiellement) correctement !")
        except:
            messagebox.showerror("Erreur", "Remplissez toutes les cases avec un entier 1-9")


#####################
# Main Execution
#####################
def main():
    app = GameApp()
    app.mainloop()if __name__ == "__main__":
main()