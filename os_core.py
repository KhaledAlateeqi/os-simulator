"""
OS Simulator - Complete Operating System Simulation
Covers: Process Scheduling, Memory Management, Deadlock, File System,
        Page Replacement, and Producer-Consumer Synchronization
"""

import random
import time
import threading
import queue
from collections import deque, defaultdict
from enum import Enum

# ─────────────────────────────────────────────
# ENUMS & CONSTANTS
# ─────────────────────────────────────────────

class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"

class SchedulingAlgorithm(Enum):
    FCFS = "FCFS"
    SJF = "SJF"
    PRIORITY = "Priority"
    ROUND_ROBIN = "Round Robin"

class PageReplacementAlgorithm(Enum):
    FIFO = "FIFO"
    LRU = "LRU"
    OPTIMAL = "Optimal"

# ─────────────────────────────────────────────
# 1. PROCESS MANAGEMENT
# ─────────────────────────────────────────────

class Process:
    _id_counter = 1

    def __init__(self, name=None, burst_time=None, priority=1, arrival_time=0, memory_required=None):
        self.pid = Process._id_counter
        Process._id_counter += 1
        self.name = name or f"P{self.pid}"
        self.burst_time = burst_time or random.randint(2, 12)
        self.remaining_time = self.burst_time
        self.priority = priority
        self.arrival_time = arrival_time
        self.memory_required = memory_required or random.randint(64, 512)
        self.state = ProcessState.NEW
        self.waiting_time = 0
        self.turnaround_time = 0
        self.start_time = None
        self.finish_time = None
        self.allocated_frames = []

    def to_dict(self):
        return {
            "pid": self.pid,
            "name": self.name,
            "burst_time": self.burst_time,
            "remaining_time": self.remaining_time,
            "priority": self.priority,
            "arrival_time": self.arrival_time,
            "memory_required": self.memory_required,
            "state": self.state.value,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time,
        }

    def __repr__(self):
        return f"Process({self.name}, PID={self.pid}, BT={self.burst_time}, State={self.state.value})"


