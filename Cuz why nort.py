import pygame
import random

pygame.init()
pygame.mixer.init()

# ---------------- CONFIG ----------------
WIDTH, HEIGHT = 800, 500
PLAYER_SPEED = 5.5

BASE_POLICE_SPEED = 1.0
SPEED_INCREMENT = 0.125
MAX_POLICE_SPEED = 5.0

COIN_SIZE = 14
SIREN_DISTANCE = 140
JAIL_MARGIN = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Thief vs Police Game")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 22)
big_font = pygame.font.SysFont(None, 42)

# ---------------- AUDIO ----------------
pygame.mixer.music.load("C:\\Users\\admin\\Desktop\\Sourabh\\Python\\phonk.mp3")
siren = pygame.mixer.Sound("C:\\Users\\admin\\Downloads\\Police Siren Sound Effect.mp3")

# ---------------- JAIL RECT ----------------
JAIL_RECT = pygame.Rect(
    JAIL_MARGIN,
    JAIL_MARGIN,
    WIDTH - 2 * JAIL_MARGIN,
    HEIGHT - 2 * JAIL_MARGIN
)

# ---------------- HITBOX FUNCTION ----------------
def get_hitbox(rect):
    return pygame.Rect(
        rect.x + 8,
        rect.y + 6,
        rect.width - 16,
        rect.height - 14
    )

# ---------------- AVATARS ----------------
def create_thief():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    pygame.draw.circle(surf, (0, 0, 0), (20, 10), 8)
    pygame.draw.rect(surf, (255, 255, 255), (12, 8, 16, 4))
    pygame.draw.rect(surf, (40, 40, 40), (12, 18, 16, 20))
    pygame.draw.rect(surf, (70, 70, 70), (12, 38, 6, 18))
    pygame.draw.rect(surf, (70, 70, 70), (22, 38, 6, 18))
    return surf

def create_police():
    surf = pygame.Surface((40, 60), pygame.SRCALPHA)
    pygame.draw.circle(surf, (255, 220, 180), (20, 10), 8)
    pygame.draw.rect(surf, (0, 0, 0), (8, 0, 24, 6))
    pygame.draw.rect(surf, (0, 0, 180), (10, 18, 20, 22))
    pygame.draw.rect(surf, (0, 0, 120), (10, 40, 7, 18))
    pygame.draw.rect(surf, (0, 0, 120), (23, 40, 7, 18))
    return surf

thief_img = create_thief()
police_img = create_police()

# ---------------- COIN ----------------
def spawn_coin():
    return pygame.Rect(
        random.randint(JAIL_MARGIN + 20, WIDTH - JAIL_MARGIN - 20),
        random.randint(JAIL_MARGIN + 20, HEIGHT - JAIL_MARGIN - 20),
        COIN_SIZE,
        COIN_SIZE
    )

# ---------------- RESET ----------------
def reset_game():
    global thief_rect, police_rect, coin_rect
    global score, game_over, game_over_reason, siren_playing

    thief_rect = thief_img.get_rect(center=(400, 250))
    police_rect = police_img.get_rect(center=(120, 120))
    coin_rect = spawn_coin()

    score = 0
    game_over = False
    game_over_reason = ""
    siren_playing = False

    pygame.mixer.music.play(-1)
    siren.stop()

# ---------------- INIT ----------------
score = 0
game_over = False
game_over_reason = ""
siren_playing = False

reset_game()

# ---------------- GAME LOOP ----------------
running = True
while running:
    clock.tick(60)
    screen.fill((210, 210, 210))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_q, pygame.K_ESCAPE):
                running = False
            if event.key == pygame.K_r and game_over:
                reset_game()

    # -------- DRAW JAIL --------
    pygame.draw.rect(screen, (0, 0, 0), JAIL_RECT, 3)
    for x in range(JAIL_MARGIN + 20, WIDTH - JAIL_MARGIN, 30):
        pygame.draw.line(screen, (0, 0, 0), (x, JAIL_MARGIN), (x, HEIGHT - JAIL_MARGIN))

    screen.blit(font.render("JAIL", True, (0, 0, 0)),
                (WIDTH // 2 - 20, JAIL_MARGIN - 30))

    if not game_over:
        # -------- PLAYER MOVE --------
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            thief_rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            thief_rect.y += PLAYER_SPEED
        if keys[pygame.K_LEFT]:
            thief_rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            thief_rect.x += PLAYER_SPEED

        thief_hitbox = get_hitbox(thief_rect)
        police_hitbox = get_hitbox(police_rect)

        # -------- POLICE CHASE --------
        direction = pygame.Vector2(thief_rect.center) - pygame.Vector2(police_rect.center)
        distance = direction.length()

        if distance < SIREN_DISTANCE:
            if not siren_playing:
                siren.play(-1)
                siren_playing = True
        else:
            siren.stop()
            siren_playing = False

        if distance != 0:
            speed = BASE_POLICE_SPEED + score * SPEED_INCREMENT
            speed = min(speed, MAX_POLICE_SPEED)
            police_rect.center += direction.normalize() * speed

        # -------- COIN COLLISION --------
        if thief_hitbox.colliderect(coin_rect):
            score += 1
            coin_rect = spawn_coin()

        # -------- JAIL COLLISION --------
        if not JAIL_RECT.contains(thief_hitbox):
            game_over = True
            game_over_reason = "OUT OF JAIL"
            pygame.mixer.music.stop()
            siren.stop()

        # -------- POLICE COLLISION --------
        elif thief_hitbox.colliderect(police_hitbox):
            game_over = True
            game_over_reason = "CAUGHT BY POLICE"
            pygame.mixer.music.stop()
            siren.stop()

    # -------- DRAW OBJECTS --------
    pygame.draw.rect(screen, (255, 215, 0), coin_rect)
    screen.blit(thief_img, thief_rect)
    screen.blit(police_img, police_rect)

    screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (10, 10))

    if game_over:
        screen.blit(big_font.render("GAME OVER", True, (200, 0, 0)),
                    (WIDTH // 2 - 110, HEIGHT // 2 - 60))
        screen.blit(font.render(game_over_reason, True, (0, 0, 0)),
                    (WIDTH // 2 - 90, HEIGHT // 2 - 20))
        screen.blit(font.render("Press R to Restart | Q to Quit", True, (0, 0, 0)),
                    (WIDTH // 2 - 140, HEIGHT // 2 + 20))

    pygame.display.flip()

pygame.quit()
