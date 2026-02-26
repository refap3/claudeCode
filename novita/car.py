import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Window icon — tiny top-down car drawn on a 32×32 surface
def _make_icon():
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    # Road background
    s.fill((50, 50, 50))
    # Wheels
    for wx, wy in [(2, 6), (22, 6), (2, 20), (22, 20)]:
        pygame.draw.rect(s, (20, 20, 20), (wx, wy, 8, 7), border_radius=2)
    # Body
    body = [(10, 2), (22, 2), (26, 10), (26, 28), (6, 28), (6, 10)]
    pygame.draw.polygon(s, (220, 20, 20), body)
    pygame.draw.polygon(s, (160, 0, 0), body, 1)
    # Windscreen
    pygame.draw.rect(s, (100, 180, 255), (11, 8, 10, 7), border_radius=2)
    # Centre stripe
    pygame.draw.rect(s, (255, 255, 255), (15, 2, 2, 26))
    return s

pygame.display.set_icon(_make_icon())

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Car Racing — How Far Can You Go?")

# Colors
SKY_BLUE = (135, 206, 235)
ROAD_GRAY = (50, 50, 50)
ROAD_LINE = (255, 255, 255)
CAR_RED = (220, 20, 20)
CAR_BLUE = (30, 144, 255)
CAR_GREEN = (34, 139, 34)
CAR_YELLOW = (255, 215, 0)
TEXT_COLOR = (0, 0, 0)
OBSTACLE_COLORS = [CAR_RED, CAR_BLUE, CAR_GREEN, CAR_YELLOW]
NITRO_GREEN = (0, 220, 80)
NITRO_GLOW = (180, 255, 100)
OIL_COLOR = (15, 10, 5)
WHEEL_TIRE = (15, 15, 15)
WHEEL_RIM = (130, 130, 130)
WING_BAR = (45, 45, 45)
WING_PLATE = (255, 200, 0)   # yellow endplates — visible on dark road

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

# Difficulty progression
difficulty_level = 0
DISTANCE_PER_LEVEL = 10_000   # 10 km (distance units; 1 km = 1 000 units)
BASE_SPEED = 5
BASE_OBSTACLE_FREQ = 60       # frames between spawns
level_up_timer = 0
LEVEL_UP_DISPLAY = 180        # show "Level Up" for 3 seconds

# Distance tracking
distance = 0.0
BONUS_DISTANCE_PER_KILL = 500

# Nitro system
nitro_available = False
nitro_active = False
nitro_timer = 0
NITRO_DURATION = 300        # 5 seconds × 60 fps
nitro_depots = []
depot_spawn_timer = 0
DEPOT_SPAWN_INTERVAL = 240  # ~4 seconds between depot spawns

# Oil spots
oil_spots = []
oil_spawn_timer = 0
OIL_SPAWN_INTERVAL = 180    # ~3 seconds between oil spawns

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


