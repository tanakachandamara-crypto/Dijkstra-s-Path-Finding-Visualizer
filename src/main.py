import tkinter as tk
from tkinter import messagebox
import math
import heapq

# ==========================================
# 1. THEME & CONFIGURATION
# ==========================================
class UITheme:
    BG_COLOR = "#1e1e2e"
    PANEL_BG = "#2b2b3d"
    CANVAS_BG = "#181825"
    NODE_COLOR = "#89b4fa"
    NODE_TEXT = "#11111b"
    EDGE_COLOR = "#45475a"
    EDGE_TEXT = "#a6adc8"
    START_COLOR = "#a6e3a1"      # Green
    END_COLOR = "#f38ba8"        # Red
    VISITING_COLOR = "#f9e2af"   # Yellow
    VISITED_COLOR = "#fab387"    # Orange
    PATH_COLOR = "#00f0ff"       # Cyan
    NODE_RADIUS = 20


# ==========================================
# 2. DATA MODEL (The Graph)
# ==========================================
class GraphModel:
    """Handles all data related to nodes, edges, and distances."""
    def __init__(self):
        self.nodes = {}  # {node_id: {'name': str, 'x': float, 'y': float}}
        self.edges = {}  # {frozenset({u, v}): weight_in_km}
        self.node_counter = 0

    def get_node_name(self, index):
        """Generate alphabetical node names: A..Z, AA..ZZ."""
        name = ""
        while index >= 0:
            name = chr(index % 26 + ord('A')) + name
            index = index // 26 - 1
        return name

    def add_node(self, x, y):
        node_id = f"N{self.node_counter}"
        node_name = self.get_node_name(self.node_counter)
        self.nodes[node_id] = {'name': node_name, 'x': x, 'y': y}
        self.node_counter += 1
        return node_id, node_name

    def toggle_edge(self, u, v):
        """Adds an edge if it doesn't exist, removes it if it does."""
        edge_key = frozenset({u, v})
        if edge_key in self.edges:
            del self.edges[edge_key]
            return False, 0  # Edge removed
        else:
            dist = self.calculate_distance(u, v)
            self.edges[edge_key] = dist
            return True, dist  # Edge added

    def calculate_distance(self, u, v):
        return int(math.hypot(self.nodes[u]['x'] - self.nodes[v]['x'], 
                              self.nodes[u]['y'] - self.nodes[v]['y']))

    def update_node_position(self, node_id, x, y):
        self.nodes[node_id]['x'] = x
        self.nodes[node_id]['y'] = y
        # Recalculate connected edges
        for edge_key in list(self.edges.keys()):
            if node_id in edge_key:
                u, v = tuple(edge_key)
                self.edges[edge_key] = self.calculate_distance(u, v)

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.node_counter = 0


# ==========================================
# 3. ALGORITHM (Pathfinding Logic)
# ==========================================
class Pathfinder:
    """Contains pure algorithmic logic independent of the UI."""
    @staticmethod
    def dijkstra_generator(graph, start_id, target_id):
        adj = {n: [] for n in graph.nodes}
        for edge_key, weight in graph.edges.items():
            u, v = tuple(edge_key)
            adj[u].append((v, weight))
            adj[v].append((u, weight))

        distances = {n: float('inf') for n in graph.nodes}
        distances[start_id] = 0
        parent = {n: None for n in graph.nodes}
        pq = [(0, start_id)]
        visited = set()

        while pq:
            curr_dist, u = heapq.heappop(pq)
            if u in visited:
                continue
            visited.add(u)

            # Yield current state for visualization
            yield ('visit', u, visited, distances)

            if u == target_id:
                break

            for v, weight in adj[u]:
                if v not in visited:
                    new_dist = curr_dist + weight
                    if new_dist < distances[v]:
                        distances[v] = new_dist
                        parent[v] = u
                        heapq.heappush(pq, (new_dist, v))

        # Reconstruct path
        path = []
        curr = target_id
        while curr is not None:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

        if path and path[0] == start_id:
            yield ('done', path, distances[target_id])
        else:
            yield ('unreachable', [], float('inf'))


