# 🖥️ OS Simulator — Operating Systems Graduation Project

A comprehensive **Operating Systems Simulator** built in Python that demonstrates core OS concepts through interactive simulation and a visual web dashboard.

---

## 📌 Project Overview

This project simulates six fundamental Operating Systems components:

| Module | Description |
|--------|-------------|
| ⚙️ Process Scheduling | FCFS, SJF, Priority, Round Robin with Gantt Charts |
| 🧠 Memory Management | Paging, Frame Allocation, Address Translation |
| 📄 Page Replacement | FIFO, LRU, Optimal algorithms with comparison |
| 🔒 Deadlock Management | Banker's Algorithm (Safety Check + Resource Request) |
| 🗂️ File System | Hierarchical directory tree, CRUD operations |
| 🔄 Synchronization | Producer-Consumer with Semaphores & Mutex |

---

## 📁 Project Structure

```
os-simulator/
│
├── os_core.py                  # Core simulation logic (all 6 modules)
├── main.py                     # Entry point — run all modules
├── os_simulator_dashboard.html # Interactive visual dashboard (open in browser)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- A modern web browser (Chrome, Firefox, Edge)

### Installation

```bash
# 1. Clone or download the project files
# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the simulator
python main.py
```

### Open the Dashboard

Simply open `os_simulator_dashboard.html` in your browser — no server required.

---

## 🔧 Modules In Detail

### 1. Process Scheduling

Simulates CPU scheduling with 4 algorithms:

- **FCFS** (First Come First Served) — non-preemptive, arrival order
- **SJF** (Shortest Job First) — non-preemptive, minimizes average wait time
- **Priority Scheduling** — lower number = higher priority
- **Round Robin** — preemptive, configurable time quantum

**Output:** Gantt Chart, Waiting Time, Turnaround Time per process.

```python
from os_core import ProcessScheduler, Process, SchedulingAlgorithm

scheduler = ProcessScheduler(algorithm=SchedulingAlgorithm.ROUND_ROBIN, quantum=3)
scheduler.add_process(Process("P1", burst_time=8, arrival_time=0))
scheduler.add_process(Process("P2", burst_time=4, arrival_time=1))
result = scheduler.run()
print(result)
```

---

### 2. Memory Management (Paging)

Simulates physical memory divided into fixed-size frames:

- Allocates pages to processes
- Maintains per-process page tables
- Translates logical addresses to physical addresses
- Detects page faults

```python
from os_core import MemoryManager, Process

mem = MemoryManager(total_memory=4096, page_size=256)
p = Process("P1", memory_required=512)
mem.allocate(p)
physical, msg = mem.translate_address(p.pid, 300)
print(msg)  # Logical 300 → Physical XXXX
```

---

### 3. Page Replacement Algorithms

Compares three algorithms on a reference string:

- **FIFO** — evicts the oldest page
- **LRU** — evicts the least recently used page
- **Optimal** — evicts the page used farthest in the future (theoretical best)

```python
from os_core import PageReplacer

pr = PageReplacer(num_frames=4)
ref = [7,0,1,2,0,3,0,4,2,3,0,3,2,1,2,0,1,7]
results = pr.compare_all(ref)
for r in results:
    print(f"{r['algorithm']}: {r['faults']} faults, {r['hits']} hits")
```

---

### 4. Deadlock Management — Banker's Algorithm

Implements the Banker's Algorithm for deadlock avoidance:

- **Safety Check** — determines if the system is in a safe state
- **Resource Request** — grants or denies requests based on safety
- **Deadlock Detection** — identifies deadlocked processes

```python
from os_core import DeadlockManager

dm = DeadlockManager(
    num_processes=5, num_resources=3,
    available=[3,3,2],
    max_matrix=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]],
    allocation_matrix=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
)
print(dm.is_safe())          # Safe state + sequence
print(dm.detect_deadlock())  # Deadlock detection
print(dm.request_resources(1, [1,0,2]))  # Request resources
```

---

### 5. File System

Simulates a hierarchical Unix-like file system:

- Create/delete files and directories
- Navigate with `cd`, list with `ls`
- Read and write file content
- Address translation with logical tree

```python
from os_core import FileSystem

fs = FileSystem()
fs.mkdir("projects")
fs.cd("projects")
fs.create_file("main.py", "print('Hello OS!')")
content, _ = fs.read_file("main.py")
print(fs.pwd())   # /projects
print(fs.ls())    # ['main.py']
```

---

### 6. Producer-Consumer (Synchronization)

Demonstrates the classic synchronization problem using:

- **Semaphores** (empty/full) to control buffer access
- **Mutex** to ensure mutual exclusion
- **Threading** to simulate concurrent producer and consumer

```python
from os_core import ProducerConsumerSimulator

sim = ProducerConsumerSimulator(buffer_size=5)
result = sim.simulate(num_produce=10, num_consume=10)
print(f"Produced: {result['produced']}, Consumed: {result['consumed']}")
```

---

## 🖥️ Interactive Dashboard

Open `os_simulator_dashboard.html` in any browser to access the visual dashboard:

- **Scheduling Tab** — live Gantt chart, process table, algorithm comparison
- **Memory Tab** — visual frame grid, address translator
- **Deadlock Tab** — Banker's matrix, safety checker, request simulator
- **Page Replacement Tab** — step-by-step table for FIFO/LRU/Optimal
- **File System Tab** — clickable file tree, terminal-style operations
- **Sync Tab** — animated producer-consumer buffer simulation

---

## 📊 Sample Output

```
=== PROCESS SCHEDULING ===
Algorithm: Round Robin (Quantum=3)
Average Waiting Time:  5.4
Average Turnaround:    9.8

=== MEMORY MANAGEMENT ===
Total Frames: 16  |  Used: 10  |  Free: 6  |  Utilization: 62.5%

=== PAGE REPLACEMENT ===
Reference String: [7,0,1,2,0,3,0,4,2,3,0,3,0,3,2,1,2,0,1,7]
FIFO:    15 faults | 5 hits
LRU:     12 faults | 8 hits
Optimal: 8 faults  | 12 hits

=== DEADLOCK ===
System is in SAFE STATE
Safe Sequence: P1 → P3 → P4 → P0 → P2

=== SYNCHRONIZATION ===
Produced: 8 items | Consumed: 8 items | No race conditions
```

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Core simulation logic |
| `threading` | Concurrent producer-consumer |
| `collections.deque` | Efficient queue for scheduling |
| HTML/CSS/JS | Interactive dashboard |
| Canvas API | Gantt chart rendering |

---

## 👨‍💻 Author

**Graduation Project — Operating Systems Course**  
Faculty of Computer Science & Information Technology

---

## 📝 License

This project is developed for academic purposes.
