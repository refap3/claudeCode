import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing Game with Lives and Bonuses")

# Colors
SKY_BLUE = (135, 206, 235)
ROAD_GRAY = (50, 50, 50)
ROAD_LINE = (255, 255, 255)
CAR_RED = (220, 20, 20)
CAR_BLUE = (30, 144, 255)
CAR_GREEN = (34, 139, 34)
CAR_YELLOW = (255, 215, 0)
TEXT_COLOR = (0, 0, 0)
HEART_COLOR = (255, 0, 0)
OBSTACLE_COLORS = [CAR_RED, CAR_BLUE, CAR_GREEN, CAR_YELLOW]

# Game variables
clock = pygame.time.Clock()
FPS = 60
road_width = 400
road_x = (WIDTH - road_width) // 2
road_lines = []
line_height = 40
line_width = 20
line_gap = 40
score = 0
game_over = False
speed = 5
player_speed = 0
max_speed = 10
acceleration = 0.2
deceleration = 0.1
lives = 3
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Player car
player_width = 50
player_height = 80
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20

# Obstacle cars
obstacles = []
obstacle_frequency = 60  # frames between obstacle spawns
obstacle_timer = 0

# Create road lines
for i in range(20):
    y = i * (line_height + line_gap)
    road_lines.append(pygame.Rect(road_x + road_width//2 - line_width//2, y, line_width, line_height))

# Function to draw the player car
def draw_player_car(x, y):
    pygame.draw.rect(screen, CAR_RED, (x, y, player_width, player_height), border_radius=10)
    pygame.draw.rect(screen, (180, 0, 0), (x, y, player_width, player_height), 3, border_radius=10)
    # Car windows
    pygame.draw.rect(screen, (173, 216, 230), (x + 5, y + 5, player_width - 10, 20), border_radius=5)
    pygame.draw.rect(screen, (173, 216, 230), (x + 5, y + player_height - 25, player_width - 10, 20), border_radius=5)
    # Car details
    pygame.draw.rect(screen, (0, 0, 0), (x + 10, y + 10, 10, 10), border_radius=3)
    pygame.draw.rect(screen, (0, 0, 0), (x + player_width - 20, y + 10, 10, 10), border_radius=3)
    # Headlights
    pygame.draw.rect(screen, (255, 255, 0), (x + 5, y + player_height - 10, 10, 5), border_radius=2)
    pygame.draw.rect(screen, (255, 255, 0), (x + player_width - 15, y + player_height - 10, 10, 5), border_radius=2)

# Function to draw obstacle cars
def draw_obstacle_car(x, y, color):
    pygame.draw.rect(screen, color, (x, y, player_width, player_height), border_radius=10)
    pygame.draw.rect(screen, (0, 0, 0), (x, y, player_width, player_height), 3, border_radius=10)
    # Car windows
    pygame.draw.rect(screen, (173, 216, 230), (x + 5, y + 5, player_width - 10, 20), border_radius=5)
    pygame.draw.rect(screen, (173, 216, 230), (x + 5, y + player_height - 25, player_width - 10, 20), border_radius=5)
    # Taillights
    pygame.draw.rect(screen, (255, 0, 0), (x + 5, y + 5, 10, 5), border_radius=2)
    pygame.draw.rect(screen, (255, 0, 0), (x + player_width - 15, y + 5, 10, 5), border_radius=2)

# Function to reset the game
def reset_game():
    global player_x, player_speed, obstacles, score, game_over, speed, lives
    player_x = WIDTH // 2 - player_width // 2
    player_speed = 0
    obstacles = []
    score = 0
    game_over = False
    speed = 5
    lives = 3

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and game_over:
                reset_game()
    
    if not game_over:
        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_speed = min(player_speed + acceleration, max_speed)
        elif keys[pygame.K_DOWN]:
            player_speed = max(player_speed - acceleration, 0)
        else:
            # Gradually slow down when no keys are pressed
            player_speed = max(player_speed - deceleration, 0)
        
        # Move player car horizontally
        if keys[pygame.K_LEFT] and player_x > road_x:
            player_x -= 5
        if keys[pygame.K_RIGHT] and player_x < road_x + road_width - player_width:
            player_x += 5
        
        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer >= obstacle_frequency:
            obstacle_timer = 0
            obstacle_x = random.randint(road_x, road_x + road_width - player_width)
            obstacle_y = -player_height
            obstacle_color = random.choice(OBSTACLE_COLORS)
            obstacles.append([obstacle_x, obstacle_y, obstacle_color])
        
        # Move obstacles
        for obstacle in obstacles[:]:
            obstacle[1] += speed + player_speed  # Move with player's speed
            if obstacle[1] > HEIGHT:
                obstacles.remove(obstacle)
                score += 1
        
        # Check for life bonus
        if score > 0 and score % 10 == 0:
            lives += 1
            # Remove the bonus from score to avoid multiple bonuses
            score -= 10
        
        # Collision detection
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        for obstacle in obstacles:
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], player_width, player_height)
            if player_rect.colliderect(obstacle_rect):
                lives -= 1
                obstacles.remove(obstacle)  # Remove the collided obstacle
                if lives <= 0:
                    game_over = True
        
        # Increase difficulty over time
        if score > 0 and score % 5 == 0:
            speed = 5 + score // 5
    
    # Drawing
    screen.fill(SKY_BLUE)
    
    # Draw road
    pygame.draw.rect(screen, ROAD_GRAY, (road_x, 0, road_width, HEIGHT))
    
    # Draw road lines
    for line in road_lines:
        pygame.draw.rect(screen, ROAD_LINE, line)
    
    # Move road lines to simulate movement
    for line in road_lines:
        line.y += speed + player_speed
        if line.y > HEIGHT:
            line.y = -line_height
    
    # Draw player car
    draw_player_car(player_x, player_y)
    
    # Draw obstacles
    for obstacle in obstacles:
        draw_obstacle_car(obstacle[0], obstacle[1], obstacle[2])
    
    # Draw score
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (20, 20))
    
    # Draw lives
    lives_text = font.render(f"Lives: {lives}", True, TEXT_COLOR)
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 20, 20))
    
    # Draw speed indicator
    speed_text = font.render(f"Speed: {int(player_speed * 10)}", True, TEXT_COLOR)
    screen.blit(speed_text, (WIDTH//2 - speed_text.get_width()//2, 20))
    
    # Draw controls info
    controls_text = font.render("Controls: UP/DOWN to accelerate/brake, LEFT/RIGHT to steer", True, TEXT_COLOR)
    screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 40))
    
    # Draw game over screen
    if game_over:
        game_over_text = big_font.render("GAME OVER!", True, TEXT_COLOR)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        restart_text = font.render("Press R to restart", True, TEXT_COLOR)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(FPS)

# Quit pygame
pygame.quit()
sys.exit()