# ==========================================
# 4. USER INTERFACE (View & Controller)
# ==========================================
class MapVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dijkstra's Route Finder")
        self.root.geometry("1050x700")
        self.root.configure(bg=UITheme.BG_COLOR)

        # Core Data
        self.graph = GraphModel()
        
        # UI States
        self.selected_node_for_edge = None
        self.start_node = None
        self.end_node = None
        self.dragged_node = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.is_animating = False

        self._build_ui()
        self.load_preset_map()

    def _build_ui(self):
        # Top Panel
        top_panel = tk.Frame(self.root, bg=UITheme.PANEL_BG, pady=10, padx=15)
        top_panel.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_panel, text="Dijkstra's Route Finder", 
                 font=("Helvetica", 14, "bold"), bg=UITheme.PANEL_BG, fg="#cdd6f4").pack(side=tk.LEFT, padx=(0, 20))

        # Buttons
        btn_opts = {"font": ("Helvetica", 10, "bold"), "relief": tk.FLAT, "cursor": "hand2", "padx": 10, "pady": 4}
        tk.Button(top_panel, text="Find Shortest Path", bg="#a6e3a1", activebackground="#94e2d5", 
                  command=self.run_animation, **btn_opts).pack(side=tk.LEFT, padx=5)
        tk.Button(top_panel, text="Clear Route", bg="#fab387", activebackground="#f9e2af", 
                  command=self.clear_route, **btn_opts).pack(side=tk.LEFT, padx=5)
        tk.Button(top_panel, text="Load Preset", bg="#89b4fa", activebackground="#b4befe", 
                  command=self.load_preset_map, **btn_opts).pack(side=tk.LEFT, padx=5)
        tk.Button(top_panel, text="Reset Map", bg="#f38ba8", activebackground="#eba0ac", 
                  command=self.reset_all, **btn_opts).pack(side=tk.LEFT, padx=5)

        # Speed Slider
        tk.Label(top_panel, text="Animation Speed:", bg=UITheme.PANEL_BG, fg="#a6adc8").pack(side=tk.LEFT, padx=(20, 5))
        self.speed_scale = tk.Scale(top_panel, from_=10, to=300, orient=tk.HORIZONTAL, bg=UITheme.PANEL_BG,
                                    fg="#cdd6f4", highlightthickness=0, troughcolor="#45475a", length=100)
        self.speed_scale.set(70)
        self.speed_scale.pack(side=tk.LEFT)

        # Bottom Info Bar
        info_panel = tk.Frame(self.root, bg=UITheme.PANEL_BG, pady=6, padx=15)
        info_panel.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = tk.Label(info_panel, text="Left-Click: Add/Connect/Drag | Right-Click: Set Start/End", 
                                     font=("Helvetica", 10), bg=UITheme.PANEL_BG, fg="#cdd6f4")
        self.status_label.pack(side=tk.LEFT)
        self.route_info = tk.Label(info_panel, text="Distance: 0 km", font=("Helvetica", 10, "bold"), 
                                   bg=UITheme.PANEL_BG, fg=UITheme.PATH_COLOR)
        self.route_info.pack(side=tk.RIGHT)

        # Canvas
        self.canvas = tk.Canvas(self.root, bg=UITheme.CANVAS_BG, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bindings
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", lambda e: setattr(self, 'dragged_node', None))
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Button-2>", self.on_right_click) # Mac trackpad fallback

    # --- Mouse Events ---
    def get_clicked_node(self, x, y):
        for node_id, data in self.graph.nodes.items():
            if math.hypot(data['x'] - x, data['y'] - y) <= UITheme.NODE_RADIUS:
                return node_id
        return None

    def on_left_click(self, event):
        if self.is_animating: return
        node_id = self.get_clicked_node(event.x, event.y)

        if not node_id:
            # Create Node
            n_id, n_name = self.graph.add_node(event.x, event.y)
            self.selected_node_for_edge = None
            self.status_label.config(text=f"Added City '{n_name}'.")
        else:
            # Handle Drag/Connect Prep
            self.dragged_node = node_id
            self.drag_offset_x = event.x - self.graph.nodes[node_id]['x']
            self.drag_offset_y = event.y - self.graph.nodes[node_id]['y']

            if not self.selected_node_for_edge:
                self.selected_node_for_edge = node_id
                self.status_label.config(text=f"Selected City. Click another to link.")
            elif self.selected_node_for_edge == node_id:
                self.selected_node_for_edge = None
                self.status_label.config(text="Deselected city.")
            else:
                # Toggle Edge
                added, dist = self.graph.toggle_edge(self.selected_node_for_edge, node_id)
                msg = f"Connected ({dist} km)" if added else "Removed road"
                self.status_label.config(text=msg)
                self.selected_node_for_edge = None
        self.redraw()

    def on_drag(self, event):
        if self.is_animating or not self.dragged_node: return
        r = UITheme.NODE_RADIUS
        w = max(r, min(self.canvas.winfo_width() - r, event.x - self.drag_offset_x))
        h = max(r, min(self.canvas.winfo_height() - r, event.y - self.drag_offset_y))
        
        self.graph.update_node_position(self.dragged_node, w, h)
        self.redraw()

    def on_right_click(self, event):
        if self.is_animating: return
        node_id = self.get_clicked_node(event.x, event.y)
        if not node_id: return

        if not self.start_node:
            self.start_node = node_id
            self.status_label.config(text="Start city set. Right-click another for Destination.")
        elif self.start_node == node_id:
            self.start_node = None
            self.status_label.config(text="Removed Start city.")
        elif not self.end_node:
            self.end_node = node_id
            self.status_label.config(text="Destination set. Ready to find route!")
        elif self.end_node == node_id:
            self.end_node = None
            self.status_label.config(text="Removed Destination.")
        else:
            self.start_node = node_id
            self.end_node = None
            self.status_label.config(text="New Start city. Right-click another for Destination.")
        
        self.clear_route(keep_endpoints=True)

    # --- Drawing Logic ---
    def redraw(self, active_path=None, visiting_node=None, visited_nodes=None):
        self.canvas.delete("all")
        visited_nodes = visited_nodes or set()
        active_edges = {frozenset({active_path[i], active_path[i+1]}) for i in range(len(active_path)-1)} if active_path else set()

        # Draw Edges
        for edge_key, weight in self.graph.edges.items():
            u, v = tuple(edge_key)
            x1, y1 = self.graph.nodes[u]['x'], self.graph.nodes[u]['y']
            x2, y2 = self.graph.nodes[v]['x'], self.graph.nodes[v]['y']
            is_active = edge_key in active_edges

            color = UITheme.PATH_COLOR if is_active else UITheme.EDGE_COLOR
            width = 4 if is_active else 2
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width, smooth=True)

            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            self.canvas.create_rectangle(mx - 14, my - 8, mx + 14, my + 8, fill=UITheme.CANVAS_BG, outline="")
            self.canvas.create_text(mx, my, text=f"{weight}", fill=UITheme.EDGE_TEXT, font=("Helvetica", 8, "bold"))

        # Draw Nodes
        r = UITheme.NODE_RADIUS
        for node_id, data in self.graph.nodes.items():
            x, y = data['x'], data['y']
            
            fill_col = UITheme.NODE_COLOR
            if node_id == self.start_node: fill_col = UITheme.START_COLOR
            elif node_id == self.end_node: fill_col = UITheme.END_COLOR
            elif node_id == visiting_node: fill_col = UITheme.VISITING_COLOR
            elif node_id in visited_nodes: fill_col = UITheme.VISITED_COLOR
            elif node_id == self.selected_node_for_edge: fill_col = "#cdd6f4"

            out_width = 3 if node_id in [self.start_node, self.end_node, self.selected_node_for_edge] else 1
            out_col = "#ffffff" if node_id == self.selected_node_for_edge else "#313244"

            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=fill_col, outline=out_col, width=out_width)
            self.canvas.create_text(x, y, text=data['name'], fill=UITheme.NODE_TEXT, font=("Helvetica", 10, "bold"))

    # --- Animation ---
    def run_animation(self):
        if not self.start_node or not self.end_node:
            messagebox.showwarning("Error", "Please set Start (Green) and Destination (Red) using Right-Click.")
            return
        if self.is_animating: return

        self.is_animating = True
        self.status_label.config(text="Finding optimal route...")
        gen = Pathfinder.dijkstra_generator(self.graph, self.start_node, self.end_node)

        def step():
            try:
                action, data, *extra = next(gen)
                if action == 'visit':
                    self.redraw(visiting_node=data, visited_nodes=extra[0])
                    self.root.after(self.speed_scale.get(), step)
                elif action == 'done':
                    path_names = " -> ".join([self.graph.nodes[n]['name'] for n in data])
                    self.status_label.config(text=f"Route: {path_names}")
                    self.route_info.config(text=f"Distance: {extra[0]} km")
                    self.redraw(active_path=data)
                    self.is_animating = False
                elif action == 'unreachable':
                    self.status_label.config(text="No route exists!")
                    self.route_info.config(text="Distance: Unreachable")
                    self.redraw()
                    self.is_animating = False
            except StopIteration:
                self.is_animating = False
        step()

    # --- Utilities ---
    def clear_route(self, keep_endpoints=False):
        if not keep_endpoints:
            self.start_node = self.end_node = None
        self.route_info.config(text="Distance: 0 km")
        self.redraw()

    def reset_all(self):
        self.graph.clear()
        self.selected_node_for_edge = self.start_node = self.end_node = None
        self.clear_route()
        self.status_label.config(text="Map cleared.")

    def load_preset_map(self):
        self.reset_all()
        preset_coords = {'A': (150, 150), 'B': (350, 100), 'C': (320, 280), 'D': (550, 160),
                         'E': (580, 360), 'F': (780, 220), 'G': (750, 420), 'H': (920, 320)}
        name_to_id = {}
        
        for name, (x, y) in preset_coords.items():
            nid, _ = self.graph.add_node(x, y)
            name_to_id[name] = nid

        preset_edges = [('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D'), ('C', 'E'), 
                        ('D', 'F'), ('D', 'E'), ('E', 'G'), ('F', 'G'), ('F', 'H'), ('G', 'H')]
        
        for u, v in preset_edges:
            self.graph.toggle_edge(name_to_id[u], name_to_id[v])

        self.start_node, self.end_node = name_to_id['A'], name_to_id['H']
        self.redraw()


if __name__ == "__main__":
    root = tk.Tk()
    app = MapVisualizerApp(root)
    root.mainloop()