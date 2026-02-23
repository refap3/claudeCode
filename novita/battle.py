import pygame
import random
import math
import numpy as np

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship Battle")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Create simple sound effects using pygame.mixer
def create_sounds():
    # Initialize mixer
    pygame.mixer.init()
    
    # Create a simple beep sound for shooting
    # Create a waveform for a short beep sound
    sample_rate = 22050
    duration = 0.1  # seconds
    
    # Generate a simple square wave for shooting sound
    frames = int(duration * sample_rate)
    shoot_mono = np.array(
        [32767 * (1 if i % 100 < 50 else -1) for i in range(frames)],
        dtype=np.int16
    )
    shoot_wave = np.column_stack([shoot_mono, shoot_mono])
    shoot_sound = pygame.sndarray.make_sound(shoot_wave)
    shoot_sound.set_volume(0.3)

    # Create explosion sound
    # Create a short, sharp sound for explosions
    exp_frames = int(0.2 * sample_rate)
    explosion_mono = np.array(
        [min(32767, max(-32768,
             int(32767 * math.exp(-i / (sample_rate * 0.05))) + random.randint(-2000, 2000)))
         for i in range(exp_frames)],
        dtype=np.int16
    )
    explosion_wave = np.column_stack([explosion_mono, explosion_mono])
    explosion_sound = pygame.sndarray.make_sound(explosion_wave)
    explosion_sound.set_volume(0.5)
    
    return shoot_sound, explosion_sound

# Player class
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.speed = 5
        self.health = 100
        self.max_health = 100
        self.shoot_cooldown = 0
        self.score = 0
        self.lives = 3
        self.shoot_sound = None
        self.explosion_sound = None
        
    def draw(self, screen):
        # Draw ship body
        pygame.draw.polygon(screen, BLUE, [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width/2, self.y - self.height)
        ])
        # Draw cockpit
        pygame.draw.circle(screen, WHITE, (self.x + self.width/2, self.y - self.height/2), 10)
        # Draw engine glow
        pygame.draw.polygon(screen, YELLOW, [
            (self.x + self.width/2 - 10, self.y),
            (self.x + self.width/2 + 10, self.y),
            (self.x + self.width/2, self.y + 15)
        ])
        
        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x, self.y - 20, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 20, self.width * (self.health/self.max_health), 5))
        
    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < HEIGHT - self.height:
            self.y += self.speed
            
    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = 5  # Reduced cooldown for continuous firing
            # Play shooting sound
            if self.shoot_sound:
                self.shoot_sound.play()
            return Bullet(self.x + self.width/2 - 2, self.y - self.height, True)
        return None
        
    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

# Enemy class
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 30
        self.speed = random.uniform(1.0, 3.0)
        self.health = 30
        self.max_health = 30
        self.shoot_cooldown = random.randint(30, 120)
        self.explosion_sound = None
        
    def draw(self, screen):
        # Draw enemy ship
        pygame.draw.polygon(screen, RED, [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width/2, self.y + self.height)
        ])
        # Draw cockpit
        pygame.draw.circle(screen, WHITE, (self.x + self.width/2, self.y + self.height/2), 8)
        # Draw engine glow
        pygame.draw.polygon(screen, ORANGE, [
            (self.x + self.width/2 - 8, self.y + self.height),
            (self.x + self.width/2 + 8, self.y + self.height),
            (self.x + self.width/2, self.y + self.height - 10)
        ])
        
        # Draw health bar
        pygame.draw.rect(screen, RED, (self.x, self.y - 15, self.width, 4))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 15, self.width * (self.health/self.max_health), 4))
        
    def move(self):
        self.y += self.speed
        self.shoot_cooldown -= 1
        
    def shoot(self):
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = random.randint(60, 180)
            return Bullet(self.x + self.width/2 - 2, self.y + self.height, False)
        return None

# Bullet class
class Bullet:
    def __init__(self, x, y, is_player_bullet):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 10
        self.speed = 7
        self.is_player_bullet = is_player_bullet
        
    def draw(self, screen):
        if self.is_player_bullet:
            pygame.draw.rect(screen, GREEN, (self.x, self.y, self.width, self.height))
        else:
            pygame.draw.rect(screen, RED, (self.x, self.y, self.width, self.height))
            
    def move(self):
        if self.is_player_bullet:
            self.y -= self.speed
        else:
            self.y += self.speed
            
    def is_off_screen(self):
        return self.y < 0 or self.y > HEIGHT

# Explosion class
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 20
        self.growth_rate = 1.5
        self.active = True
        self.explosion_sound = None
        
    def update(self):
        self.radius += self.growth_rate
        if self.radius > self.max_radius:
            self.active = False
            
    def draw(self, screen):
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), int(self.radius))
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), int(self.radius/2))

