import pygame
import random
import math


# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna gry
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Strzelanka Zombie")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)

gunshot_sound = pygame.mixer.Sound("gunshot.wav")
zombie_die_sound = pygame.mixer.Sound("zombie_die.wav")
gunshot_sound.set_volume(0.5)
zombie_die_sound.set_volume(0.5)

# Kolory
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRASS = (59,185,13)


class Button:
    def __init__(self, text, pos, size):
        self.rect = pygame.Rect(pos, size)
        self.text = text
        self.color = GREEN
        self.text_render = font.render(text, True, BLACK)
        self.text_rect = self.text_render.get_rect(center=self.rect.center)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        surface.blit(self.text_render, self.text_rect)

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Klasa gracza
class Player(pygame.sprite.Sprite):
    def __init__(self, weapon_type):
        super().__init__()
        self.images_right = [pygame.image.load(f"player{i}.png").convert_alpha() for i in range(1, 6)]
        self.images_left = [pygame.transform.flip(img, True, False) for img in self.images_right]
        self.image_index = 0
        self.image = self.images_right[self.image_index]
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        self.speed = 5
        self.health = 3
        self.facing_right = True
        self.last_hit_time = 0
        self.hit_cooldown = 1000
        self.weapon_type = weapon_type
        self.last_shot_time = 0
        self.shot_delay = 150 if weapon_type == "rifle" else 400
        self.is_hit = False

    def update(self):
        keys = pygame.key.get_pressed()
        moved = False
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            moved = True
        if keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            moved = True
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
            moved = True
        if keys[pygame.K_s]:
            self.rect.y += self.speed
            moved = True

        if moved:
            self.image_index = (self.image_index + 1) % len(self.images_right)
        if self.facing_right:
            self.image = self.images_right[self.image_index]
        else:
            self.image = self.images_left[self.image_index]

    def draw(self, surface):
        if self.is_hit:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                return
        surface.blit(self.image, self.rect)
#klasa zombie
class Zombie(pygame.sprite.Sprite):
    def __init__(self, existing_zombies):
        super().__init__()
        self.images_right = [pygame.image.load(f"zombie{i}.png").convert_alpha() for i in range(1, 5)]
        self.images_left = [pygame.transform.flip(img, True, False) for img in self.images_right]
        self.image_index = 0
        self.facing_right = True
        self.image = self.images_right[self.image_index]

        while True:
            side = random.choice(["top", "bottom", "left", "right"])
            if side == "top":
                pos = (random.randint(0, WIDTH), -40)
            elif side == "bottom":
                pos = (random.randint(0, WIDTH), HEIGHT + 40)
            elif side == "left":
                pos = (-40, random.randint(0, HEIGHT))
            else:
                pos = (WIDTH + 40, random.randint(0, HEIGHT))

            self.rect = self.image.get_rect(center=pos)
            if not any(self.rect.colliderect(z.rect) for z in existing_zombies):
                break

        self.speed = 3
        self.animation_timer = 0
        self.animation_speed = 150

    def update(self, player_pos):
        direction = pygame.math.Vector2(player_pos) - pygame.math.Vector2(self.rect.center)
        if direction.length() > 0:
            direction = direction.normalize()
            self.facing_right = direction.x > 0
        self.rect.center += direction * self.speed

        now = pygame.time.get_ticks()
        if now - self.animation_timer > self.animation_speed:
            self.image_index = (self.image_index + 1) % len(self.images_right)
            self.animation_timer = now

        self.image = self.images_right[self.image_index] if self.facing_right else self.images_left[self.image_index]

class Bullet(pygame.sprite.Sprite):
    def __init__(self, pos, direction):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=pos)
        self.velocity = pygame.math.Vector2(direction).normalize() * 10

    def update(self):
        self.rect.center += self.velocity

# Funkcja do zwiększania liczby zombie w czasie
zombie_spawn_timer = 0
zombie_spawn_interval = 1500
zombie_max_count = 15
zombie_spawn_growth = 4

def spawn_zombies(zombies_group, all_sprites, player, zombie_list):
    for _ in range(zombie_max_count - len(zombies_group)):
        zombie = Zombie(zombie_list)
        zombies_group.add(zombie)
        all_sprites.add(zombie)
        zombie_list.append(zombie)


