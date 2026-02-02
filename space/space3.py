import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions and frame rate
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter with Dynamic Difficulty and Final Score")

clock = pygame.time.Clock()

# Define fonts for rendering symbols and stats
font = pygame.font.SysFont("Arial", 36)      # For large texts like GAME OVER and final score
stats_font = pygame.font.SysFont("Arial", 24)  # For in-game stats

# Create surfaces using Unicode symbols:
# Player's spaceship: ▲, Enemy: ▼, Bullet: •
player_img = font.render("▲", True, (255, 255, 255))
enemy_img = font.render("▼", True, (255, 0, 0))
bullet_img = font.render("•", True, (255, 255, 0))

# Background color (black for space)
background_color = (0, 0, 0)

# Global game stats
score = 0
lives = 3
misses = 0  # Count of misses in current life (each life tolerates 5 misses)

# Function to compute enemy spawn interval based on lives
def get_spawn_interval(lives):
    if lives >= 3:
        return 1000
    elif lives == 2:
        return 750
    elif lives == 1:
        return 500

# Set initial spawn interval and timer event
enemy_spawn_event = pygame.USEREVENT + 1
current_spawn_interval = get_spawn_interval(lives)
pygame.time.set_timer(enemy_spawn_event, current_spawn_interval)

# Define the Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed = 5
        self.last_shot = 0
        self.shoot_delay = 250  # milliseconds delay between shots

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()
            if now - self.last_shot > self.shoot_delay:
                self.last_shot = now
                self.shoot()

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Define the Enemy class with dynamic speed based on lives
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        # Increase enemy speed as lives decrease
        base_speed = random.randint(1, 3)
        difficulty_factor = 1 + (3 - lives) * 0.5  # Lives 3->factor 1; Lives 2->1.5; Lives 1->2
        self.speedy = base_speed * difficulty_factor

    def update(self):
        global lives, misses
        self.rect.y += self.speedy
        # If enemy goes off the bottom, count as a miss
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
            misses += 1
            # Check if misses exceed allowed per life
            if misses >= 5:
                lives -= 1
                misses = 0

# Define the Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Instantiate the player and add to sprite group
player = Player()
all_sprites.add(player)

# Function to spawn enemies
def spawn_enemy():
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Function to draw score and lives information
def draw_stats(surface, score, lives, misses):
    score_text = stats_font.render(f"Score: {score}", True, (255, 255, 255))
    lives_text = stats_font.render(f"Lives: {lives} (Misses: {misses}/5)", True, (255, 255, 255))
    surface.blit(score_text, (10, 10))
    surface.blit(lives_text, (10, 40))

# Function to display the game over screen along with the final score
def show_game_over(final_score):
    game_over_text = font.render("GAME OVER", True, (255, 0, 0))
    final_score_text = font.render(f"Final Score: {final_score}", True, (255, 255, 255))
    screen.fill(background_color)
    # Center the texts on the screen with adequate spacing
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
    screen.blit(game_over_text, game_over_rect)
    screen.blit(final_score_text, final_score_rect)
    pygame.display.flip()
    # Wait for a key press or quit event
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            break

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    # Update spawn timer based on current lives
    desired_interval = get_spawn_interval(lives)
    if desired_interval != current_spawn_interval:
        pygame.time.set_timer(enemy_spawn_event, desired_interval)
        current_spawn_interval = desired_interval
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == enemy_spawn_event:
            spawn_enemy()

    all_sprites.update()

    # Check for collisions between bullets and enemies
    hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
    for hit in hits:
        score += 10  # Increase score for each enemy hit

    # Check for game over condition
    if lives <= 0:
        show_game_over(score)
        running = False
        continue

    # Render the game scene
    screen.fill(background_color)
    all_sprites.draw(screen)
    draw_stats(screen, score, lives, misses)
    pygame.display.flip()

pygame.quit()
sys.exit()

