"""
OS Simulator — Main Entry Point
================================
Graduation Project: Operating Systems Simulation
Run this file to execute all modules and see results.
"""

import json
import sys
from os_core import (
    OSSimulator, Process, ProcessScheduler, SchedulingAlgorithm,
    MemoryManager, PageReplacer, DeadlockManager, FileSystem,
    ProducerConsumerSimulator
)

DIVIDER = "=" * 60

def print_section(title):
    print(f"\n{DIVIDER}")
    print(f"  {title}")
    print(DIVIDER)

def demo_scheduling():
    print_section("1. PROCESS SCHEDULING")
    algorithms = [
        SchedulingAlgorithm.FCFS,
        SchedulingAlgorithm.SJF,
        SchedulingAlgorithm.PRIORITY,
        SchedulingAlgorithm.ROUND_ROBIN,
    ]
    processes_data = [
        {"name": "P1", "burst_time": 8,  "priority": 3, "arrival_time": 0},
        {"name": "P2", "burst_time": 4,  "priority": 1, "arrival_time": 1},
        {"name": "P3", "burst_time": 9,  "priority": 2, "arrival_time": 2},
        {"name": "P4", "burst_time": 5,  "priority": 4, "arrival_time": 3},
        {"name": "P5", "burst_time": 2,  "priority": 2, "arrival_time": 4},
    ]
    for algo in algorithms:
        import copy
        procs = [Process(**p) for p in processes_data]
        scheduler = ProcessScheduler(algorithm=algo, quantum=3)
        for p in procs:
            scheduler.add_process(p)
        result = scheduler.run()
        print(f"\n  [{algo.value}]")
        print(f"  Avg Waiting Time  : {result['avg_waiting_time']}")
        print(f"  Avg Turnaround    : {result['avg_turnaround_time']}")
        gantt_str = " → ".join(f"{g['process']}({g['start']}-{g['end']})" for g in result['gantt'][:8])
        print(f"  Gantt (first 8)   : {gantt_str}")

def demo_memory():
    print_section("2. MEMORY MANAGEMENT (Paging)")
    mem = MemoryManager(total_memory=4096, page_size=256)
    processes = [
        Process("P1", memory_required=512),
        Process("P2", memory_required=768),
        Process("P3", memory_required=256),
    ]
    for p in processes:
        ok = mem.allocate(p)
        status = "✅ Allocated" if ok else "❌ Failed"
        print(f"  {status}: {p.name} needs {p.memory_required}KB → frames {p.allocated_frames}")

    snap = mem.get_snapshot()
    print(f"\n  Total Frames  : {snap['total_frames']}")
    print(f"  Used Frames   : {snap['used_frames']}")
    print(f"  Free Frames   : {snap['free_frames']}")
    print(f"  Utilization   : {snap['utilization']}%")

    # Address translation
    p = processes[0]
    for addr in [0, 300, 510]:
        phys, msg = mem.translate_address(p.pid, addr)
        print(f"\n  Translate [{p.name}] Logical {addr}: {msg}")

def demo_page_replacement():
    print_section("3. PAGE REPLACEMENT ALGORITHMS")
    ref = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 0, 3, 2, 1, 2, 0, 1, 7]
    print(f"  Reference String : {ref}")
    print(f"  Number of Frames : 4\n")
    pr = PageReplacer(num_frames=4)
    results = pr.compare_all(ref)
    for r in results:
        hit_rate = round(r['hits'] / len(ref) * 100, 1)
        bar = "█" * r['hits'] + "░" * r['faults']
        print(f"  {r['algorithm']:8s} | Faults: {r['faults']:2d} | Hits: {r['hits']:2d} | Hit Rate: {hit_rate}% | {bar}")

def demo_deadlock():
    print_section("4. DEADLOCK — BANKER'S ALGORITHM")
    dm = DeadlockManager(
        num_processes=5,
        num_resources=3,
        available=[3, 3, 2],
        max_matrix=[[7,5,3],[3,2,2],[9,0,2],[2,2,2],[4,3,3]],
        allocation_matrix=[[0,1,0],[2,0,0],[3,0,2],[2,1,1],[0,0,2]]
    )
    safety = dm.is_safe()
    print(f"\n  Safety Check    : {'✅ SAFE' if safety['safe'] else '❌ UNSAFE'}")
    if safety['safe']:
        print(f"  Safe Sequence   : {' → '.join(safety['safe_sequence'])}")

    detection = dm.detect_deadlock()
    print(f"\n  Deadlock Check  : {detection['message']}")

    print(f"\n  Resource Request by P1: [1, 0, 2]")
    req = dm.request_resources(1, [1, 0, 2])
    print(f"  Result          : {'✅ Granted' if req['granted'] else '❌ Denied'} — {req['message']}")

def demo_filesystem():
    print_section("5. FILE SYSTEM")
    fs = FileSystem()
    print(f"\n  PWD: {fs.pwd()}")
    print(f"  LS : {fs.ls()}")

    fs.mkdir("projects")
    fs.cd("projects")
    fs.create_file("main.py", "# OS Simulator\nprint('Running...')")
    fs.create_file("report.txt", "Graduation Project Report")

    print(f"\n  After creating files in /projects:")
    print(f"  PWD: {fs.pwd()}")
    print(f"  LS : {fs.ls()}")

    content, _ = fs.read_file("main.py")
    print(f"\n  Read main.py:\n    {content}")

    fs.write_file("report.txt", "Updated: OS Simulation Complete!")
    content2, _ = fs.read_file("report.txt")
    print(f"\n  After write to report.txt:\n    {content2}")

    fs.delete("report.txt")
    print(f"\n  After delete report.txt, LS: {fs.ls()}")

def demo_sync():
    print_section("6. PRODUCER-CONSUMER (Synchronization)")
    print("\n  Buffer Size: 5 | Items to produce/consume: 8")
    sim = ProducerConsumerSimulator(buffer_size=5)
    result = sim.simulate(num_produce=8, num_consume=8)
    print(f"\n  Produced  : {result['produced']}")
    print(f"  Consumed  : {result['consumed']}")
    print(f"  Final Buffer: {result['final_buffer']}")
    print(f"\n  Log (last 6 entries):")
    for line in result['log'][-6:]:
        print(f"    {line}")

def main():
    print("\n" + "█" * 60)
    print("  OS SIMULATOR — Operating Systems Graduation Project")
    print("█" * 60)
    print("  Modules: Scheduling | Memory | Paging | Deadlock | FS | Sync")

    demo_scheduling()
    demo_memory()
    demo_page_replacement()
    demo_deadlock()
    demo_filesystem()
    demo_sync()

    print(f"\n{DIVIDER}")
    print("  ✅ All modules completed successfully!")
    print(f"  📊 Open os_simulator_dashboard.html in browser for visual demo")
    print(DIVIDER + "\n")

if __name__ == "__main__":
    main()
