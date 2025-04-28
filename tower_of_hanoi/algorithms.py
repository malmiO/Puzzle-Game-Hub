import time
from timeit import default_timer as timer
import matplotlib.pyplot as plt

# Classic 3-peg Tower of Hanoi recursive solution
def solve_hanoi_recursive(n, source, auxiliary, destination):
    moves = []
    
    def hanoi(n, source, auxiliary, destination):
        if n == 1:
            moves.append(f"{source}->{destination}")
            return
        hanoi(n-1, source, destination, auxiliary)
        moves.append(f"{source}->{destination}")
        hanoi(n-1, auxiliary, source, destination)
    
    start_time = timer()
    hanoi(n, source, auxiliary, destination)
    end_time = timer()
    
    return moves, end_time - start_time

# Classic 3-peg Tower of Hanoi iterative solution
def solve_hanoi_iterative(n, source, auxiliary, destination):
    moves = []
    start_time = timer()
    
    # If n is even, swap auxiliary and destination
    if n % 2 == 0:
        auxiliary, destination = destination, auxiliary
    
    total_moves = (1 << n) - 1  # 2^n - 1
    
    for i in range(1, total_moves + 1):
        if i % 3 == 1:
            # Move between source and destination
            if not moves or moves[-1].startswith(destination) and moves[-1].endswith(source):
                moves.append(f"{source}->{destination}")
            else:
                moves.append(f"{destination}->{source}")
        elif i % 3 == 2:
            # Move between source and auxiliary
            if not moves or moves[-1].startswith(auxiliary) and moves[-1].endswith(source):
                moves.append(f"{source}->{auxiliary}")
            else:
                moves.append(f"{auxiliary}->{source}")
        else:
            # Move between auxiliary and destination
            if not moves or moves[-1].startswith(destination) and moves[-1].endswith(auxiliary):
                moves.append(f"{auxiliary}->{destination}")
            else:
                moves.append(f"{destination}->{auxiliary}")
    
    end_time = timer()
    return moves, end_time - start_time

# Frame-Stewart algorithm for 4 pegs
def solve_frame_stewart(n, source, aux1, aux2, destination):
    moves = []
    start_time = timer()
    
    # Calculate k (optimal split for Frame-Stewart)
    k = int(n - (2*n)**(1/2))
    if k < 1:
        k = 1
    
    def frame_stewart_helper(n, source, aux1, aux2, destination):
        if n == 0:
            return
        if n == 1:
            moves.append(f"{source}->{destination}")
            return
            
        # Calculate k for this recursion level
        k = int(n - (2*n)**(1/2))
        if k < 1:
            k = 1
            
        # Move top k disks to aux1
        frame_stewart_helper(k, source, destination, aux2, aux1)
        # Move remaining n-k disks from source to destination using 3 pegs
        three_peg_hanoi(n-k, source, aux1, aux2, destination)
        # Move k disks from aux1 to destination
        frame_stewart_helper(k, aux1, source, aux2, destination)
    
    def three_peg_hanoi(n, source, auxiliary, not_used, destination):
        if n == 0:
            return
        if n == 1:
            moves.append(f"{source}->{destination}")
            return
        three_peg_hanoi(n-1, source, not_used, auxiliary, auxiliary)
        moves.append(f"{source}->{destination}")
        three_peg_hanoi(n-1, auxiliary, source, not_used, destination)
    
    frame_stewart_helper(n, source, aux1, aux2, destination)
    end_time = timer()
    
    return moves, end_time - start_time

