# Dijkstra's Algorithm Route Finder & Visualizer

An interactive desktop GUI application built in Python and Tkinter that visualizes Dijkstra's shortest path algorithm on dynamic, user-configurable weighted graphs.

## Features
- **Dynamic Graph Construction:** Click to place nodes, drag to reposition, and link nodes with automatically computed Euclidean weights.
- **Real-Time Step-by-Step Animation:** Utilizes Python generator coroutines (`yield`) to drive progressive frontier exploration (visiting, visited, frontier nodes) without freezing the UI event loop.
- **Priority Queue Optimization:** Graph traversal is powered by `heapq` for $O((V + E) \log V)$ time complexity.
- **Interactive Controls:** Adjustable animation execution speed, preset demo topologies, and node coordinate state caching.

## Tech Stack
- **Language:** Python 3
- **GUI Framework:** Tkinter (Canvas-based vector rendering)
- **Data Structures:** Adjacency mappings, min-heap priority queues, hash sets

## How to Run

### Prerequisites
Python 3.8 or higher installed with standard Tkinter support.

### Execution
```bash
git clone [https://github.com/tanakachandamara-crypto/dijkstra-pathfinding-visualizer.git](https://github.com/tanakachandamara-crypto/dijkstra-pathfinding-visualizer.git)
cd dijkstra-pathfinding-visualizer/src
python main.py
