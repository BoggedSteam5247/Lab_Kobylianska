# encoding: utf-8
from __future__ import division
from nodebox.graphics import *
import pymunk
import pymunk.pyglet_util
import random
import math
import numpy as np

space = pymunk.Space()

def createBody(x, y, shape, *shapeArgs):
    body = pymunk.Body()
    body.position = x, y
    s = shape(body, *shapeArgs)
    s.mass = 1
    s.friction = 1
    space.add(body, s)
    return s  # shape!!!

s0 = createBody(300, 300, pymunk.Poly, ((-20, -5), (-20, 5), (20, 15), (20, -15)))
s0.score = 0
s3 = createBody(200, 300, pymunk.Poly, ((-20, -5), (-20, 5), (20, 15), (20, -15)))
s3.color = (0, 255, 0, 255)
s3.score = 0
s3.body.Q = [[0, 0], [0, 0], [0, 0]]
s3.body.action = 0  # 0 - залишати, 1 - змінювати (випадковий кут)
s1 = createBody(300, 200, pymunk.Circle, 10, (0, 0))
S2 = []
for i in range(1):
    s2 = createBody(350, 250, pymunk.Circle, 10, (0, 0))
    s2.color = (255, 0, 0, 255)
    S2.append(s2)

def getAngle(x, y, x1, y1):
    return math.atan2(y1 - y, x1 - x)

def getDist(x, y, x1, y1):
    return ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5

def inCircle(x, y, cx, cy, R):
    return (x - cx) ** 2 + (y - cy) ** 2 < R ** 2

def inSector(x, y, cx, cy, R, angle):
    if inCircle(x, y, cx, cy, R):
        angle = angle % (2 * math.pi)
        return (angle - 0.5 < getAngle(cx, cy, x, y) < angle + 0.5)
    return False

def get_random_angle():
    """Генерує випадковий кут від 0 до 2π."""
    return random.uniform(0, 2 * math.pi)

def update_q_table(b, state, reward):
    """Оновлює Q-таблицю на основі поточного стану та винагороди."""
    b.Q[state][b.action] += reward

def choose_action(b, state):
    """Вибирає дію на основі Q-таблиці з ймовірністю випадкового вибору."""
    act = b.Q[state][b.action]
    if random.random() < abs(1.0 / (act + 0.1)):  # Уникнути ділення на нуль
        b.action = random.choice([0, 1])  # Випадковий вибір
    else:
        b.action = np.argmax(b.Q[state])  # Вибір оптимальної дії

def strategy2(b=s3.body):
    """Стратегія робота з Q-learning для ухвалення рішень на основі вхідних даних з сенсорів."""
    v = 100
    a = b.angle
    b.velocity = v * math.cos(a), v * math.sin(a)
    x, y = b.position

    # Візуалізація сектора
    ellipse(x, y, 200, 200, stroke=Color(0.5))

    if canvas.frame % 10 == 0:  # Кожні 10 кадрів
        inS = inSector(s1.body.position[0], s1.body.position[1], x, y, 100, a)
        inS2 = inSector(S2[0].body.position[0], S2[0].body.position[1], x, y, 100, a)

        # Встановлення стану та винагороди
        if inS:
            state = 1
            reward = 1 if b.action == 0 else -1
        elif inS2:
            state = 2
            reward = -1 if b.action == 0 else 1
        else:
            state = 0
            reward = 0
        
        update_q_table(b, state, reward)  # Оновлення Q-таблиці
        print(state, b.action, b.Q)

        choose_action(b, state)  # Вибір дії

        if b.action:  # Якщо потрібно змінити напрямок
            b.angle = get_random_angle()  # Генерація випадкового кута

        if getDist(x, y, 350, 250) > 180:  # Запобігання виходу за межі
            b.angle = getAngle(x, y, 350, 250)

def scr(s, s0, s3, p=1):
    bx, by = s.body.position
    s0x, s0y = s0.body.position
    s3x, s3y = s3.body.position
    if not inCircle(bx, by, 350, 250, 180):
        if getDist(bx, by, s0x, s0y) < getDist(bx, by, s3x, s3y):
            s0.score = s0.score + p
        else:
            s3.score = s3.score + p
        s.body.position = random.randint(200, 400), random.randint(200, 300)

def score():
    """Визначає переможця."""
    scr(s1, s0, s3)
    for s in S2:
        scr(s, s0, s3, p=-1)

def manualControl():
    """Керування роботом з мишки або клавіатури."""
    v = 10  # швидкість
    b = s0.body
    a = b.angle
    x, y = b.position
    vx, vy = b.velocity
    if canvas.keys.char == "a":
        b.angle -= 0.1
    if canvas.keys.char == "d":
        b.angle += 0.1
    if canvas.keys.char == "w":
        b.velocity = vx + v * math.cos(a), vy + v * math.sin(a)
    if canvas.mouse.button == LEFT:
        b.angle = getAngle(x, y, *canvas.mouse.xy)
        b.velocity = vx + v * math.cos(a), vy + v * math.sin(a)

def simFriction():
    for s in [s0, s1, s3] + S2:
        s.body.velocity = s.body.velocity[0] * 0.9, s.body.velocity[1] * 0.9
        s.body.angular_velocity = s.body.angular_velocity * 0.9

draw_options = pymunk.pyglet_util.DrawOptions()

def draw(canvas):
    canvas.clear()
    fill(0, 0, 0, 1)
    text("%i %i" % (s0.score, s3.score), 20, 20)
    nofill()
    ellipse(350, 250, 350, 350, stroke=Color(0))
    manualControl()
    strategy2()
    score()
    simFriction()
    space.step(0.02)
    space.debug_draw(draw_options)

canvas.size = 700, 500
canvas.run(draw)
