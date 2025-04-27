#ifndef SNAKE_CORE_H
#define SNAKE_CORE_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>

// Constants for game dimensions and settings
#define MAX_SNAKE_LENGTH 100  // Maximum length the snake can grow to
#define INITIAL_SNAKE_LENGTH 3  // Starting length of snake

// Directions for snake movement
typedef enum {
    UP = 0,
    RIGHT = 1,
    DOWN = 2,
    LEFT = 3
} Direction;

// Structure to represent a point/position in the game grid
typedef struct {
    int x;
    int y;
} Point;

// Structure to represent a snake segment
typedef struct {
    Point position;
} SnakeSegment;

// Structure to represent food
typedef struct {
    Point position;
    int value;  // Score value of the food
} Food;

// Structure to hold the entire game state
typedef struct {
    int width;          // Width of game board
    int height;         // Height of game board
    SnakeSegment snake[MAX_SNAKE_LENGTH];  // Array of snake segments
    int snake_length;   // Current length of the snake
    Direction direction;  // Current direction of movement
    Food food;          // Current food item
    int score;          // Current score
    bool game_over;     // Game over flag
} GameState;

// Function declarations

// Initialize the game state with default values
void initialize_game(GameState* game, int width, int height);

// Process a single game tick, moving the snake and handling collisions
// Returns true if game state changed, false otherwise
bool update_game(GameState* game);

// Change the snake's direction
void set_direction(GameState* game, Direction new_direction);

// Check if the movement would cause a collision
// Returns true if collision detected, false otherwise
bool check_collision(GameState* game, Point position);

// Check for collision with snake's own body
// Returns true if collision detected, false otherwise
bool check_self_collision(GameState* game, Point position);

// Check if position is on food
// Returns true if position matches food position
bool is_food_position(GameState* game, Point position);

// Generate new food at a random valid position
void spawn_food(GameState* game);

// Get snake segment at index
Point get_snake_segment(GameState* game, int index);

// Get food position
Point get_food_position(GameState* game);

// Get current score
int get_score(GameState* game);

// Check if game is over
bool is_game_over(GameState* game);

// Reset the game to initial state
void reset_game(GameState* game);

#ifdef __cplusplus
}
#endif

#endif // SNAKE_CORE_H