class ProcessScheduler:
    def __init__(self, algorithm=SchedulingAlgorithm.ROUND_ROBIN, quantum=3):
        self.algorithm = algorithm
        self.quantum = quantum
        self.processes = []
        self.ready_queue = deque()
        self.gantt_chart = []
        self.current_time = 0

    def add_process(self, process):
        process.state = ProcessState.READY
        self.processes.append(process)
        self.ready_queue.append(process)

    def run_fcfs(self):
        self.gantt_chart = []
        sorted_procs = sorted(self.processes, key=lambda p: p.arrival_time)
        t = 0
        for p in sorted_procs:
            if t < p.arrival_time:
                t = p.arrival_time
            p.start_time = t
            p.state = ProcessState.RUNNING
            self.gantt_chart.append({"process": p.name, "start": t, "end": t + p.burst_time})
            t += p.burst_time
            p.finish_time = t
            p.turnaround_time = p.finish_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            p.state = ProcessState.TERMINATED
        return self._stats()

    def run_sjf(self):
        self.gantt_chart = []
        remaining = sorted(self.processes, key=lambda p: p.arrival_time)
        t = 0
        completed = []
        while remaining:
            available = [p for p in remaining if p.arrival_time <= t]
            if not available:
                t = remaining[0].arrival_time
                continue
            p = min(available, key=lambda x: x.burst_time)
            remaining.remove(p)
            p.start_time = t
            p.state = ProcessState.RUNNING
            self.gantt_chart.append({"process": p.name, "start": t, "end": t + p.burst_time})
            t += p.burst_time
            p.finish_time = t
            p.turnaround_time = p.finish_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            p.state = ProcessState.TERMINATED
            completed.append(p)
        return self._stats()

    def run_priority(self):
        self.gantt_chart = []
        remaining = sorted(self.processes, key=lambda p: p.arrival_time)
        t = 0
        completed = []
        while remaining:
            available = [p for p in remaining if p.arrival_time <= t]
            if not available:
                t = remaining[0].arrival_time
                continue
            p = min(available, key=lambda x: x.priority)
            remaining.remove(p)
            p.start_time = t
            p.state = ProcessState.RUNNING
            self.gantt_chart.append({"process": p.name, "start": t, "end": t + p.burst_time})
            t += p.burst_time
            p.finish_time = t
            p.turnaround_time = p.finish_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            p.state = ProcessState.TERMINATED
            completed.append(p)
        return self._stats()

    def run_round_robin(self):
        self.gantt_chart = []
        remaining = [(p, p.burst_time) for p in sorted(self.processes, key=lambda x: x.arrival_time)]
        queue = deque()
        t = 0
        idx = 0
        while queue or idx < len(remaining):
            while idx < len(remaining) and remaining[idx][0].arrival_time <= t:
                queue.append(list(remaining[idx]))
                idx += 1
            if not queue:
                t = remaining[idx][0].arrival_time
                continue
            item = queue.popleft()
            p, rem = item[0], item[1]
            exec_time = min(self.quantum, rem)
            if p.start_time is None:
                p.start_time = t
            p.state = ProcessState.RUNNING
            self.gantt_chart.append({"process": p.name, "start": t, "end": t + exec_time})
            t += exec_time
            rem -= exec_time
            while idx < len(remaining) and remaining[idx][0].arrival_time <= t:
                queue.append(list(remaining[idx]))
                idx += 1
            if rem > 0:
                queue.append([p, rem])
            else:
                p.finish_time = t
                p.turnaround_time = p.finish_time - p.arrival_time
                p.waiting_time = p.turnaround_time - p.burst_time
                p.state = ProcessState.TERMINATED
        return self._stats()

    def run(self):
        if self.algorithm == SchedulingAlgorithm.FCFS:
            return self.run_fcfs()
        elif self.algorithm == SchedulingAlgorithm.SJF:
            return self.run_sjf()
        elif self.algorithm == SchedulingAlgorithm.PRIORITY:
            return self.run_priority()
        else:
            return self.run_round_robin()

    def _stats(self):
        terminated = [p for p in self.processes if p.state == ProcessState.TERMINATED]
        if not terminated:
            return {}
        avg_wait = sum(p.waiting_time for p in terminated) / len(terminated)
        avg_tat = sum(p.turnaround_time for p in terminated) / len(terminated)
        return {
            "algorithm": self.algorithm.value,
            "processes": [p.to_dict() for p in terminated],
            "gantt": self.gantt_chart,
            "avg_waiting_time": round(avg_wait, 2),
            "avg_turnaround_time": round(avg_tat, 2),
        }


# ─────────────────────────────────────────────
# 2. MEMORY MANAGEMENT (Paging)
# ─────────────────────────────────────────────

class MemoryManager:
    def __init__(self, total_memory=4096, page_size=256):
        self.total_memory = total_memory
        self.page_size = page_size
        self.total_frames = total_memory // page_size
        self.frames = [None] * self.total_frames  # None = free
        self.page_tables = {}  # pid -> {page_num: frame_num}
        self.log = []

    def allocate(self, process):
        pages_needed = (process.memory_required + self.page_size - 1) // self.page_size
        free_frames = [i for i, f in enumerate(self.frames) if f is None]
        if len(free_frames) < pages_needed:
            self.log.append(f"❌ Not enough memory for {process.name} (needs {pages_needed} frames, {len(free_frames)} free)")
            return False
        self.page_tables[process.pid] = {}
        for i in range(pages_needed):
            frame = free_frames[i]
            self.frames[frame] = process.pid
            self.page_tables[process.pid][i] = frame
            process.allocated_frames.append(frame)
        self.log.append(f"✅ Allocated {pages_needed} frames to {process.name}: frames {process.allocated_frames}")
        return True

    def deallocate(self, process):
        if process.pid not in self.page_tables:
            return
        for frame in process.allocated_frames:
            self.frames[frame] = None
        del self.page_tables[process.pid]
        self.log.append(f"🔓 Freed memory for {process.name}")
        process.allocated_frames = []

    def translate_address(self, pid, logical_address):
        if pid not in self.page_tables:
            return None, "Process not in memory"
        page_num = logical_address // self.page_size
        offset = logical_address % self.page_size
        if page_num not in self.page_tables[pid]:
            return None, f"Page fault! Page {page_num} not in memory"
        frame_num = self.page_tables[pid][page_num]
        physical = frame_num * self.page_size + offset
        return physical, f"Logical {logical_address} → Physical {physical} (Page {page_num}, Frame {frame_num}, Offset {offset})"

    def get_snapshot(self):
        used = sum(1 for f in self.frames if f is not None)
        return {
            "total_frames": self.total_frames,
            "used_frames": used,
            "free_frames": self.total_frames - used,
            "utilization": round(used / self.total_frames * 100, 1),
            "frames": [{"frame": i, "pid": self.frames[i]} for i in range(self.total_frames)],
            "page_tables": {str(k): v for k, v in self.page_tables.items()},
            "log": self.log[-10:],
        }