def show_menu():
    start_button = Button("Start", (WIDTH // 2 - 75, HEIGHT // 2), (150, 50))
    tutorial_lines = [
        "Poruszaj się WSAD",
        "Strzelaj LPM",
        "Zdobadz 50 punktow",
        "Unikaj zombie!",
    ]
    while True:
        screen.fill(WHITE)
        title = font.render("Strzelanka Zombie", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        for i, line in enumerate(tutorial_lines):
            txt = font.render(line, True, BLACK)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 180 + i * 30))

        start_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if start_button.is_clicked(event):
                return

def choose_weapon():
    buttons = [
        Button("Pistolet", (150, 250), (150, 50)),
        Button("Karabin", (325, 250), (150, 50)),
        Button("Shotgun", (500, 250), (150, 50))
    ]
    while True:
        screen.fill(WHITE)
        title = font.render("Wybierz broń", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 150))

        for b in buttons:
            b.draw(screen)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            for i, b in enumerate(buttons):
                if b.is_clicked(event):
                    return ["pistol", "rifle", "shotgun"][i]

def show_game_over(score):
    restart_button = Button("Restart", (WIDTH // 2 - 160, HEIGHT // 2 + 40), (140, 50))
    quit_button = Button("Wyjście", (WIDTH // 2 + 20, HEIGHT // 2 + 40), (140, 50))
    while True:
        screen.fill(WHITE)
        text = font.render(f"Koniec gry! Wynik: {score}", True, BLACK)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))

        restart_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if restart_button.is_clicked(event):
                return True
            if quit_button.is_clicked(event):
                pygame.quit()
                exit()
def show_game_win(score):
    restart_button = Button("Restart", (WIDTH // 2 - 160, HEIGHT // 2 + 40), (140, 50))
    quit_button = Button("Wyjście", (WIDTH // 2 + 20, HEIGHT // 2 + 40), (140, 50))
    while True:
        screen.fill(WHITE)
        text = font.render(f"Wygrałeś! Wynik: {score}", True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))

        restart_button.draw(screen)
        quit_button.draw(screen)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if restart_button.is_clicked(event):
                return True
            if quit_button.is_clicked(event):
                pygame.quit()
                exit()

# Glowna petla gry

while True:
    show_menu()
    weapon = choose_weapon()

    player = Player(weapon)
    player_group = pygame.sprite.Group(player)
    zombie_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()

    running = True
    spawn_timer = 0
    score = 0

    while running:
        game_won = False
        clock.tick(60)
        current_time = pygame.time.get_ticks()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if player.weapon_type == "pistol" and mouse_pressed[0]:
            if current_time - player.last_shot_time > player.shot_delay:
                direction = pygame.mouse.get_pos() - pygame.math.Vector2(player.rect.center)
                bullet = Bullet(player.rect.center, direction)
                bullet_group.add(bullet)
                player.last_shot_time = current_time
                gunshot_sound.play()

        elif player.weapon_type == "rifle" and mouse_pressed[0]:
            if current_time - player.last_shot_time > player.shot_delay:
                direction = pygame.mouse.get_pos() - pygame.math.Vector2(player.rect.center)
                bullet = Bullet(player.rect.center, direction)
                bullet_group.add(bullet)
                player.last_shot_time = current_time
                gunshot_sound.play()

        elif player.weapon_type == "shotgun" and mouse_pressed[0]:
            if current_time - player.last_shot_time > player.shot_delay:
                base_dir = pygame.mouse.get_pos() - pygame.math.Vector2(player.rect.center)
                for angle in [-15, -5, 5, 15]:
                    rad = math.radians(angle)
                    rotated = base_dir.rotate_rad(rad)
                    bullet_group.add(Bullet(player.rect.center, rotated))
                player.last_shot_time = current_time
                gunshot_sound.play()

        spawn_timer += 1
        if spawn_timer > 60:
            zombie = Zombie(zombie_group)
            zombie_group.add(zombie)
            spawn_timer = 0

        player_group.update()
        bullet_group.update()
        for zombie in zombie_group:
            zombie.update(player.rect.center)

        for bullet in bullet_group.copy():
            if not screen.get_rect().colliderect(bullet.rect):
                bullet_group.remove(bullet)

        for bullet in bullet_group.copy():
            hit_zombies = pygame.sprite.spritecollide(bullet, zombie_group, True)
            if hit_zombies:
                bullet_group.remove(bullet)
                score += len(hit_zombies)
                zombie_die_sound.play()

        if pygame.sprite.spritecollide(player, zombie_group, False):
            if current_time - player.last_hit_time >= player.hit_cooldown:
                player.health -= 1
                player.last_hit_time = current_time
                player.is_hit = True
                if player.health <= 0:
                    running = False
        else:
            if current_time - player.last_hit_time >= player.hit_cooldown:
                player.is_hit = False

        if score >= 50:
            running = False
            game_won = True

        screen.fill(GRASS)
        bullet_group.draw(screen)
        zombie_group.draw(screen)
        player.draw(screen)

        score_text = font.render(f"Punkty: {score}", True, BLACK)
        health_text = font.render(f"Życie: {player.health}", True, RED)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 50))
        pygame.display.flip()

    if game_won:
        if not show_game_win(score):
            break
    else:
        if not show_game_over(score):
            break
