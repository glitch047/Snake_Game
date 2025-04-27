# Makefile for Snake Game C library
# Compiles the snake_core.c into a shared library (libsnake.so)

# Compiler and compiler flags
CC = gcc
CFLAGS = -Wall -Wextra -g -O2 -fPIC

# Target shared library
TARGET = libsnake.so

# Source and object files
SRC = snake_core.c
OBJ = $(SRC:.c=.o)

# Default target
all: $(TARGET)

# Rule to create the shared library
$(TARGET): $(OBJ)
	$(CC) -shared -o $@ $^ $(CFLAGS)
	@echo "Shared library created: $(TARGET)"

# Rule to compile source files to object files
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

# Clean target
clean:
	rm -f $(OBJ) $(TARGET)
	@echo "Cleaned build files"

# Install target (copies to parent directory for Python to use)
install: $(TARGET)
	cp $(TARGET) ../
	@echo "Installed $(TARGET) to parent directory"

# Phony targets (targets that don't create files with these names)
.PHONY: all clean install