# ─────────────────────────────────────────────
# 3. PAGE REPLACEMENT ALGORITHMS
# ─────────────────────────────────────────────

class PageReplacer:
    def __init__(self, num_frames=4):
        self.num_frames = num_frames

    def fifo(self, reference_string):
        frames = []
        order = deque()
        faults = 0
        log = []
        for page in reference_string:
            fault = False
            if page not in frames:
                fault = True
                faults += 1
                if len(frames) < self.num_frames:
                    frames.append(page)
                    order.append(page)
                else:
                    evicted = order.popleft()
                    frames[frames.index(evicted)] = page
                    order.append(page)
            log.append({"page": page, "frames": list(frames), "fault": fault})
        return {"algorithm": "FIFO", "faults": faults, "hits": len(reference_string) - faults, "log": log}

    def lru(self, reference_string):
        frames = []
        usage = {}
        faults = 0
        log = []
        for t, page in enumerate(reference_string):
            fault = False
            if page not in frames:
                fault = True
                faults += 1
                if len(frames) < self.num_frames:
                    frames.append(page)
                else:
                    lru_page = min(frames, key=lambda p: usage.get(p, -1))
                    frames[frames.index(lru_page)] = page
            usage[page] = t
            log.append({"page": page, "frames": list(frames), "fault": fault})
        return {"algorithm": "LRU", "faults": faults, "hits": len(reference_string) - faults, "log": log}

    def optimal(self, reference_string):
        frames = []
        faults = 0
        log = []
        for i, page in enumerate(reference_string):
            fault = False
            if page not in frames:
                fault = True
                faults += 1
                if len(frames) < self.num_frames:
                    frames.append(page)
                else:
                    future = reference_string[i + 1:]
                    def next_use(p):
                        try:
                            return future.index(p)
                        except ValueError:
                            return float('inf')
                    evict = max(frames, key=next_use)
                    frames[frames.index(evict)] = page
            log.append({"page": page, "frames": list(frames), "fault": fault})
        return {"algorithm": "Optimal", "faults": faults, "hits": len(reference_string) - faults, "log": log}

    def compare_all(self, reference_string):
        return [
            self.fifo(reference_string),
            self.lru(reference_string),
            self.optimal(reference_string),
        ]


# ─────────────────────────────────────────────
# 4. DEADLOCK DETECTION & AVOIDANCE (Banker's Algorithm)
# ─────────────────────────────────────────────

