import pygame
from models import Job

class ExecutionTimeAdjuster:
    def __init__(self):
        pygame.init()
        self.width, self.height = 400, 200
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Adjust Execution Time Coefficient")

        self.font = pygame.font.Font(None, 36)
        self.running = True

        # Slider properties
        self.slider_x = 50  # Slider bar position
        self.slider_y = 100
        self.slider_width = 300
        self.slider_height = 10

        self.knob_x = self.slider_x + (Job.execution_time_coefficient - 0.5) * (self.slider_width / 1.5)
        self.knob_radius = 10
        self.dragging = False

    def run(self):
        while self.running:
            self.screen.fill((30, 30, 30))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_mouse_on_knob(event.pos):
                        self.dragging = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                elif event.type == pygame.MOUSEMOTION and self.dragging:
                    self.update_knob_position(event.pos[0])

            # Draw slider
            pygame.draw.rect(self.screen, (200, 200, 200), (self.slider_x, self.slider_y, self.slider_width, self.slider_height))
            pygame.draw.circle(self.screen, (255, 0, 0), (int(self.knob_x), self.slider_y + self.slider_height // 2), self.knob_radius)

            # Display the current coefficient
            text = self.font.render(f"Coeff: {Job.execution_time_coefficient:.2f}", True, (255, 255, 255))
            self.screen.blit(text, (self.slider_x, self.slider_y - 40))

            pygame.display.flip()

        pygame.quit()

    def is_mouse_on_knob(self, pos):
        """Check if the mouse is on the slider knob."""
        return (self.knob_x - self.knob_radius <= pos[0] <= self.knob_x + self.knob_radius) and \
               (self.slider_y - self.knob_radius <= pos[1] <= self.slider_y + self.knob_radius)

    def update_knob_position(self, mouse_x):
        """Update the knob position based on mouse movement and update execution_time_coefficient."""
        self.knob_x = max(self.slider_x, min(mouse_x, self.slider_x + self.slider_width))

        # Normalize the knob position to a range of 0.5 to 2.0
        Job.execution_time_coefficient = 0.5 + ((self.knob_x - self.slider_x) / self.slider_width) * 1.5
