import random
import pygame
from game.text_box import TextBox

MIN_NUMBER = 1
MAX_NUMBER = 100

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.secret_number = random.randint(MIN_NUMBER, MAX_NUMBER)
        self.attempts = 0
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False

        # Task 2: track the narrowing search range
        self.range_low = MIN_NUMBER
        self.range_high = MAX_NUMBER

        self.input_box = TextBox(width // 2 - 110, 150, 120, 48)
        self.submit_btn = pygame.Rect(width // 2 + 25, 150, 100, 48)

        self.font_title = pygame.font.SysFont(None, 42)
        self.font_medium = pygame.font.SysFont(None, 28)
        self.font_btn = pygame.font.SysFont(None, 26)

    def show_warning(self, message):
        self.feedback_msg = message
        self.feedback_color = (240, 200, 80)

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
            # Task 2: secret is above this guess, raise the lower bound
            self.range_low = max(self.range_low, guess + 1)
        elif guess > self.secret_number:
            self.feedback_msg = f"TOO HIGH! (Guess was {guess})"
            self.feedback_color = (240, 100, 80)
            # Task 2: secret is below this guess, lower the upper bound
            self.range_high = min(self.range_high, guess - 1)
        else:
            self.feedback_msg = f"CORRECT! Found in {self.attempts} attempts."
            self.feedback_color = (80, 220, 90)
            self.game_won = True
            self.range_low = guess
            self.range_high = guess

    def reset(self):
        self.secret_number = random.randint(MIN_NUMBER, MAX_NUMBER)
        self.attempts = 0
        self.feedback_msg = "Enter a number between 1 and 100"
        self.feedback_color = (220, 220, 220)
        self.game_won = False
        self.range_low = MIN_NUMBER
        self.range_high = MAX_NUMBER
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

    def render(self, screen):
        screen.fill((30, 34, 42))

        title_surf = self.font_title.render("Number Guessing Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 35))

        attempts_surf = self.font_medium.render(f"Attempts: {self.attempts}", True, (180, 185, 195))
        screen.blit(attempts_surf, (self.width // 2 - attempts_surf.get_width() // 2, 95))
        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 80), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(
            btn_text,
            (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2),
        )

        feedback_surf = self.font_medium.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 235))

        # Task 2: show the current valid search range
        if self.game_won:
            range_text = f"The number was {self.secret_number}"
        else:
            range_text = f"Search range: {self.range_low} to {self.range_high}"
        range_surf = self.font_medium.render(range_text, True, (120, 220, 230))
        screen.blit(range_surf, (self.width // 2 - range_surf.get_width() // 2, 275))

        if self.game_won:
            restart_surf = self.font_medium.render("Press [R] to Start a New Game", True, (255, 220, 80))
            screen.blit(restart_surf, (self.width // 2 - restart_surf.get_width() // 2, 320))
