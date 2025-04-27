#!/usr/bin/env python3
import os
import sys
import ctypes
import pygame
from ctypes import c_int, c_bool, Structure, POINTER, c_void_p
from enum import IntEnum
import time
import random

# Ensure we can find the C library
script_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.join(os.path.dirname(script_dir), "libsnake.so")

# Constants for the game
CELL_SIZE = 20
GRID_WIDTH = 20
GRID_HEIGHT = 15
WINDOW_WIDTH = CELL_SIZE * GRID_WIDTH
WINDOW_HEIGHT = CELL_SIZE * GRID_HEIGHT
FPS = 10  # Initial frames per second

# Nokia-style color palette
NOKIA_GREEN = (155, 188, 15)
NOKIA_DARK_GREEN = (139, 172, 15)
NOKIA_LIGHT_GREEN = (170, 204, 34)
NOKIA_DARKEST = (48, 56, 0)
NOKIA_BACKGROUND = (48, 98, 48)

# Game phases
class GamePhase:
    START_MENU = 0
    PLAYING = 1
    GAME_OVER = 2

# Directions from the C library (must match the enum in snake_core.h)
class Direction(IntEnum):
    UP = 0
    RIGHT = 1
    DOWN = 2
    LEFT = 3

# C struct definitions to match the C library
class Point(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]

class Food(Structure):
    _fields_ = [("position", Point), ("value", c_int)]

class SnakeSegment(Structure):
    _fields_ = [("position", Point)]

class GameState(Structure):
    _fields_ = [
        ("width", c_int),
        ("height", c_int),
        ("snake", SnakeSegment * 100),  # MAX_SNAKE_LENGTH from snake_core.h
        ("snake_length", c_int),
        ("direction", c_int),
        ("food", Food),
        ("score", c_int),
        ("game_over", c_bool)
    ]

# Load the C library
try:
    snake_lib = ctypes.CDLL(lib_path)
    print(f"Loaded C library from {lib_path}")
except Exception as e:
    print(f"Error loading C library: {e}")
    sys.exit(1)

# Define the C function prototypes
snake_lib.initialize_game.argtypes = [POINTER(GameState), c_int, c_int]
snake_lib.initialize_game.restype = None

snake_lib.update_game.argtypes = [POINTER(GameState)]
snake_lib.update_game.restype = c_bool

snake_lib.set_direction.argtypes = [POINTER(GameState), c_int]
snake_lib.set_direction.restype = None

snake_lib.check_self_collision.argtypes = [POINTER(GameState), Point]
snake_lib.check_self_collision.restype = c_bool

snake_lib.is_food_position.argtypes = [POINTER(GameState), Point]
snake_lib.is_food_position.restype = c_bool

snake_lib.spawn_food.argtypes = [POINTER(GameState)]
snake_lib.spawn_food.restype = None

snake_lib.get_snake_segment.argtypes = [POINTER(GameState), c_int]
snake_lib.get_snake_segment.restype = Point

snake_lib.get_food_position.argtypes = [POINTER(GameState)]
snake_lib.get_food_position.restype = Point

snake_lib.get_score.argtypes = [POINTER(GameState)]
snake_lib.get_score.restype = c_int

snake_lib.is_game_over.argtypes = [POINTER(GameState)]
snake_lib.is_game_over.restype = c_bool

snake_lib.reset_game.argtypes = [POINTER(GameState)]
snake_lib.reset_game.restype = None

