import pygame
import random
import math
import os
from pygame import mixer

# Инициализация Pygame
pygame.init()
mixer.init()

# Создание окна
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Survival Game")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Загрузка изображений
def load_image(name, scale=1):
    try:
        image = pygame.image.load(os.path.join('assets', name))
        if scale != 1:
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] * scale)))
        return image
    except:
        # Если изображение не найдено, создаем временный спрайт
        surf = pygame.Surface((30, 30))
        surf.fill(BLUE if 'player' in name else RED if 'enemy' in name else GREEN)
        return surf

# Загрузка звуков
def load_sound(name):
    try:
        return mixer.Sound(os.path.join('assets', name))
    except:
        return None

# Класс игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = load_image('player.png', 0.5)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.speed = 5
        self.health = 100
        self.hunger = 100
        self.thirst = 100
        self.energy = 100
        self.score = 0
        self.inventory = {'food': 0, 'water': 0, 'wood': 0}
        self.last_shot = 0
        self.shoot_cooldown = 500  # миллисекунды
        self.bullets = pygame.sprite.Group()
        self.hit_sound = load_sound('hit.wav')
        self.collect_sound = load_sound('collect.wav')

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed
        if keys[pygame.K_SPACE]:
            self.shoot()

        # Ограничение движения по границам экрана
        self.rect.clamp_ip(screen.get_rect())

        # Уменьшение показателей со временем
        self.hunger = max(0, self.hunger - 0.01)
        self.thirst = max(0, self.thirst - 0.02)
        self.energy = max(0, self.energy - 0.005)

        # Обновление пуль
        self.bullets.update()

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            bullet = Bullet(self.rect.centerx, self.rect.centery)
            self.bullets.add(bullet)
            self.last_shot = current_time

    def collect_resource(self, resource):
        if self.collect_sound:
            self.collect_sound.play()
        self.inventory[resource.type] += 1
        if resource.type == 'food':
            self.hunger = min(100, self.hunger + 20)
        elif resource.type == 'water':
            self.thirst = min(100, self.thirst + 20)
        self.score += 10

# Класс пули
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 5))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 10
        self.direction = pygame.math.Vector2(1, 0)  # Направление по умолчанию

    def update(self):
        self.rect.x += self.direction.x * self.speed
        if self.rect.right < 0 or self.rect.left > WINDOW_WIDTH:
            self.kill()

# Класс врага
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = load_image('enemy.png', 0.4)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOW_WIDTH)
        self.rect.y = random.randint(0, WINDOW_HEIGHT)
        self.speed = 2
        self.health = 30
        self.hit_sound = load_sound('enemy_hit.wav')

    def update(self, player):
        # Движение к игроку
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx = dx / dist
            dy = dy / dist
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        # Поворот спрайта в сторону игрока
        angle = math.degrees(math.atan2(-dy, dx))
        self.image = pygame.transform.rotate(self.original_image, angle - 90)
        self.rect = self.image.get_rect(center=self.rect.center)

    def take_damage(self):
        self.health -= 10
        if self.hit_sound:
            self.hit_sound.play()
        if self.health <= 0:
            self.kill()
            return True
        return False

# Класс ресурса
class Resource(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.type = random.choice(['food', 'water', 'wood'])
        if self.type == 'food':
            self.image = load_image('food.png', 0.3)
        elif self.type == 'water':
            self.image = load_image('water.png', 0.3)
        else:
            self.image = load_image('wood.png', 0.3)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOW_WIDTH)
        self.rect.y = random.randint(0, WINDOW_HEIGHT)
        self.animation_offset = 0
        self.animation_speed = 0.1

    def update(self):
        # Анимация парения
        self.animation_offset += self.animation_speed
        self.rect.y += math.sin(self.animation_offset) * 0.5

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
resources = pygame.sprite.Group()

# Создание игрока
player = Player()
all_sprites.add(player)

# Создание врагов
for i in range(5):
    enemy = Enemy()
    all_sprites.add(enemy)
    enemies.add(enemy)

# Создание ресурсов
for i in range(10):
    resource = Resource()
    all_sprites.add(resource)
    resources.add(resource)

# Игровой цикл
clock = pygame.time.Clock()
running = True
font = pygame.font.Font(None, 36)
game_over = False

# Фон
background = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
background.fill((50, 50, 50))
for i in range(100):
    x = random.randint(0, WINDOW_WIDTH)
    y = random.randint(0, WINDOW_HEIGHT)
    pygame.draw.circle(background, (100, 100, 100), (x, y), 1)

while running:
    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                # Перезапуск игры
                game_over = False
                player.health = 100
                player.hunger = 100
                player.thirst = 100
                player.energy = 100
                player.score = 0
                player.inventory = {'food': 0, 'water': 0, 'wood': 0}
                for enemy in enemies:
                    enemy.kill()
                for resource in resources:
                    resource.kill()
                for i in range(5):
                    enemy = Enemy()
                    all_sprites.add(enemy)
                    enemies.add(enemy)
                for i in range(10):
                    resource = Resource()
                    all_sprites.add(resource)
                    resources.add(resource)

    if not game_over:
        # Обновление
        player.update()
        for enemy in enemies:
            enemy.update(player)
        for resource in resources:
            resource.update()

        # Проверка столкновений с ресурсами
        hits = pygame.sprite.spritecollide(player, resources, True)
        for hit in hits:
            player.collect_resource(hit)
            # Создание нового ресурса
            resource = Resource()
            all_sprites.add(resource)
            resources.add(resource)

        # Проверка столкновений пуль с врагами
        for bullet in player.bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, False)
            for enemy in hits:
                if enemy.take_damage():
                    player.score += 50
                bullet.kill()

        # Проверка столкновений с врагами
        hits = pygame.sprite.spritecollide(player, enemies, False)
        if hits:
            player.health -= 1
            if player.health <= 0:
                game_over = True

        # Проверка условий проигрыша
        if player.hunger <= 0 or player.thirst <= 0 or player.energy <= 0:
            game_over = True

    # Отрисовка
    screen.blit(background, (0, 0))
    all_sprites.draw(screen)
    player.bullets.draw(screen)

    # Отображение статистики
    health_text = font.render(f'Health: {int(player.health)}', True, WHITE)
    hunger_text = font.render(f'Hunger: {int(player.hunger)}', True, WHITE)
    thirst_text = font.render(f'Thirst: {int(player.thirst)}', True, WHITE)
    energy_text = font.render(f'Energy: {int(player.energy)}', True, WHITE)
    score_text = font.render(f'Score: {player.score}', True, WHITE)
    inventory_text = font.render(f'Food: {player.inventory["food"]} Water: {player.inventory["water"]} Wood: {player.inventory["wood"]}', True, WHITE)

    screen.blit(health_text, (10, 10))
    screen.blit(hunger_text, (10, 50))
    screen.blit(thirst_text, (10, 90))
    screen.blit(energy_text, (10, 130))
    screen.blit(score_text, (10, 170))
    screen.blit(inventory_text, (10, 210))

    if game_over:
        game_over_text = font.render('GAME OVER! Press R to restart', True, RED)
        screen.blit(game_over_text, (WINDOW_WIDTH//2 - 200, WINDOW_HEIGHT//2))

    pygame.display.flip()
    clock.tick(60)

# Завершение игры
pygame.quit() 