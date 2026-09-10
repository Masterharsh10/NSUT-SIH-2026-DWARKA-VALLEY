# TerraNav – Radar-Based Safety & Navigation System for Mine Vehicles in Fog
 
This repository contains our SIH 2026 project submission.
 
## 1. Project Information
 
- **Project Title:** TerraNav – Radar-Based Safety & Navigation System for Mine Vehicles in Fog
- **PS ID:** SIH26007
- **PS Title:** Safe and Efficient Operation of Mine Vehicles in Fog and Low-Visibility Conditions in Open Cast Iron Ore Mines
- **Category:** Hardware
- **Theme:** Smart Automation
## 2. Problem Statement
 
Dense monsoon fog in open-cast iron ore mines (e.g. Bailadila, Dantewada) scatters both visible light and LiDAR pulses off water droplets, blinding drivers and camera/LiDAR-based driver-assist systems at the same time. Mines currently respond by slowing down or halting operations until fog clears — which protects safety but directly cuts production, even though the problem statement calls for **safe and efficient** operation, not just a system that stops the truck.
 
## 3. Proposed Solution
 
TerraNav is a multi-tier edge-computing system that lets a haul truck sense its way through fog it cannot see through:
 
- **4D mmWave radar** detects obstacles by physically ignoring fog and dust, instead of trying to see through it like a camera or LiDAR
- An onboard **A\* pathfinder** computes and displays a live bypass route around the obstacle, instead of just warning the driver
- An **independent hardware reflex** (MCU) cuts power directly if a critical threshold is crossed, bypassing the main software stack entirely
- A **LoRa V2V/V2X mesh** lets trucks warn each other before line-of-sight detection is even possible
- A **mandatory BLE personnel tag** covers radar's blind spot on small, slow, human-scale targets — protecting ground workers specifically
## 4. Key Features
 
- Fog-penetrating 4D mmWave radar obstacle detection (distance, angle, relative velocity)
- Live A* path rerouting around detected obstacles, not just a warning
- Independent hardware safety reflex — cuts motor power even if the main software stack is frozen or unresponsive
- Mandatory BLE personnel-tag detection, closing radar's blind spot on people
- LoRa V2V/V2X mesh broadcasting position, speed, and brake-status between vehicles
- AR path overlay rendered live on the driver's camera feed
- RTK-GPS + IMU position lock against a pre-surveyed digital haul-road boundary
## 5. Technology Stack
 
- **Perception Hardware:** TI AWR1843 4D mmWave radar ·RTK-GPS + MPU6050 IMU · BLE beacon 
- **Compute:** (Python) ·fallback MCU (bare-metal C) · ESP32
- **Communication:** LoRa (866 MHz, India ISM band) · BLE · UART / SPI / I²C
- **Simulation & Modeling:** Python (A* pathfinding, sensor-fusion logic)
- **Tooling:** KiCad / EasyEDA (circuit diagrams) · Git
## 6. Architecture

        ┌────────────────────────────┐
        │       PERCEPTION TIER       │
        │  Radar · RTK-GPS+IMU ·      │
        │  BLE Personnel Tag · Camera │
        └──────────────┬─────────────┘
                        │
                        v
        ┌────────────────────────────┐
        │        COMPUTE TIER         │
        │  Pi — A* Pathfinder + AR    │
        │  Reflex Board (FPGA/MCU)    │
        │  ESP32 — LoRa V2X + BLE     │
        └──────────────┬─────────────┘
                        │
                        v
        ┌────────────────────────────┐
        │       INTERFACE TIER        │
        │  AR Path Overlay            │
        │  V2X Broadcast              │
        │  Motor Reflex Cutoff        │
        └────────────────────────────┘

 
## 7. Repository Structure
 
```
TerraNav/
├── README.md
├── submission.md       
├── terranav_sim.py       # End-to-end radar → A* → AR simulation
├── esp_code.pdf
├── requirements.txt
├── .gitignore
└── LICENSE
```
 
### What goes where?
``` 
| Item | Location |
|---|---|
| ESP32 / reflex firmware | `firmware/` |
| Simulation (Python) | `simulation/` |
| Project screenshots / hardware photos | `assets/screenshots/` |
| Final PPT / presentation | `submission.md/` |
| Demo video link | `submission.md/` |
| Project overview | `README.md` |
 ```
## 8. Final Presentation

Link - https://drive.google.com/file/d/1zTn3Ow_8Lwkq7asrLZ14QZSwZh6zExr_/view?usp=sharing

 
 
## 9. Demo Video

Link - https://www.youtube.com/watch?v=YTs8wyJ8J9k
 
 
## 10.Prototype Photos and costing
 

 
See [`Images & Costing.pdf`] for examples and naming conventions and industrial cost of proposed final solution.
 
## 11. Installation
```
# 1. Clone the repository
git clone https://github.com/<Masterharsh10>/<NSUT-SIH-2026-DWARKA-VALLEY
>.git

# 2. Navigate to the project folder
cd <NSUT-SIH-2026-DWARKA-VALLEY
>

# 3. Install required Python libraries
pip install numpy matplotlib pyserial keyboard

# 4. Run the Python dashboard
python main.py
```
## 12. Future Scope
 
- Integrate the real AWR1843 radar point cloud (simulated for the current demo)
- Add genuine RTK correction (NTRIP feed or a dedicated base station) for centimeter-accurate positioning
- Move the hardware reflex fully to FPGA once the team has deeper Verilog experience
- Real windshield AR HUD (optical combiner) in place of the current screen-based overlay
- Fleet-wide control room dashboard aggregating V2X broadcasts across all trucks
- Pilot retrofit on an actual mine haul truck, beyond the two-rover demo platform