class SnakeGame:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption("Nokia Snake")
        
        # Create the game window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Load font for text
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Initialize game state
        self.game_state = GameState()
        snake_lib.initialize_game(self.game_state, GRID_WIDTH, GRID_HEIGHT)
        
        # Game control variables
        self.running = True
        self.phase = GamePhase.START_MENU
        self.current_fps = FPS
        
        # Visual effect variables
        self.food_pulse = 0
        self.teleport_effect = None
        self.eat_effect = None
        
        # Sound effects (could be added here)
        
    def run(self):
        """Main game loop"""
        while self.running:
            if self.phase == GamePhase.START_MENU:
                self.handle_start_menu()
            elif self.phase == GamePhase.PLAYING:
                self.handle_gameplay()
            elif self.phase == GamePhase.GAME_OVER:
                self.handle_game_over()
            
            # Maintain frame rate
            self.clock.tick(self.current_fps)
            
    def handle_start_menu(self):
        """Handle the start menu phase"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self.phase = GamePhase.PLAYING
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Render start menu
        self.screen.fill(NOKIA_BACKGROUND)
        
        # Draw title
        title_text = self.font.render("NOKIA SNAKE", True, NOKIA_GREEN)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        self.screen.blit(title_text, title_rect)
        
        # Draw instruction
        instruction_text = self.small_font.render("Press SPACE to start", True, NOKIA_LIGHT_GREEN)
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*2//3))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Draw small snake icon
        self.draw_snake_icon()
        
        pygame.display.flip()
    
    def draw_snake_icon(self):
        """Draw a small snake icon for the menu"""
        snake_x, snake_y = WINDOW_WIDTH//2, WINDOW_HEIGHT//2
        
        # Draw snake body segments
        for i in range(5):
            pygame.draw.rect(self.screen, NOKIA_GREEN, 
                            (snake_x - i*10, snake_y, 8, 8))
        
        # Draw food
        pygame.draw.rect(self.screen, NOKIA_LIGHT_GREEN, 
                        (snake_x + 15, snake_y, 8, 8))
    
    def handle_gameplay(self):
        """Handle the main gameplay phase"""
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_key_press(event.key)
        
        # Update game state through C library
        updated = snake_lib.update_game(self.game_state)
        
        # Check if game is over
        if self.game_state.game_over:
            self.phase = GamePhase.GAME_OVER
        
        # Update speed based on score
        self.update_game_speed()
        
        # Update visual effects
        self.update_effects()
        
        # Render game
        self.render_game()
        
        pygame.display.flip()
    
    def handle_key_press(self, key):
        """Handle keyboard input for game control"""
        if key == pygame.K_UP or key == pygame.K_w:
            snake_lib.set_direction(self.game_state, Direction.UP)
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            snake_lib.set_direction(self.game_state, Direction.RIGHT)
        elif key == pygame.K_DOWN or key == pygame.K_s:
            snake_lib.set_direction(self.game_state, Direction.DOWN)
        elif key == pygame.K_LEFT or key == pygame.K_a:
            snake_lib.set_direction(self.game_state, Direction.LEFT)
        elif key == pygame.K_ESCAPE:
            self.phase = GamePhase.START_MENU
            snake_lib.reset_game(self.game_state)
    
    def update_game_speed(self):
        """Update game speed based on score"""
        base_fps = FPS
        score = snake_lib.get_score(self.game_state)
        # Increase speed as score increases
        self.current_fps = min(base_fps + (score // 30), base_fps * 2)
    
    def update_effects(self):
        """Update visual effects for food pulsing, teleportation, etc."""
        # Food pulsing effect
        self.food_pulse = (self.food_pulse + 0.1) % (2 * 3.14159)
        
        # Update teleport effect if active
        if self.teleport_effect is not None:
            self.teleport_effect[1] -= 1
            if self.teleport_effect[1] <= 0:
                self.teleport_effect = None
        
        # Update eat effect if active
        if self.eat_effect is not None:
            self.eat_effect[1] -= 1
            if self.eat_effect[1] <= 0:
                self.eat_effect = None
    
    def render_game(self):
        """Render the current game state to the screen"""
        # Fill the background
        self.screen.fill(NOKIA_DARKEST)
        
        # Draw border
        pygame.draw.rect(self.screen, NOKIA_GREEN, (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 2)
        
        # Draw food with pulsing effect
        food_pos = snake_lib.get_food_position(self.game_state)
        food_color = NOKIA_LIGHT_GREEN
        pulse_size = int(1 + 0.5 * abs(round(2 * (abs(self.food_pulse - 1.57) / 3.14 - 0.5))))
        pygame.draw.rect(self.screen, food_color, 
                        (food_pos.x * CELL_SIZE + pulse_size, 
                         food_pos.y * CELL_SIZE + pulse_size, 
                         CELL_SIZE - 2*pulse_size, 
                         CELL_SIZE - 2*pulse_size))
        
        # Draw snake
        snake_length = self.game_state.snake_length
        for i in range(snake_length):
            segment = snake_lib.get_snake_segment(self.game_state, i)
            
            # Determine color (head is lighter)
            if i == 0:  # Head
                color = NOKIA_LIGHT_GREEN
                # Draw eyes on the head
                eye_size = 2
                eye_offset = 6
                eye_color = NOKIA_DARKEST
                
                # Position eyes based on direction
                if self.game_state.direction == Direction.UP:
                    pygame.draw.rect(self.screen, eye_color, 
                                    (segment.x * CELL_SIZE + eye_offset - 2, 
                                     segment.y * CELL_SIZE + eye_offset - 3, 
                                     eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, 
                                    (segment.x * CELL_SIZE + CELL_SIZE - eye_offset, 
                                     segment.y * CELL_SIZE + eye_offset - 3, 
                                     eye_size, eye_size))
                elif self.game_state.direction == Direction.RIGHT:
                    pygame.draw.rect(self.screen, eye_color, 
                                    (segment.x * CELL_SIZE + CELL_SIZE - eye_offset + 3, 
                                     segment.y * CELL_SIZE + eye_offset - 2, 
                                     eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, 
                                    (segment.x * CELL_SIZE + CELL_SIZE - eye_offset + 3, 
                                     segment.y * CELL_SIZE + CELL_SIZE - eye_offset, 
                                     eye_size, eye_size))
                elif self.game_state.direction == Direction.DOWN:
                    pygame.draw.rect(self.screen, eye_color, 
                                    (segment.x * CELL_SIZE + eye_offset - 2, 
                                     segment.y * CELL_SIZE + CELL_SIZE - eye_offset + 3, 
                                     eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, 
                                    (segment.x * CELL_SIZE + CELL_SIZE - eye_offset, 
                                     segment.y * CELL_SIZE + CELL_SIZE - eye_offset + 3, 
                                     eye_size, eye_size))
                elif self.game_state.direction == Direction.LEFT:
                    pygame.draw.rect(self.screen, eye_color, 
                                    (segment.x * CELL_SIZE + eye_offset - 3, 
                                     segment.y * CELL_SIZE + eye_offset - 2, 
                                     eye_size, eye_size))
                    pygame.draw.rect(self.screen, eye_color, 
                                    (segment.x * CELL_SIZE + eye_offset - 3, 
                                     segment.y * CELL_SIZE + CELL_SIZE - eye_offset, 
                                     eye_size, eye_size))
            else:  # Body
                color = NOKIA_GREEN
                # Every few segments, use a slightly darker color for visual effect
                if i % 2 == 0:
                    color = NOKIA_DARK_GREEN
            
            # Draw the segment with a small gap to create segmented look
            gap = 1 if i > 0 else 0
            pygame.draw.rect(self.screen, color, 
                            (segment.x * CELL_SIZE + gap, 
                             segment.y * CELL_SIZE + gap, 
                             CELL_SIZE - 2*gap, 
                             CELL_SIZE - 2*gap))
        
        # Draw teleport effect if active
        if self.teleport_effect is not None:
            pos, time_left, color = self.teleport_effect
            radius = (10 - time_left) * 2
            pygame.draw.circle(self.screen, color, 
                              (pos.x * CELL_SIZE + CELL_SIZE//2, 
                               pos.y * CELL_SIZE + CELL_SIZE//2), 
                              radius, 1)
        
        # Draw eat effect if active
        if self.eat_effect is not None:
            pos, time_left, size = self.eat_effect
            color = NOKIA_LIGHT_GREEN
            pygame.draw.rect(self.screen, color, 
                            (pos.x * CELL_SIZE + (CELL_SIZE - size)//2, 
                             pos.y * CELL_SIZE + (CELL_SIZE - size)//2, 
                             size, size))
        
        # Draw score
        score_text = self.small_font.render(f"Score: {snake_lib.get_score(self.game_state)}", 
                                          True, NOKIA_GREEN)
        self.screen.blit(score_text, (10, 10))
        
        # Draw border indicators for teleportation (Nokia style wall markers)
        for i in range(0, GRID_WIDTH):
            pygame.draw.rect(self.screen, NOKIA_GREEN, 
                           (i * CELL_SIZE + CELL_SIZE//2 - 1, 0, 2, 2))
            pygame.draw.rect(self.screen, NOKIA_GREEN, 
                           (i * CELL_SIZE + CELL_SIZE//2 - 1, WINDOW_HEIGHT-2, 2, 2))
        for i in range(0, GRID_HEIGHT):
            pygame.draw.rect(self.screen, NOKIA_GREEN, 
                           (0, i * CELL_SIZE + CELL_SIZE//2 - 1, 2, 2))
            pygame.draw.rect(self.screen, NOKIA_GREEN, 
                           (WINDOW_WIDTH-2, i * CELL_SIZE + CELL_SIZE//2 - 1, 2, 2))
    
    def handle_game_over(self):
        """Handle the game over phase"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    # Reset game and go to start menu
                    snake_lib.reset_game(self.game_state)
                    self.phase = GamePhase.START_MENU
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Render game over screen
        # Keep the game state visible in the background
        self.render_game()
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((NOKIA_DARKEST[0], NOKIA_DARKEST[1], NOKIA_DARKEST[2], 200))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over text
        game_over_text = self.font.render("GAME OVER", True, NOKIA_GREEN)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw final score
        score = snake_lib.get_score(self.game_state)
        score_text = self.font.render(f"Score: {score}", True, NOKIA_LIGHT_GREEN)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # Draw restart instruction
        instruction_text = self.small_font.render("Press SPACE to play again", True, NOKIA_GREEN)
        instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*2//3))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Make the text blink at game over
        current_time = int(time.time() * 2)  # 2 blinks per second
        if current_time % 2 == 0:
            restart_text = self.small_font.render("RETRY", True, NOKIA_LIGHT_GREEN)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT*3//4))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
    
    def check_wall_teleport(self, prev_pos, new_pos):
        """Check if teleportation occurred and trigger effect if needed"""
        # Check if snake has teleported through walls
        if (abs(prev_pos.x - new_pos.x) > 1 or abs(prev_pos.y - new_pos.y) > 1):
            # Create teleport effect at both entry and exit points
            self.teleport_effect = [new_pos, 10, NOKIA_LIGHT_GREEN]
            return True
        return False
    
    def create_eat_effect(self, position):
        """Create visual effect when snake eats food"""
        self.eat_effect = [position, 5, CELL_SIZE * 1.5]  # Position, duration, size

# Main execution
if __name__ == "__main__":
    # Create and run the snake game
    game = SnakeGame()
    game.run()
    
    # Clean up when exiting
    pygame.quit()
    print("Game exited successfully.")