# Game class
class Game:
    def __init__(self):
        self.player = Player(WIDTH/2 - 25, HEIGHT - 60)
        self.enemies = []
        self.bullets = []
        self.explosions = []
        self.enemy_spawn_timer = 0
        self.game_over = False
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        # Create sounds
        try:
            self.shoot_sound, self.explosion_sound = create_sounds()
            # Assign sounds to objects
            self.player.shoot_sound = self.shoot_sound
            self.player.explosion_sound = self.explosion_sound
        except Exception as e:
            # Fallback to None if sound creation fails
            print(f"Sound initialization failed: {e}")
            self.shoot_sound = None
            self.explosion_sound = None
            self.player.shoot_sound = None
            self.player.explosion_sound = None
        
    def spawn_enemy(self):
        x = random.randint(0, WIDTH - 40)
        enemy = Enemy(x, -30)
        enemy.explosion_sound = self.explosion_sound
        self.enemies.append(enemy)
        
    def update(self):
        if self.game_over:
            return
            
        # Update player
        self.player.update()
        
        # Spawn enemies
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= 60:  # Spawn every 60 frames
            self.spawn_enemy()
            self.enemy_spawn_timer = 0
            
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.move()
            
            # Enemy shooting
            bullet = enemy.shoot()
            if bullet:
                self.bullets.append(bullet)
                
            # Remove enemies that go off screen
            if enemy.y > HEIGHT:
                self.enemies.remove(enemy)
                
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.move()
            
            # Remove bullets that go off screen
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
                
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)
                
        # Check collisions
        self.check_collisions()
        
    def check_collisions(self):
        # Player bullets hitting enemies
        for bullet in self.bullets[:]:
            if bullet.is_player_bullet:
                for enemy in self.enemies[:]:
                    if (bullet.x < enemy.x + enemy.width and
                        bullet.x + bullet.width > enemy.x and
                        bullet.y < enemy.y + enemy.height and
                        bullet.y + bullet.height > enemy.y):
                        
                        # Hit enemy
                        enemy.health -= 10
                        if enemy.health <= 0:
                            self.enemies.remove(enemy)
                            self.player.score += 100
                            # Create explosion
                            explosion = Explosion(enemy.x + enemy.width/2, enemy.y + enemy.height/2)
                            explosion.explosion_sound = self.explosion_sound
                            self.explosions.append(explosion)
                            # Play explosion sound
                            if explosion.explosion_sound:
                                explosion.explosion_sound.play()
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
                        break
                        
        # Enemy bullets hitting player
        for bullet in self.bullets[:]:
            if not bullet.is_player_bullet:
                if (bullet.x < self.player.x + self.player.width and
                    bullet.x + bullet.width > self.player.x and
                    bullet.y < self.player.y + self.player.height and
                    bullet.y + bullet.height > self.player.y):
                    
                    # Hit player
                    self.player.health -= 10
                    if self.player.health <= 0:
                        self.player.lives -= 1
                        self.player.health = self.player.max_health
                        if self.player.lives <= 0:
                            self.game_over = True
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                        
    def draw(self, screen):
        # Draw background
        screen.fill(BLACK)
        
        # Draw stars
        for i in range(100):
            x = (i * 17) % WIDTH
            y = (i * 13) % HEIGHT
            pygame.draw.circle(screen, WHITE, (x, y), 1)
            
        # Draw player
        self.player.draw(screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen)
            
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
            
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(screen)
            
        # Draw UI
        score_text = self.font.render(f"Score: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        health_text = self.small_font.render(f"Health: {self.player.health}", True, WHITE)
        
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (WIDTH - 120, 10))
        screen.blit(health_text, (10, 50))
        
        # Draw game over screen
        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, RED)
            restart_text = self.small_font.render("Press R to Restart", True, WHITE)
            screen.blit(game_over_text, (WIDTH/2 - 80, HEIGHT/2 - 20))
            screen.blit(restart_text, (WIDTH/2 - 70, HEIGHT/2 + 20))
            
        # Draw instructions
        if not self.game_over:
            instr_text1 = self.small_font.render("ARROW KEYS: move  SPACE: shoot  M: mute  Q: quit", True, WHITE)
            screen.blit(instr_text1, (WIDTH/2 - 190, HEIGHT - 20))

# Main game loop
def main():
    clock = pygame.time.Clock()
    game = Game()
    
    running = True
    muted = False
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_m:
                    muted = not muted
                    pygame.mixer.set_num_channels(0 if muted else 8)
                elif event.key == pygame.K_r and game.game_over:
                    # Restart game
                    game = Game()
                    
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if not game.game_over:
            game.player.move(keys)
            # Fire continuously when space is pressed
            if keys[pygame.K_SPACE]:
                bullet = game.player.shoot()
                if bullet:
                    game.bullets.append(bullet)
        
        # Update game state
        game.update()
        
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(60)
        
    pygame.quit()

if __name__ == "__main__":
    main()