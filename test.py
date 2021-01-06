import pygame


pygame.init()
display = pygame.display.set_mode((640, 480))
clock = pygame.time.Clock()
GRAY = pygame.Color('gray12')
display_width, display_height = display.get_size()
x = display_width * 0.45
y = display_height * 0.8
x_change = 0
accel_x = 0
max_speed = 6

crashed = False
while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
                crashed = True
        elif event.type == pygame.KEYDOWN:
            # Set the acceleration value.
            if event.key == pygame.K_LEFT:
                accel_x = -.2
            elif event.key == pygame.K_RIGHT:
                accel_x = .2
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                accel_x = 0

    x_change += accel_x  # Accelerate.
    if abs(x_change) >= max_speed:  # If max_speed is exceeded.
        # Normalize the x_change and multiply it with the max_speed.
        x_change = x_change/abs(x_change) * max_speed

    # Decelerate if no key is pressed.
    if accel_x == 0:
        x_change *= 0.92
    print(x_change)
    x += x_change  # Move the object.

    display.fill(GRAY)
    pygame.draw.rect(display, (0, 120, 250), (x, y, 20, 40))

    pygame.display.update()
    clock.tick(60)

pygame.quit()