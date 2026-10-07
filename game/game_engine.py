import random
import pygame
from game.text_box import TextBox

MIN_NUMBER = 1
MAX_NUMBER = 100
PLAY_WIDTH = 620   # left area for the game, right area for the history panel
MAX_HISTORY = 6    # Task 3: how many recent guesses to show

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.play_width = PLAY_WIDTH
        cx = self.play_width // 2

        self.secret_number = random.randint(MIN_NUMBER, MAX_NUMBER)
        self.attempts = 0
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False

        # Task 2: track the narrowing search range
        self.range_low = MIN_NUMBER
        self.range_high = MAX_NUMBER

        # Task 3: list of (attempt_number, guess, result)
        self.history = []

        self.input_box = TextBox(cx - 110, 150, 120, 48)
        self.submit_btn = pygame.Rect(cx + 25, 150, 100, 48)

        self.font_title = pygame.font.SysFont(None, 42)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_btn = pygame.font.SysFont(None, 26)
        self.font_small = pygame.font.SysFont(None, 20)

    def show_warning(self, message):
        self.feedback_msg = message
        self.feedback_color = (240, 200, 80)

    def add_to_history(self, guess, result):
        self.history.append((self.attempts, guess, result))
        if len(self.history) > MAX_HISTORY:
            self.history.pop(0)

    def submit_guess(self):
        if self.game_won:
            return

        text = self.input_box.text.strip()

        # Task 1 fix: empty input no longer crashes and does not use an attempt
        if not text:
            self.show_warning("Please type a number before submitting!")
            return

        try:
            guess = int(text)
        except ValueError:
            self.show_warning("Invalid input! Digits only.")
            self.input_box.clear()
            return

        # Reject numbers outside 1-100 without using an attempt
        if guess < MIN_NUMBER or guess > MAX_NUMBER:
            self.show_warning("Out of range! Pick a number from 1 to 100.")
            self.input_box.clear()
            return

        self.attempts += 1
        self.input_box.clear()

        if guess < self.secret_number:
            self.feedback_msg = f"TOO LOW! (Guess was {guess})"
            self.feedback_color = (80, 160, 240)
            self.range_low = max(self.range_low, guess + 1)
            self.add_to_history(guess, "low")
        elif guess > self.secret_number:
            self.feedback_msg = f"TOO HIGH! (Guess was {guess})"
            self.feedback_color = (240, 100, 80)
            self.range_high = min(self.range_high, guess - 1)
            self.add_to_history(guess, "high")
        else:
            self.feedback_msg = f"CORRECT! Found in {self.attempts} attempts."
            self.feedback_color = (80, 220, 90)
            self.game_won = True
            self.range_low = guess
            self.range_high = guess
            self.add_to_history(guess, "correct")

    def reset(self):
        self.secret_number = random.randint(MIN_NUMBER, MAX_NUMBER)
        self.attempts = 0
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False
        self.range_low = MIN_NUMBER
        self.range_high = MAX_NUMBER
        self.history = []
        self.input_box.clear()

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.submit_guess()
            elif event.key == pygame.K_r and self.game_won:
                self.reset()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()

    def update(self):
        pass

    def draw_centered(self, screen, surf, y):
        screen.blit(surf, (self.play_width // 2 - surf.get_width() // 2, y))

    # Task 3: recent guess history panel
    def draw_history_panel(self, screen):
        panel = pygame.Rect(self.play_width, 20, self.width - self.play_width - 20, self.height - 40)
        pygame.draw.rect(screen, (40, 45, 56), panel, border_radius=8)
        pygame.draw.rect(screen, (70, 76, 90), panel, width=2, border_radius=8)

        title = self.font_medium.render("Recent Guesses", True, (245, 245, 245))
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 15))

        if not self.history:
            empty = self.font_small.render("No guesses yet", True, (140, 145, 155))
            screen.blit(empty, (panel.centerx - empty.get_width() // 2, panel.y + 60))
            return

        y = panel.y + 55
        for attempt_no, guess, result in reversed(self.history):
            if result == "high":
                color, label = (240, 100, 80), "TOO HIGH"
            elif result == "low":
                color, label = (80, 160, 240), "TOO LOW"
            else:
                color, label = (80, 220, 90), "CORRECT"

            row = pygame.Rect(panel.x + 10, y, panel.width - 20, 34)
            pygame.draw.rect(screen, (52, 58, 72), row, border_radius=6)
            pygame.draw.rect(screen, color, (row.x, row.y, 5, row.height), border_radius=3)

            num = self.font_small.render(f"#{attempt_no}", True, (150, 155, 165))
            screen.blit(num, (row.x + 12, row.centery - num.get_height() // 2))

            guess_surf = self.font_medium.render(str(guess), True, (245, 245, 245))
            screen.blit(guess_surf, (row.x + 46, row.centery - guess_surf.get_height() // 2))

            ax, cy = row.right - 16, row.centery
            if result == "high":
                pygame.draw.polygon(screen, color, [(ax - 7, cy - 4), (ax + 7, cy - 4), (ax, cy + 6)])
            elif result == "low":
                pygame.draw.polygon(screen, color, [(ax - 7, cy + 4), (ax + 7, cy + 4), (ax, cy - 6)])
            else:
                pygame.draw.circle(screen, color, (ax, cy), 6)

            label_surf = self.font_small.render(label, True, color)
            screen.blit(label_surf, (ax - 14 - label_surf.get_width(), row.centery - label_surf.get_height() // 2))

            y += 40

    def render(self, screen):
        screen.fill((30, 34, 42))

        title_surf = self.font_title.render("Number Guessing Arena", True, (245, 245, 245))
        self.draw_centered(screen, title_surf, 35)

        attempts_surf = self.font_medium.render(f"Attempts: {self.attempts}", True, (180, 185, 195))
        self.draw_centered(screen, attempts_surf, 95)
        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(
            btn_text,
            (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2),
        )

        feedback_surf = self.font_medium.render(self.feedback_msg, True, self.feedback_color)
        self.draw_centered(screen, feedback_surf, 235)

        # Task 2: show the current valid search range
        if self.game_won:
            range_text = f"The number was {self.secret_number}"
        else:
            range_text = f"Search range: {self.range_low} to {self.range_high}"
        range_surf = self.font_medium.render(range_text, True, (120, 220, 230))
        self.draw_centered(screen, range_surf, 275)

        if self.game_won:
            restart_surf = self.font_medium.render("Press [R] to Start a New Game", True, (255, 220, 80))
            self.draw_centered(screen, restart_surf, 320)

        self.draw_history_panel(screen)
