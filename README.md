# Maze Generator and Solver

## 📌 Overview

This project generates and solves a rectangular maze using stack-based algorithms and visualizes the process using Pygame.

---

## 🧠 Maze Generation (DFS "Mouse Algorithm")

The maze is generated using a **Depth-First Search (DFS)** algorithm with a stack.

* A virtual "mouse" starts at a random cell
* It checks all neighboring cells
* Randomly chooses an unvisited neighbor
* Removes the wall between them
* Pushes the current cell onto a stack
* Backtracks when no unvisited neighbors exist

This ensures a **proper maze (perfect maze)** where:

* Every cell is reachable
* There is exactly one path between any two cells

---

## 🧱 Data Structures

The maze is represented using two arrays:

* `northWall[r][c]`

  * `1` → wall exists
  * `0` → wall removed

* `eastWall[r][c]`

  * `1` → wall exists
  * `0` → wall removed

Special structure:

* Row `0` represents the bottom boundary (phantom row)
* Column `0` represents the left boundary

---

## 🔍 Maze Solving (Backtracking)

The maze is solved using a **stack-based backtracking algorithm**:

* The mouse moves through open paths
* Keeps track of visited cells
* Marks dead ends (blue)
* Marks correct path (red)

---

## 🎮 Features

* Animated maze generation
* Animated solver:

  * 🔴 Red → correct path
  * 🔵 Blue → dead ends
* Adjustable speed
* Keyboard controls
* Clean UI with legend

---

## 🎯 Bonus Feature (Cycles)

An optional mode allows the mouse to remove **extra walls (1 in 20)**:

* Creates loops (cycles) in the maze
* Breaks the "shoulder-to-the-wall" rule
* Demonstrates the difference between:

  * Tree structure (perfect maze)
  * Graph with cycles

---

## 🎹 Controls

| Key   | Action                      |
| ----- | --------------------------- |
| G     | Generate maze               |
| S     | Solve maze                  |
| R     | Reset                       |
| E     | Toggle extra walls (cycles) |
| + / - | Adjust speed                |
| ESC   | Quit                        |

---

## 🛠️ Technologies Used

* Python
* Pygame

---

## 🎥 Demonstration

Loom Recording:
https://www.loom.com/share/c67b68f6a9044381a95c5ab4c6616402

The demonstration includes:

* Dynamic maze generation using the DFS "mouse" algorithm
* Animated wall removal ("mouse eating walls")
* Maze solving with backtracking
* Red path visualization
* Blue dead-end visualization
* Bonus cycle generation using extra-wall mode
* Keyboard interaction and speed adjustment

---

## 📂 Author

* Nanat Abeshu
* I.D.: UGR/6300/16