class DeadlockManager:
    def __init__(self, num_processes, num_resources, available, max_matrix, allocation_matrix):
        self.n = num_processes
        self.m = num_resources
        self.available = list(available)
        self.max_matrix = [list(r) for r in max_matrix]
        self.allocation = [list(r) for r in allocation_matrix]
        self.need = [
            [self.max_matrix[i][j] - self.allocation[i][j] for j in range(self.m)]
            for i in range(self.n)
        ]

    def is_safe(self):
        work = list(self.available)
        finish = [False] * self.n
        safe_seq = []
        log = []
        while len(safe_seq) < self.n:
            allocated = False
            for i in range(self.n):
                if not finish[i] and all(self.need[i][j] <= work[j] for j in range(self.m)):
                    for j in range(self.m):
                        work[j] += self.allocation[i][j]
                    finish[i] = True
                    safe_seq.append(f"P{i}")
                    log.append(f"P{i} can proceed → Work: {work}")
                    allocated = True
            if not allocated:
                break
        is_safe = len(safe_seq) == self.n
        return {
            "safe": is_safe,
            "safe_sequence": safe_seq if is_safe else [],
            "log": log,
            "message": f"✅ Safe State! Sequence: {' → '.join(safe_seq)}" if is_safe else "❌ DEADLOCK DETECTED! System is in unsafe state.",
        }

    def request_resources(self, pid, request):
        log = []
        if any(request[j] > self.need[pid][j] for j in range(self.m)):
            return {"granted": False, "message": f"P{pid} exceeded maximum claim", "log": log}
        if any(request[j] > self.available[j] for j in range(self.m)):
            return {"granted": False, "message": f"P{pid} must wait – resources not available", "log": log}
        # Try allocation
        for j in range(self.m):
            self.available[j] -= request[j]
            self.allocation[pid][j] += request[j]
            self.need[pid][j] -= request[j]
        result = self.is_safe()
        if result["safe"]:
            log.append(f"✅ Request by P{pid} granted")
            return {"granted": True, "message": "Request granted", "log": result["log"], "safe_sequence": result["safe_sequence"]}
        else:
            # Rollback
            for j in range(self.m):
                self.available[j] += request[j]
                self.allocation[pid][j] -= request[j]
                self.need[pid][j] += request[j]
            return {"granted": False, "message": "❌ Request denied – would cause unsafe state (deadlock risk)", "log": result["log"]}

    def detect_deadlock(self):
        work = list(self.available)
        finish = [False] * self.n
        for i in range(self.n):
            if all(self.allocation[i][j] == 0 for j in range(self.m)):
                finish[i] = True
        changed = True
        while changed:
            changed = False
            for i in range(self.n):
                if not finish[i] and all(self.need[i][j] <= work[j] for j in range(self.m)):
                    for j in range(self.m):
                        work[j] += self.allocation[i][j]
                    finish[i] = True
                    changed = True
        deadlocked = [f"P{i}" for i in range(self.n) if not finish[i]]
        return {
            "deadlock": len(deadlocked) > 0,
            "deadlocked_processes": deadlocked,
            "message": f"🔴 Deadlocked: {deadlocked}" if deadlocked else "✅ No deadlock detected",
        }

    def get_state(self):
        return {
            "available": self.available,
            "max": self.max_matrix,
            "allocation": self.allocation,
            "need": self.need,
            "processes": self.n,
            "resources": self.m,
        }


# ─────────────────────────────────────────────
# 5. FILE SYSTEM
# ─────────────────────────────────────────────

class FileNode:
    def __init__(self, name, is_dir=False, content=""):
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {} if is_dir else None
        self.size = len(content)
        self.created_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.modified_at = self.created_at
        self.permissions = "rw-r--r--"

    def to_dict(self, path=""):
        d = {
            "name": self.name,
            "type": "directory" if self.is_dir else "file",
            "size": self.size if not self.is_dir else sum(c.size for c in (self.children or {}).values()),
            "created_at": self.created_at,
            "permissions": self.permissions,
            "path": path + "/" + self.name,
        }
        if self.is_dir:
            d["children"] = [c.to_dict(path + "/" + self.name) for c in self.children.values()]
        return d


