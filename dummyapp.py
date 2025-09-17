# dummyapp.py
import tkinter as tk
from tkinter import messagebox
import requests
import pygame
import random

API_URL = "https://login-fastapi-qalf.onrender.com"

# ---------------- Game 1: Bouncing Ball ----------------
def bouncing_ball():
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Bouncing Ball")
    clock = pygame.time.Clock()
    ball = pygame.Rect(300, 200, 20, 20)
    dx, dy = 4, 4

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        ball.x += dx
        ball.y += dy

        if ball.left <= 0 or ball.right >= 600:
            dx = -dx
        if ball.top <= 0 or ball.bottom >= 400:
            dy = -dy

        screen.fill((30, 30, 30))
        pygame.draw.ellipse(screen, (0, 200, 200), ball)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

# ---------------- Game 2: Snake ----------------
def snake_game(role):
    if role != "admin":
        messagebox.showwarning("Access Denied", "You do not have permission to play Snake!")
        return

    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()
    snake = [(100, 100)]
    direction = (20, 0)
    food = (200, 200)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 20):
                    direction = (0, -20)
                elif event.key == pygame.K_DOWN and direction != (0, -20):
                    direction = (0, 20)
                elif event.key == pygame.K_LEFT and direction != (20, 0):
                    direction = (-20, 0)
                elif event.key == pygame.K_RIGHT and direction != (-20, 0):
                    direction = (20, 0)

        new_head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
        snake = [new_head] + snake[:-1]

        if new_head == food:
            snake.append(snake[-1])
            food = (random.randrange(0, 600, 20), random.randrange(0, 400, 20))

        if new_head[0] < 0 or new_head[0] >= 600 or new_head[1] < 0 or new_head[1] >= 400 or new_head in snake[1:]:
            running = False

        screen.fill((0, 0, 0))
        for s in snake:
            pygame.draw.rect(screen, (0, 255, 0), (*s, 20, 20))
        pygame.draw.rect(screen, (255, 0, 0), (*food, 20, 20))
        pygame.display.flip()
        clock.tick(10)

    pygame.quit()

# ---------------- Main Dummy App ----------------
def run_app(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/me", headers=headers)
    user = response.json()
    role = user["role"]

    app = tk.Tk()
    app.title(f"Dummy App - {role.capitalize()} Access")

    tk.Label(app, text=f"Welcome {user['username']}! Role: {role}", font=("Arial", 14)).pack(pady=10)

    # Game 1 available to all
    tk.Button(app, text="Play Bouncing Ball (All Users)", command=bouncing_ball).pack(pady=5)

    # Game 2 restricted to admin
    tk.Button(app, text="Play Snake (Admin Only)", command=lambda: snake_game(role)).pack(pady=5)

    app.mainloop()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        token = sys.argv[1]
        run_app(token)
    else:
        print("No token provided. Please run via main.py after login.")

