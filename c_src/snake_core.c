#include "snake_core.h"
#include <stdlib.h>
#include <time.h>
#include <string.h>

// Initialize the random number generator
static void init_random() {
    static bool initialized = false;
    if (!initialized) {
        srand((unsigned int)time(NULL));
        initialized = true;
    }
}

// Helper function to get a random number within a range
static int get_random(int min, int max) {
    return min + rand() % (max - min + 1);
}

// Initialize the game state with default values
void initialize_game(GameState* game, int width, int height) {
    if (!game) return;
    
    init_random();
    
    game->width = width;
    game->height = height;
    game->snake_length = INITIAL_SNAKE_LENGTH;
    game->direction = RIGHT;
    game->score = 0;
    game->game_over = false;
    
    // Place snake in the middle of the screen
    int start_x = width / 2;
    int start_y = height / 2;
    
    // Initialize snake segments
    for (int i = 0; i < game->snake_length; i++) {
        game->snake[i].position.x = start_x - i;
        game->snake[i].position.y = start_y;
    }
    
    // Spawn initial food
    spawn_food(game);
}

// Generate a new point in the given direction from the current position
static Point get_new_position(Point current, Direction dir, int width, int height) {
    Point new_pos = current;
    
    switch (dir) {
        case UP:
            new_pos.y = (new_pos.y - 1 + height) % height;  // Wrap around top/bottom
            break;
        case RIGHT:
            new_pos.x = (new_pos.x + 1) % width;  // Wrap around right edge
            break;
        case DOWN:
            new_pos.y = (new_pos.y + 1) % height;  // Wrap around bottom
            break;
        case LEFT:
            new_pos.x = (new_pos.x - 1 + width) % width;  // Wrap around left edge
            break;
    }
    
    return new_pos;
}

// Process a single game tick, moving the snake and handling collisions
bool update_game(GameState* game) {
    if (!game || game->game_over) return false;
    
    // Calculate new head position
    Point new_head = get_new_position(
        game->snake[0].position,
        game->direction,
        game->width,
        game->height
    );
    
    // Check for collision with self
    if (check_self_collision(game, new_head)) {
        game->game_over = true;
        return true;
    }
    
    // Check if snake eats food
    bool eaten_food = is_food_position(game, new_head);
    
    // If snake eats food, increase length and spawn new food
    if (eaten_food) {
        if (game->snake_length < MAX_SNAKE_LENGTH) {
            game->snake_length++;
        }
        game->score += game->food.value;
        spawn_food(game);
    }
    
    // Move snake body (from tail to head)
    for (int i = game->snake_length - 1; i > 0; i--) {
        game->snake[i].position = game->snake[i - 1].position;
    }
    
    // Update head position
    game->snake[0].position = new_head;
    
    return true;
}

// Change the snake's direction (prevents 180-degree turns)
void set_direction(GameState* game, Direction new_direction) {
    if (!game) return;
    
    // Prevent 180-degree turns (can't go directly opposite current direction)
    if ((game->direction == UP && new_direction == DOWN) ||
        (game->direction == DOWN && new_direction == UP) ||
        (game->direction == LEFT && new_direction == RIGHT) ||
        (game->direction == RIGHT && new_direction == LEFT)) {
        return;
    }
    
    game->direction = new_direction;
}

// Check for collision with snake's own body
bool check_self_collision(GameState* game, Point position) {
    if (!game) return false;
    
    // Start from index 1 (skip head) to check if new position collides with body
    for (int i = 1; i < game->snake_length; i++) {
        if (game->snake[i].position.x == position.x && 
            game->snake[i].position.y == position.y) {
            return true;
        }
    }
    
    return false;
}

// Check if position is on food
bool is_food_position(GameState* game, Point position) {
    if (!game) return false;
    
    return (game->food.position.x == position.x && 
            game->food.position.y == position.y);
}

// Generate new food at a random valid position (not on snake)
void spawn_food(GameState* game) {
    if (!game) return;
    
    // Maximum attempts to find a valid position
    const int MAX_ATTEMPTS = 100;
    Point position;
    bool valid_position = false;
    int attempts = 0;
    
    while (!valid_position && attempts < MAX_ATTEMPTS) {
        position.x = get_random(0, game->width - 1);
        position.y = get_random(0, game->height - 1);
        
        valid_position = true;
        
        // Check if position overlaps with any snake segment
        for (int i = 0; i < game->snake_length; i++) {
            if (game->snake[i].position.x == position.x && 
                game->snake[i].position.y == position.y) {
                valid_position = false;
                break;
            }
        }
        
        attempts++;
    }
    
    // If we failed to find a valid position after max attempts, find any free cell
    if (!valid_position) {
        for (int y = 0; y < game->height; y++) {
            for (int x = 0; x < game->width; x++) {
                position.x = x;
                position.y = y;
                
                valid_position = true;
                for (int i = 0; i < game->snake_length; i++) {
                    if (game->snake[i].position.x == x && 
                        game->snake[i].position.y == y) {
                        valid_position = false;
                        break;
                    }
                }
                
                if (valid_position) {
                    game->food.position = position;
                    game->food.value = 10;  // Default food value
                    return;
                }
            }
        }
    } else {
        game->food.position = position;
        game->food.value = 10;  // Default food value
    }
}

// Get snake segment at index
Point get_snake_segment(GameState* game, int index) {
    Point empty = {-1, -1};
    if (!game || index < 0 || index >= game->snake_length) return empty;
    
    return game->snake[index].position;
}

// Get food position
Point get_food_position(GameState* game) {
    Point empty = {-1, -1};
    if (!game) return empty;
    
    return game->food.position;
}

// Get current score
int get_score(GameState* game) {
    if (!game) return 0;
    
    return game->score;
}

// Check if game is over
bool is_game_over(GameState* game) {
    if (!game) return true;
    
    return game->game_over;
}

// Reset the game to initial state
void reset_game(GameState* game) {
    if (!game) return;
    
    int width = game->width;
    int height = game->height;
    
    // Re-initialize the game with the same dimensions
    initialize_game(game, width, height);
}

