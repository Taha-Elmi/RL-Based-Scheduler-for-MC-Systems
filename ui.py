import pygame
from matplotlib import pyplot as plt
from matplotlib import animation as animation
from models import Job, System
import time
import io


class ExecutionTimeAdjuster:
    def __init__(self, system):
        pygame.init()
        self.system = system
        self.graph_visualizer = GraphVisualizer(system)  # Create GraphVisualizer once

        self.width, self.height = 800, 700  # Increased height for better layout
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("System Monitoring")

        self.font = pygame.font.Font(None, 24)
        self.running = True

        # Slider properties (Placed at the bottom)
        self.slider_width = 500  # Wider slider for better precision
        self.slider_height = 10
        self.slider_x = (self.width - self.slider_width) // 2  # Center horizontally
        self.slider_y = 600  # Positioned at the bottom

        self.knob_x = self.slider_x + (Job.execution_time_coefficient - 0.5) * (self.slider_width / 1.5)
        self.knob_radius = 12  # Slightly larger for better visibility
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

            # Update and draw Matplotlib graph inside Pygame
            graph_image = self.graph_visualizer.update_plot()
            self.screen.blit(graph_image, (50, 50))  # Display graph at the top

            # Draw slider (placed below the graph)
            pygame.draw.rect(self.screen, (200, 200, 200),
                             (self.slider_x, self.slider_y, self.slider_width, self.slider_height))
            pygame.draw.circle(self.screen, (255, 0, 0),
                               (int(self.knob_x), self.slider_y + self.slider_height // 2), self.knob_radius)

            # Display the current coefficient (above the slider)
            text = self.font.render(f"Execution Coeff: {Job.execution_time_coefficient:.2f}", True, (255, 255, 255))
            self.screen.blit(text, (self.slider_x + self.slider_width // 3, self.slider_y - 30))

            pygame.display.flip()
            time.sleep(0.5)  # Prevents high CPU usage

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



class GraphVisualizer:
    def __init__(self, system):
        self.system = system
        self.fig, self.ax = plt.subplots()
        self.line1, = self.ax.plot([], [], label="Mode Changes", color="blue", marker="o")
        self.line2, = self.ax.plot([], [], label="Dropped Jobs", color="red", marker="s")

        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Count")
        self.ax.set_title("System Performance Over Time")
        self.ax.legend()
        self.ax.grid(True)

    def update_plot(self):
        """Update Matplotlib graph and return as Pygame image."""
        if len(self.system.time_history) > 0:
            self.line1.set_data(self.system.time_history, self.system.mode_change_history)
            self.line2.set_data(self.system.time_history, self.system.dropped_jobs_history)
            self.ax.relim()
            self.ax.autoscale_view()

        plt.draw()

        # Convert Matplotlib figure to Pygame image
        img_buffer = io.BytesIO()
        self.fig.savefig(img_buffer, format="PNG")
        img_buffer.seek(0)
        return pygame.image.load(img_buffer, "PNG")  # Convert buffer to Pygame image