# Draw the player car as a top-down F1-style racing car
def draw_player_car(x, y, nitro):
    # Wheels (tire then silver rim overlay)
    for wx, wy in [(x - 3, y + 12), (x + 45, y + 12), (x - 3, y + 52), (x + 45, y + 52)]:
        pygame.draw.rect(screen, WHEEL_TIRE, (wx, wy, 8, 18), border_radius=3)
        pygame.draw.rect(screen, WHEEL_RIM,  (wx + 1, wy + 4, 6, 10), border_radius=2)

    # Front wing — dark bar with yellow endplates
    pygame.draw.rect(screen, WING_BAR,   (x - 5, y + 4, 60, 7), border_radius=2)
    pygame.draw.rect(screen, WING_PLATE, (x - 5, y + 2, 8, 11), border_radius=2)   # left endplate
    pygame.draw.rect(screen, WING_PLATE, (x + 47, y + 2, 8, 11), border_radius=2)  # right endplate

    # Rear wing — dark bar with yellow endplates
    pygame.draw.rect(screen, WING_BAR,   (x - 5, y + 70, 60, 7), border_radius=2)
    pygame.draw.rect(screen, WING_PLATE, (x - 5, y + 68, 8, 11), border_radius=2)
    pygame.draw.rect(screen, WING_PLATE, (x + 47, y + 68, 8, 11), border_radius=2)

    # Main body — tapered F1 polygon, front at top
    body_color = NITRO_GLOW if nitro else CAR_RED
    body_outline = (120, 200, 60) if nitro else (160, 0, 0)
    body_points = [
        (x + 18, y +  5),   # front-left
        (x + 32, y +  5),   # front-right
        (x + 42, y + 25),   # right shoulder
        (x + 43, y + 55),   # right side max
        (x + 40, y + 75),   # rear-right
        (x + 10, y + 75),   # rear-left
        (x +  7, y + 55),   # left side max
        (x +  8, y + 25),   # left shoulder
    ]
    pygame.draw.polygon(screen, body_color, body_points)
    pygame.draw.polygon(screen, body_outline, body_points, 2)

    # Center racing stripe
    pygame.draw.rect(screen, (255, 255, 255), (x + 22, y + 5, 6, 70))

    # Cockpit (dark visor in upper body)
    pygame.draw.ellipse(screen, (25, 25, 25), (x + 17, y + 22, 16, 22))
    pygame.draw.ellipse(screen, (80, 80, 80), (x + 17, y + 22, 16, 22), 1)

    # Headlights at front
    pygame.draw.rect(screen, (255, 220, 0), (x +  8, y + 5, 8, 4), border_radius=1)
    pygame.draw.rect(screen, (255, 220, 0), (x + 34, y + 5, 8, 4), border_radius=1)

    # Nitro exhaust flames at rear
    if nitro:
        pygame.draw.circle(screen, (255, 150, 0), (x + 19, y + 82), 5)
        pygame.draw.circle(screen, (255, 230, 0), (x + 19, y + 82), 3)
        pygame.draw.circle(screen, (255, 150, 0), (x + 31, y + 82), 5)
        pygame.draw.circle(screen, (255, 230, 0), (x + 31, y + 82), 3)


# Draw an obstacle car (street car style)
def draw_obstacle_car(x, y, color):
    pygame.draw.rect(screen, color, (x, y, player_width, player_height), border_radius=10)
    pygame.draw.rect(screen, (0, 0, 0), (x, y, player_width, player_height), 3, border_radius=10)
    # Windows
    pygame.draw.rect(screen, (173, 216, 230), (x + 5, y + 5, player_width - 10, 20), border_radius=5)
    pygame.draw.rect(screen, (173, 216, 230), (x + 5, y + player_height - 25, player_width - 10, 20), border_radius=5)
    # Taillights (top = facing away from player)
    pygame.draw.rect(screen, (255, 0, 0), (x + 5, y + 5, 10, 5), border_radius=2)
    pygame.draw.rect(screen, (255, 0, 0), (x + player_width - 15, y + 5, 10, 5), border_radius=2)


# Draw a nitro fuel depot (green box with lightning bolt)
def draw_nitro_depot(x, y):
    pygame.draw.rect(screen, NITRO_GREEN, (x, y, 40, 35), border_radius=5)
    pygame.draw.rect(screen, (0, 150, 50), (x, y, 40, 35), 2, border_radius=5)
    bolt = [
        (x + 22, y +  4),
        (x + 14, y + 18),
        (x + 20, y + 18),
        (x + 18, y + 31),
        (x + 26, y + 17),
        (x + 20, y + 17),
    ]
    pygame.draw.polygon(screen, (255, 230, 0), bolt)


# Draw an oil spot (dark slick ellipse)
def draw_oil_spot(x, y):
    pygame.draw.ellipse(screen, OIL_COLOR, (x, y, 60, 22))
    pygame.draw.ellipse(screen, (40, 25, 10), (x + 8, y + 4, 30, 10))


def pick_spawn_x(width, margin=10, attempts=8):
    """Return a random road x that doesn't x-overlap with any on-screen item."""
    blocked = [obs[0] for obs in obstacles] + \
              [dep[0] for dep in nitro_depots] + \
              [oil[0] for oil in oil_spots]
    for _ in range(attempts):
        x = random.randint(road_x, road_x + road_width - width)
        if all(abs(x - bx) > width + margin for bx in blocked):
            return x
    return random.randint(road_x, road_x + road_width - width)  # fallback


