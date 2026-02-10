import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Font for score
font = pygame.font.SysFont(None, 36)

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 40))
        self.image.fill(WHITE)
        pygame.draw.polygon(self.image, BLACK, [(25, 0), (0, 40), (50, 40)])
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0

    def update(self):
        self.speed_x = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speed_x = -5
        if keystate[pygame.K_RIGHT]:
            self.speed_x = 5
        self.rect.x += self.speed_x
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        all_sprites.add(bullet)
        bullets.add(bullet)

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        pygame.draw.circle(self.image, BLACK, (15, 15), 15)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randrange(-300, -100)
        self.speed_y = random.randrange(1, 4)

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT + 10 or self.rect.left < -25 or self.rect.right > SCREEN_WIDTH + 20:
            self.rect.x = random.randrange(SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randrange(-300, -100)
            self.speed_y = random.randrange(1, 4)

# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill(WHITE)
        pygame.draw.polygon(self.image, BLACK, [(5, 0), (0, 20), (10, 20)])
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y

    def update(self):
        self.rect.y -= 10
        if self.rect.bottom < 0:
            self.kill()

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()

# Create player and add to all_sprites group
player = Player()
all_sprites.add(player)

# Create enemies and add them to all_sprites and enemies groups
for i in range(8):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Game variables
score = 0
lives = 3
shoot_cooldown = 0  # Cooldown timer for shooting

# Main game loop
running = True
while running:
    # Keep the loop running at the right speed
    clock.tick(60)

    # Process input (events)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Continuous shooting with space key
    keystate = pygame.key.get_pressed()
    if keystate[pygame.K_SPACE] and shoot_cooldown <= 0:
        player.shoot()
        shoot_cooldown = 10  # Delay between shots (10 frames = ~0.16 seconds)

    # Decrease cooldown
    if shoot_cooldown > 0:
        shoot_cooldown -= 1

    # Update
    all_sprites.update()

    # Check bullet collision with enemies
    hits = pygame.sprite.groupcollide(bullets, enemies, True, True)
    for hit in hits:
        score += 10
        new_enemy = Enemy()
        all_sprites.add(new_enemy)
        enemies.add(new_enemy)

    # Check if player collides with enemy
    hits = pygame.sprite.spritecollide(player, enemies, True)
    if hits:
        lives -= 1
        if lives <= 0:
            running = False

    # Draw / render
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Draw score and lives
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 50))

    # Flip the display to update the screen
    pygame.display.flip()

# Game over screen
screen.fill(BLACK)
game_over_text = font.render("GAME OVER", True, WHITE)
final_score_text = font.render(f"Final Score: {score}", True, WHITE)
screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50))
screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
pygame.display.flip()
pygame.time.wait(3000)

# Quit Pygame
pygame.quit()