class FileSystem:
    def __init__(self):
        self.root = FileNode("/", is_dir=True)
        self.current_path = [self.root]
        self.log = []
        self._init_structure()

    def _init_structure(self):
        self.mkdir("home")
        self.mkdir("bin")
        self.mkdir("etc")
        self.mkdir("var")
        self.cd("home")
        self.mkdir("user")
        self.cd("user")
        self.create_file("readme.txt", "Welcome to OS Simulator!")
        self.create_file("notes.txt", "Operating Systems Project")
        self.cd("..")
        self.cd("..")

    def _current_dir(self):
        return self.current_path[-1]

    def pwd(self):
        return "/" + "/".join(n.name for n in self.current_path[1:])

    def mkdir(self, name):
        if name in self._current_dir().children:
            return False, "Directory already exists"
        self._current_dir().children[name] = FileNode(name, is_dir=True)
        self.log.append(f"mkdir {name} in {self.pwd()}")
        return True, f"Created directory '{name}'"

    def create_file(self, name, content=""):
        if name in self._current_dir().children:
            return False, "File already exists"
        self._current_dir().children[name] = FileNode(name, content=content)
        self.log.append(f"create {name} in {self.pwd()}")
        return True, f"Created file '{name}'"

    def read_file(self, name):
        node = self._current_dir().children.get(name)
        if not node:
            return None, "File not found"
        if node.is_dir:
            return None, "Is a directory"
        return node.content, "OK"

    def write_file(self, name, content):
        node = self._current_dir().children.get(name)
        if not node:
            self.create_file(name, content)
        else:
            node.content = content
            node.size = len(content)
            node.modified_at = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log.append(f"write {name}")
        return True, "Written"

    def delete(self, name):
        if name not in self._current_dir().children:
            return False, "Not found"
        del self._current_dir().children[name]
        self.log.append(f"delete {name}")
        return True, f"Deleted '{name}'"

    def ls(self):
        return list(self._current_dir().children.keys())

    def cd(self, name):
        if name == "..":
            if len(self.current_path) > 1:
                self.current_path.pop()
            return True, self.pwd()
        node = self._current_dir().children.get(name)
        if node and node.is_dir:
            self.current_path.append(node)
            return True, self.pwd()
        return False, f"No such directory: {name}"

    def tree(self):
        return self.root.to_dict()

    def get_snapshot(self):
        return {
            "pwd": self.pwd(),
            "ls": self.ls(),
            "tree": self.tree(),
            "log": self.log[-10:],
        }


# ─────────────────────────────────────────────
# 6. PRODUCER-CONSUMER (Synchronization)
# ─────────────────────────────────────────────

class ProducerConsumerSimulator:
    def __init__(self, buffer_size=5):
        self.buffer_size = buffer_size
        self.buffer = []
        self.mutex = threading.Lock()
        self.empty = threading.Semaphore(buffer_size)
        self.full = threading.Semaphore(0)
        self.log = []
        self.produced = 0
        self.consumed = 0
        self.running = False

    def produce(self, item):
        acquired = self.empty.acquire(timeout=1)
        if not acquired:
            self.log.append(f"⏳ Producer blocked – buffer full")
            return False
        with self.mutex:
            self.buffer.append(item)
            self.produced += 1
            self.log.append(f"📦 Produced: {item} | Buffer: {list(self.buffer)}")
        self.full.release()
        return True

    def consume(self):
        acquired = self.full.acquire(timeout=1)
        if not acquired:
            self.log.append(f"⏳ Consumer blocked – buffer empty")
            return None
        with self.mutex:
            item = self.buffer.pop(0)
            self.consumed += 1
            self.log.append(f"✅ Consumed: {item} | Buffer: {list(self.buffer)}")
        self.empty.release()
        return item

    def simulate(self, num_produce=8, num_consume=8):
        self.log = []
        self.produced = 0
        self.consumed = 0
        self.buffer = []
        self.empty = threading.Semaphore(self.buffer_size)
        self.full = threading.Semaphore(0)

        items = [f"item_{i+1}" for i in range(num_produce)]
        threads = []

        def producer_task():
            for item in items:
                time.sleep(random.uniform(0.01, 0.05))
                self.produce(item)

        def consumer_task():
            for _ in range(num_consume):
                time.sleep(random.uniform(0.02, 0.07))
                self.consume()

        p = threading.Thread(target=producer_task)
        c = threading.Thread(target=consumer_task)
        threads = [p, c]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)

        return {
            "buffer_size": self.buffer_size,
            "produced": self.produced,
            "consumed": self.consumed,
            "final_buffer": list(self.buffer),
            "log": self.log,
        }

    def get_state(self):
        return {
            "buffer": list(self.buffer),
            "buffer_size": self.buffer_size,
            "produced": self.produced,
            "consumed": self.consumed,
            "log": self.log[-10:],
        }