# Reset all game state
def reset_game():
    global player_x, player_speed, obstacles, score, game_over, speed, lives
    global distance, nitro_available, nitro_active, nitro_timer
    global nitro_depots, depot_spawn_timer, oil_spots, oil_spawn_timer
    global obstacle_timer, difficulty_level, obstacle_frequency, level_up_timer
    player_x = WIDTH // 2 - player_width // 2
    player_speed = 0
    obstacles = []
    score = 0
    game_over = False
    speed = BASE_SPEED
    lives = 3
    distance = 0.0
    nitro_available = False
    nitro_active = False
    nitro_timer = 0
    nitro_depots = []
    depot_spawn_timer = 0
    oil_spots = []
    oil_spawn_timer = 0
    obstacle_timer = 0
    difficulty_level = 0
    obstacle_frequency = BASE_OBSTACLE_FREQ
    level_up_timer = 0


# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False
            elif event.key == pygame.K_r and game_over:
                reset_game()
            elif event.key == pygame.K_n and not game_over:
                if nitro_available and not nitro_active:
                    nitro_active = True
                    nitro_available = False
                    nitro_timer = NITRO_DURATION

    # Speed multiplier: nitro doubles all movement
    speed_mult = 2 if nitro_active else 1

    if not game_over:
        # Player controls
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            player_speed = min(player_speed + acceleration, max_speed)
        elif keys[pygame.K_DOWN]:
            player_speed = max(player_speed - acceleration, 0)
        else:
            player_speed = max(player_speed - deceleration, 0)

        if keys[pygame.K_LEFT] and player_x > road_x:
            player_x -= 5
        if keys[pygame.K_RIGHT] and player_x < road_x + road_width - player_width:
            player_x += 5

        # Accumulate distance (scaled to give sensible meter values)
        distance += (speed + player_speed) * speed_mult * 0.5

        # Nitro countdown
        if nitro_active:
            nitro_timer -= 1
            if nitro_timer <= 0:
                nitro_active = False

        # Spawn obstacles
        obstacle_timer += 1
        if obstacle_timer >= obstacle_frequency:
            obstacle_timer = 0
            obstacle_x = pick_spawn_x(player_width)
            obstacle_color = random.choice(OBSTACLE_COLORS)
            obstacles.append([obstacle_x, -player_height, obstacle_color])

        # Move obstacles
        for obstacle in obstacles[:]:
            obstacle[1] += (speed + player_speed) * speed_mult
            if obstacle[1] > HEIGHT:
                obstacles.remove(obstacle)
                score += 1

        # Spawn nitro depots
        depot_spawn_timer += 1
        if depot_spawn_timer >= DEPOT_SPAWN_INTERVAL:
            depot_spawn_timer = 0
            dx = pick_spawn_x(40)
            nitro_depots.append([dx, -40])

        # Move nitro depots
        for depot in nitro_depots[:]:
            depot[1] += (speed + player_speed) * speed_mult
            if depot[1] > HEIGHT:
                nitro_depots.remove(depot)

        # Spawn oil spots
        oil_spawn_timer += 1
        if oil_spawn_timer >= OIL_SPAWN_INTERVAL:
            oil_spawn_timer = 0
            ox = pick_spawn_x(60)
            oil_spots.append([ox, -25])

        # Move oil spots
        for oil in oil_spots[:]:
            oil[1] += (speed + player_speed) * speed_mult
            if oil[1] > HEIGHT:
                oil_spots.remove(oil)

        # Difficulty scaling — every 10 km
        new_level = int(distance // DISTANCE_PER_LEVEL)
        if new_level > difficulty_level:
            difficulty_level = new_level
            speed = BASE_SPEED + difficulty_level          # +1 scroll speed per level
            obstacle_frequency = max(20, BASE_OBSTACLE_FREQ - difficulty_level * 5)  # denser traffic, floor 20
            level_up_timer = LEVEL_UP_DISPLAY

        if level_up_timer > 0:
            level_up_timer -= 1

        # Collision detection
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)

        for obstacle in obstacles[:]:
            obstacle_rect = pygame.Rect(obstacle[0], obstacle[1], player_width, player_height)
            if player_rect.colliderect(obstacle_rect):
                obstacles.remove(obstacle)
                if nitro_active:
                    # Nitro kill — bonus distance instead of damage
                    distance += BONUS_DISTANCE_PER_KILL
                else:
                    lives -= 1
                    if lives <= 0:
                        game_over = True

        # Nitro depot collection
        for depot in nitro_depots[:]:
            depot_rect = pygame.Rect(depot[0], depot[1], 40, 35)
            if player_rect.colliderect(depot_rect):
                nitro_depots.remove(depot)
                nitro_available = True

        # Oil spot collision — random horizontal teleport
        for oil in oil_spots[:]:
            oil_rect = pygame.Rect(oil[0], oil[1], 60, 22)
            if player_rect.colliderect(oil_rect):
                oil_spots.remove(oil)
                player_x = random.randint(road_x, road_x + road_width - player_width)


    # --- Rendering ---
    screen.fill(SKY_BLUE)

    # Road surface
    pygame.draw.rect(screen, ROAD_GRAY, (road_x, 0, road_width, HEIGHT))

    # Oil spots (on road surface, under markings)
    for oil in oil_spots:
        draw_oil_spot(oil[0], oil[1])

    # Nitro depots
    for depot in nitro_depots:
        draw_nitro_depot(depot[0], depot[1])

    # Road centre line (draw then scroll)
    for line in road_lines:
        pygame.draw.rect(screen, ROAD_LINE, line)
    for line in road_lines:
        line.y += (speed + player_speed) * speed_mult
        if line.y > HEIGHT:
            line.y = -line_height

    # Cars
    draw_player_car(player_x, player_y, nitro_active)
    for obstacle in obstacles:
        draw_obstacle_car(obstacle[0], obstacle[1], obstacle[2])

    # HUD — left column
    screen.blit(font.render(f"Score: {score}", True, TEXT_COLOR), (20, 20))
    screen.blit(font.render(f"Dist:  {distance/1000:.2f} km", True, TEXT_COLOR), (20, 58))
    next_km = (difficulty_level + 1) * DISTANCE_PER_LEVEL / 1000
    screen.blit(font.render(f"Level: {difficulty_level}  (next {next_km:.0f} km)", True, TEXT_COLOR), (20, 96))
    if nitro_active:
        screen.blit(font.render(f"NITRO! {nitro_timer // 60 + 1}s", True, (255, 200, 0)), (20, 134))
    elif nitro_available:
        screen.blit(font.render("NITRO READY [N]", True, NITRO_GREEN), (20, 134))

    # Level-up banner
    if level_up_timer > 0:
        alpha = min(255, level_up_timer * 4)
        lu_surf = big_font.render(f"LEVEL {difficulty_level}!", True, (255, 220, 0))
        lu_surf.set_alpha(alpha)
        screen.blit(lu_surf, (WIDTH//2 - lu_surf.get_width()//2, HEIGHT//2 - 60))

    # HUD — right / centre
    lives_text = font.render(f"Lives: {lives}", True, TEXT_COLOR)
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 20, 20))
    speed_text = font.render(f"Speed: {int(player_speed * 10)}", True, TEXT_COLOR)
    screen.blit(speed_text, (WIDTH//2 - speed_text.get_width()//2, 20))

    # Controls hint
    ctrl = font.render("UP/DOWN: speed   LEFT/RIGHT: steer   N: nitro   ESC/Q: quit", True, TEXT_COLOR)
    screen.blit(ctrl, (WIDTH//2 - ctrl.get_width()//2, HEIGHT - 40))

    # Game over overlay
    if game_over:
        game_over_text = big_font.render("GAME OVER!", True, TEXT_COLOR)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
        final_text = font.render(f"Distance: {distance/1000:.2f} km", True, (180, 0, 0))
        screen.blit(final_text, (WIDTH//2 - final_text.get_width()//2, HEIGHT//2 + 5))
        restart_text = font.render("Press R to restart", True, TEXT_COLOR)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 55))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
