import pygame
import robots


zumo = robots.Zumo()
zumo.connect()

pygame.init()
screen = pygame.display.set_mode((640, 480))

black = (0, 0, 0)
white = (255, 255, 255)
grey = (192, 192, 192)
dark_grey = (48, 48, 48)
red = (255, 0, 0)

speed = 200

# Create board with gridlines
board = pygame.Surface((430, 430))
board.fill(dark_grey)
for i in range(1, 4):
    pygame.draw.rect(board, grey, (0, -7 + i*110, 430, 4))
    pygame.draw.rect(board, grey, (-7 + i*110, 0, 4, 430))

# Create object
object1 = pygame.Surface((100, 100))
object1.fill(dark_grey)
pygame.draw.circle(object1, red, (50, 50), 50)

x, y = (0, 0)
done = False
clock = pygame.time.Clock()

number_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3,
               pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
               pygame.K_8, pygame.K_9]

left_speed, right_speed = (0, 0)
while not done:

    # Clear the screen
    screen.fill(black)

    # Draw board
    screen.blit(board, (105, 20))

    # Draw objects
    screen.blit(object1, (105 + x*110, 20 + y*110))

    # Check if movement keys pressed

    keys = pygame.key.get_pressed()

    previous_speeds = (left_speed, right_speed)
    left_speed, right_speed = (0, 0)

    if keys[pygame.K_UP]:
        left_speed += speed
        right_speed += speed
    elif keys[pygame.K_DOWN]:
        left_speed -= speed
        right_speed -= speed

    if keys[pygame.K_LEFT]:
        left_speed -= speed
        right_speed += speed
    elif keys[pygame.K_RIGHT]:
        left_speed += speed
        right_speed -= speed

    if (left_speed, right_speed) != previous_speeds:
        zumo.set_speeds(left_speed, right_speed)
        print(left_speed, right_speed)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key in number_keys[0:5]:
                speed = number_keys.index(event.key) * 100
            elif event.key == pygame.K_y:
                zumo.led_yellow(1)
            elif event.key == pygame.K_g:
                zumo.led_green(1)
            elif event.key == pygame.K_SPACE:
                zumo.buzzer()
            elif event.key == pygame.K_ESCAPE:
                done = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_y:
                zumo.led_yellow(0)
            elif event.key == pygame.K_g:
                zumo.led_green(0)

    # Update the screen
    clock.tick()
    pygame.display.flip()

