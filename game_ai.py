import pygame
import random
import os

# Инициализация Pygame
pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Поймай квадрат (AI)")

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)  # Цвет банана
GOLD = (255, 215, 0)    # Цвет монетки

# Параметры платформы
platform_width = 100
platform_height = 15
platform_y = HEIGHT - 50
platform_speed = 4  # Базовая скорость платформы
platforms = [{"x": WIDTH // 2 - platform_width // 2, "width": platform_width}]

# Параметры квадрата
square_size = 30
square_x = random.randint(0, WIDTH - square_size)
square_y = 0
square_speed = 4  # Базовая скорость падения квадрата

# Параметры банана и монетки
banana_x = random.randint(0, WIDTH - square_size)
banana_y = -random.randint(300, 700)
coin_x = random.randint(0, WIDTH - square_size)
coin_y = -random.randint(600, 1000)

# Очки и жизни
score = 0
extra_lives = 0  # Дополнительные жизни
score_file = "score.txt"

# Загружаем прошлый счет
if os.path.exists(score_file):
    with open(score_file, "r") as file:
        score = int(file.read())

# Игровые переменные
running = True
ai_mode = False  # AI режим (False = ручное управление, True = AI)
speed_up = False  # Флаг ускорения

# Основной цикл игры
while running:
    pygame.time.delay(20)
    screen.fill(WHITE)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s:  # Ускорение игры
                speed_up = not speed_up
            elif event.key == pygame.K_SPACE:  # Переключение AI режима
                ai_mode = not ai_mode

    # Ускорение
    if speed_up:
        platform_speed = 8
        square_speed = 8
    else:
        platform_speed = 4
        square_speed = 4

    # Управление платформами
    keys = pygame.key.get_pressed()
    if not ai_mode:
        if keys[pygame.K_LEFT]:
            for p in platforms:
                if p["x"] > 0:
                    p["x"] -= platform_speed
        if keys[pygame.K_RIGHT]:
            for p in platforms:
                if p["x"] < WIDTH - p["width"]:
                    p["x"] += platform_speed
    else:
        # AI управление: перемещаем платформу к квадрату
        for p in platforms:
            if square_x > p["x"] + p["width"] / 2:
                p["x"] += platform_speed
            elif square_x < p["x"] + p["width"] / 2:
                p["x"] -= platform_speed

    # Движение квадрата
    square_y += square_speed

    # Движение бонусов
    banana_y += 3  # Скорость падения банана
    coin_y += 3  # Скорость падения монетки

    # Проверка столкновения с платформами
    for p in platforms:
        if (p["x"] < square_x < p["x"] + p["width"]) and (square_y + square_size >= platform_y):
            square_y = 0
            square_x = random.randint(0, WIDTH - square_size)
            score += 1  # Увеличиваем счет
            with open(score_file, "w") as file:
                file.write(str(score))  # Сохраняем счет

    for p in platforms:
        if (p["x"] < banana_x < p["x"] + p["width"]) and (banana_y + square_size >= platform_y):
            banana_y = -random.randint(300, 700)  
            banana_x = random.randint(0, WIDTH - square_size)

            if len(platforms) == 1:
                platforms.append({"x": WIDTH // 4, "width": platform_width})

    for p in platforms:
        if (p["x"] < coin_x < p["x"] + p["width"]) and (coin_y + square_size >= platform_y):
            coin_y = -random.randint(600, 1000)  
            coin_x = random.randint(0, WIDTH - square_size)
            extra_lives += 1  

    if square_y > HEIGHT:
        if extra_lives > 0:
            extra_lives -= 1
            square_y = 0
            square_x = random.randint(0, WIDTH - square_size)
        else:
            print(f"Вы проиграли! Ваш счет: {score}")
            running = False

    # Отрисовка объектов
    for p in platforms:
        pygame.draw.rect(screen, BLUE, (p["x"], platform_y, p["width"], platform_height))  # Платформы

    pygame.draw.rect(screen, RED, (square_x, square_y, square_size, square_size))  # Квадрат
    pygame.draw.rect(screen, YELLOW, (banana_x, banana_y, square_size, square_size))  # Банан
    pygame.draw.rect(screen, GOLD, (coin_x, coin_y, square_size, square_size))  # Монетка

    # Отображение счета, режима и жизней
    font = pygame.font.Font(None, 36)
    text = font.render(f"Счет: {score} | {'AI' if ai_mode else 'Manual'} | Жизни: {extra_lives}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.update()

pygame.quit()