# Function to verify that the solutions produce the same move count
def verify_solutions(n):
    recursive_moves, _ = solve_hanoi_recursive(n, 'A', 'B', 'C')
    iterative_moves, _ = solve_hanoi_iterative(n, 'A', 'B', 'C')
    
    print(f"Disks: {n}")
    print(f"Recursive solution: {len(recursive_moves)} moves")
    print(f"Iterative solution: {len(iterative_moves)} moves")
    print(f"Solutions match: {len(recursive_moves) == len(iterative_moves)}")
    
    if n <= 4:  # Only show moves for small values
        print("First few moves (recursive):", recursive_moves[:5])
        print("First few moves (iterative):", iterative_moves[:5])
    
    # For 4 pegs
    frame_stewart_moves, _ = solve_frame_stewart(n, 'A', 'B', 'C', 'D')
    print(f"Frame-Stewart (4 pegs): {len(frame_stewart_moves)} moves")
    
    return len(recursive_moves), len(frame_stewart_moves)

# Function to benchmark algorithm performance
def benchmark():
    disk_sizes = list(range(5, 21, 3))  # [5, 8, 11, 14, 17, 20]
    recursive_times = []
    iterative_times = []
    frame_stewart_times = []
    
    three_peg_moves = []
    four_peg_moves = []
    
    print("\nRunning benchmarks...")
    for n in disk_sizes:
        print(f"\nTesting with {n} disks")
        
        # Get times for recursive solution
        _, rec_time = solve_hanoi_recursive(n, 'A', 'B', 'C')
        recursive_times.append(rec_time)
        print(f"Recursive solution time: {rec_time:.6f} seconds")
        
        # Get times for iterative solution
        _, iter_time = solve_hanoi_iterative(n, 'A', 'B', 'C')
        iterative_times.append(iter_time)
        print(f"Iterative solution time: {iter_time:.6f} seconds")
        
        # Get times for Frame-Stewart algorithm (4 pegs)
        _, fs_time = solve_frame_stewart(n, 'A', 'B', 'C', 'D')
        frame_stewart_times.append(fs_time)
        print(f"Frame-Stewart solution time: {fs_time:.6f} seconds")
        
        # Calculate number of moves
        three_peg_count = 2**n - 1
        three_peg_moves.append(three_peg_count)
        
        # For Frame-Stewart, we'll just measure the actual moves
        fs_moves, _ = solve_frame_stewart(n, 'A', 'B', 'C', 'D')
        four_peg_moves.append(len(fs_moves))
        
        print(f"3-peg moves: {three_peg_count}, 4-peg moves: {len(fs_moves)}")
    
    # Plot timing results
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(disk_sizes, recursive_times, marker='o', label='Recursive (3 pegs)')
    plt.plot(disk_sizes, iterative_times, marker='s', label='Iterative (3 pegs)')
    plt.plot(disk_sizes, frame_stewart_times, marker='^', label='Frame-Stewart (4 pegs)')
    plt.xlabel('Number of Disks')
    plt.ylabel('Time (seconds)')
    plt.title('Algorithm Running Time')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(disk_sizes, three_peg_moves, marker='o', label='3 pegs (2^n - 1)')
    plt.plot(disk_sizes, four_peg_moves, marker='s', label='4 pegs (Frame-Stewart)')
    plt.xlabel('Number of Disks')
    plt.ylabel('Number of Moves')
    plt.title('Number of Moves Required')
    plt.legend()
    plt.grid(True)
    plt.yscale('log')
    
    plt.tight_layout()
    plt.savefig('hanoi_performance.png')
    print("\nPlot saved as 'hanoi_performance.png'")

# Run verification for small examples
for i in range(1, 6):
    verify_solutions(i)
    print()

# Run benchmark
benchmark()

# Example of running a specific test case
n = 15
print(f"\nDetailed test for {n} disks:")
moves_recursive, time_recursive = solve_hanoi_recursive(n, 'A', 'B', 'C')
moves_fs, time_fs = solve_frame_stewart(n, 'A', 'B', 'C', 'D')

print(f"3-peg solution: {len(moves_recursive)} moves in {time_recursive:.6f} seconds")
print(f"4-peg solution: {len(moves_fs)} moves in {time_fs:.6f} seconds")
print(f"Improvement with 4 pegs: {100 * (1 - len(moves_fs)/len(moves_recursive)):.2f}% fewer moves")