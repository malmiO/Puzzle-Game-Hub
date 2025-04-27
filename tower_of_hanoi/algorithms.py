import time

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
    
    start_time = time.time()
    hanoi(n, source, auxiliary, destination)
    end_time = time.time()
    
    return moves, end_time - start_time

# Classic 3-peg Tower of Hanoi iterative solution
def solve_hanoi_iterative(n, source, auxiliary, destination):
    moves = []
    start_time = time.time()
    
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
    
    end_time = time.time()
    return moves, end_time - start_time

# Frame-Stewart algorithm for 4 pegs
def solve_frame_stewart(n, source, aux1, aux2, destination):
    moves = []
    start_time = time.time()
    
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
    end_time = time.time()
    
    return moves, end_time - start_time