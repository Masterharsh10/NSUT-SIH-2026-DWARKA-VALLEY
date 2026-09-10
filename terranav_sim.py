import numpy as np
import matplotlib.pyplot as plt
import time
import heapq 
import keyboard

# =========================================================================
# 0. DISABLE MATPLOTLIB HOTKEYS
# =========================================================================
plt.rcParams['keymap.save'] = []
plt.rcParams['keymap.quit'] = []
plt.rcParams['keymap.fullscreen'] = []
plt.rcParams['keymap.home'] = []
plt.rcParams['keymap.back'] = []
plt.rcParams['keymap.forward'] = []

# =========================================================================
# 1. A* PATHFINDING ALGORITHM
# =========================================================================
def heuristic(a, b): 
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid, start, goal):
    neighbors = [(0,1), (0,-1), (1,0), (-1,0), (1,1), (1,-1), (-1,1), (-1,-1)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))
    
    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            return data[::-1]
            
        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            if 0 <= neighbor[0] < grid.shape[0] and 0 <= neighbor[1] < grid.shape[1]:
                if grid[neighbor[0]][neighbor[1]] > 0: 
                    continue
            else: 
                continue
                
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0): 
                continue
                
            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [k[1] for k in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
    return []

# =========================================================================
# 2. SIL MOCK HARDWARE CLASS (MANUAL OVERRIDE)
# =========================================================================
class MockTeleopESP32:
    def __init__(self):
        self.distance = 100.0
        self.state = "STOPPED"
        self.in_waiting = 1

    def readline(self):
        # Failsafe trigger: Brake if obstacle is under 20cm
        if self.distance <= 20.0:
            self.state = "EMERGENCY_BRAKE"

        telemetry = f"{self.distance},{self.state}\n"
        time.sleep(0.05) 
        return telemetry.encode('utf-8')

    def write(self, command):
        cmd = command.decode('utf-8')
        
        # Priority Override: Obstacle Drop
        if cmd == 'O':
            self.distance = 15.0
            self.state = "EMERGENCY_BRAKE"
            print("\n[!] RADAR OVERRIDE: OBSTACLE DROPPED AT 15cm [!]")
            
        elif self.state == "EMERGENCY_BRAKE" and cmd == 'W':
            pass  # Failsafe locks out forward throttle until you steer away
            
        elif cmd == 'W':
            self.state = "MOVING"
            
        elif cmd in ['A', 'D']:
            self.state = "TURNING"
            self.distance = 100.0  # Steering physically points sensor away from obstacle
            
        elif cmd == 'S':
            self.state = "REVERSING"
            self.distance = 100.0  # Reversing backs away from obstacle
            
        elif cmd == 'X':
            self.state = "STOPPED"

# =========================================================================
# 3. MAIN TELEOPERATION & HUD LOOP
# =========================================================================
def run_teleoperation_dashboard():
    esp32 = MockTeleopESP32()
    print("=====================================================")
    print("SIL Active! Use W-A-S-D to drive.")
    print("Press 'O' at ANY time to drop an obstacle.")
    print("=====================================================")

    # Initialize Haul Road Map
    grid = np.zeros((30, 30))
    grid[:, 0:5] = 1    # Left boundary
    grid[:, 25:30] = 1  # Right boundary
    
    start_pos = (5, 15)
    goal_pos = (28, 15)
    truck_pos = list(start_pos)
    
    path = a_star(grid, tuple(truck_pos), goal_pos)
    
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 8))
    warning_text = ""
    warning_color = "black"

    while True:
        # 1. Read Keyboard Inputs (Hierarchy fixed so 'O' is never ignored)
        cmd = b'X'
        if keyboard.is_pressed('o'): 
            cmd = b'O' # God-Mode: Drop Obstacle
        elif keyboard.is_pressed('w'): 
            cmd = b'W'
            if truck_pos[0] < 29: truck_pos[0] += 0.2
        elif keyboard.is_pressed('s'): 
            cmd = b'S'
            if truck_pos[0] > 0: truck_pos[0] -= 0.2
        elif keyboard.is_pressed('a'): 
            cmd = b'A'
            if truck_pos[1] > 0: truck_pos[1] -= 0.2
        elif keyboard.is_pressed('d'): 
            cmd = b'D'
            if truck_pos[1] < 29: truck_pos[1] += 0.2
            
        esp32.write(cmd)

        # 2. Process Telemetry
        if esp32.in_waiting > 0:
            raw = esp32.readline().decode('utf-8', errors='ignore').strip()
            data = raw.split(',')
            
            if len(data) == 2:
                try:
                    distance = float(data[0])
                    state = data[1]
                except ValueError:
                    continue
                
                # 3. Dynamic Hazard Detection & Reroute
                if state == "EMERGENCY_BRAKE":
                    warning_text = f"OBSTACLE {distance:.1f}cm! FOLLOW NEW DETOUR"
                    warning_color = "red"
                    
                    obs_y = int(truck_pos[0]) + 3
                    obs_x = int(truck_pos[1])
                    if obs_y < 30: 
                        grid[obs_y, max(0, obs_x-1):min(30, obs_x+2)] = 2
                    
                    path = a_star(grid, (int(truck_pos[0]), int(truck_pos[1])), goal_pos)
                else:
                    warning_text = f"Distance: {distance:.1f}cm | State: {state}"
                    warning_color = "blue"

                # 4. Render HUD
                ax.clear()
                ax.set_title(warning_text, color=warning_color, fontsize=14, weight='bold')
                ax.imshow(grid, cmap='terrain')
                
                if path:
                    path_y, path_x = zip(*path)
                    ax.plot(path_x, path_y, 'w--', linewidth=2, label="Intended Route")
                
                ax.plot(goal_pos[1], goal_pos[0], 'rx', markersize=15, label="Dump Zone")
                truck_color = 'cyan' if state != "EMERGENCY_BRAKE" else 'red'
                ax.plot(truck_pos[1], truck_pos[0], marker='s', color=truck_color, markersize=12)
                
                ax.invert_yaxis()
                ax.legend(loc="lower right")
                plt.pause(0.05)

if __name__ == "__main__":
    run_teleoperation_dashboard()