# ─────────────────────────────────────────────
# OS SIMULATOR - MAIN CLASS
# ─────────────────────────────────────────────

class OSSimulator:
    def __init__(self):
        self.memory_manager = MemoryManager(total_memory=4096, page_size=256)
        self.page_replacer = PageReplacer(num_frames=4)
        self.file_system = FileSystem()
        self.sync_simulator = ProducerConsumerSimulator(buffer_size=5)
        self.process_pool = []

    def create_processes(self, n=5):
        Process._id_counter = 1
        self.process_pool = []
        for i in range(n):
            p = Process(
                name=f"P{i+1}",
                burst_time=random.randint(2, 12),
                priority=random.randint(1, 5),
                arrival_time=random.randint(0, 5),
                memory_required=random.randint(64, 512),
            )
            self.process_pool.append(p)
        return [p.to_dict() for p in self.process_pool]

    def run_scheduling(self, algorithm="Round Robin", quantum=3):
        import copy
        procs = [copy.deepcopy(p) for p in self.process_pool]
        algo_map = {
            "FCFS": SchedulingAlgorithm.FCFS,
            "SJF": SchedulingAlgorithm.SJF,
            "Priority": SchedulingAlgorithm.PRIORITY,
            "Round Robin": SchedulingAlgorithm.ROUND_ROBIN,
        }
        scheduler = ProcessScheduler(algorithm=algo_map.get(algorithm, SchedulingAlgorithm.ROUND_ROBIN), quantum=quantum)
        for p in procs:
            scheduler.add_process(p)
        return scheduler.run()

    def run_memory(self):
        self.memory_manager = MemoryManager(total_memory=4096, page_size=256)
        results = []
        for p in self.process_pool[:4]:
            ok = self.memory_manager.allocate(p)
            results.append({"process": p.name, "success": ok})
        return {"allocations": results, "snapshot": self.memory_manager.get_snapshot()}

    def run_page_replacement(self, ref_string=None):
        if not ref_string:
            ref_string = [random.randint(0, 7) for _ in range(20)]
        return {
            "reference_string": ref_string,
            "results": self.page_replacer.compare_all(ref_string),
        }

    def run_deadlock(self):
        n, m = 5, 3
        available = [3, 3, 2]
        max_m = [[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]]
        alloc  = [[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
        dm = DeadlockManager(n, m, available, max_m, alloc)
        safety = dm.is_safe()
        detect = dm.detect_deadlock()
        req_result = dm.request_resources(1, [1, 0, 2])
        return {
            "state": dm.get_state(),
            "safety_check": safety,
            "deadlock_detection": detect,
            "resource_request": req_result,
        }

    def run_sync(self):
        return self.sync_simulator.simulate(num_produce=8, num_consume=8)

    def run_filesystem(self):
        self.file_system.mkdir("projects")
        self.file_system.cd("projects")
        self.file_system.create_file("os_project.py", "# OS Simulator")
        self.file_system.write_file("os_project.py", "# Full OS Simulator\nprint('Running...')")
        content, _ = self.file_system.read_file("os_project.py")
        self.file_system.cd("..")
        return {
            "snapshot": self.file_system.get_snapshot(),
            "sample_read": content,
        }

    def run_all(self):
        self.create_processes(5)
        return {
            "scheduling": {
                "fcfs": self.run_scheduling("FCFS"),
                "sjf": self.run_scheduling("SJF"),
                "priority": self.run_scheduling("Priority"),
                "round_robin": self.run_scheduling("Round Robin", quantum=3),
            },
            "memory": self.run_memory(),
            "page_replacement": self.run_page_replacement(),
            "deadlock": self.run_deadlock(),
            "sync": self.run_sync(),
            "filesystem": self.run_filesystem(),
        }


if __name__ == "__main__":
    import json
    sim = OSSimulator()
    results = sim.run_all()
    print(json.dumps(results, indent=2, default=str))
    print("\n✅ OS Simulator ran successfully!")
