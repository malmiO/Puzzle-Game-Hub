import unittest
import sys

# Import game logic functions
def init_game_state(n):
    return {
        'A': list(range(n, 0, -1)),
        'B': [],
        'C': [],
        'D': []
    }

def is_valid_move(state, source, destination):
    # Can't move if source peg is empty
    if not state[source]:
        return False
    # Can always move to empty peg
    if not state[destination]:
        return True
    # Can only place smaller disk (lower number) onto larger disk (higher number)
    top_source = state[source][-1]
    top_dest = state[destination][-1]
    return top_source < top_dest

def apply_move(state, source, destination):
    if is_valid_move(state, source, destination):
        disk = state[source].pop()
        state[destination].append(disk)
        return True
    return False

def is_solved(state, n, destination='C'):
    return len(state[destination]) == n and sorted(state[destination], reverse=True) == state[destination]


class TestHanoiGameLogic(unittest.TestCase):
    """Test cases for Tower of Hanoi game logic"""
    
    def setUp(self):
        # Print the name of the test being run
        print(f"\n{self._testMethodName}: {self._testMethodDoc}")
    
    def test_init_game_state(self):
        """Test game state initialization with different disk counts"""
        # Test with 3 disks
        state_3 = init_game_state(3)
        print(f"State with 3 disks: {state_3}")
        self.assertEqual(state_3['A'], [3, 2, 1])
        self.assertEqual(state_3['B'], [])
        self.assertEqual(state_3['C'], [])
        self.assertEqual(state_3['D'], [])
        
        # Test with 0 disks (edge case)
        state_0 = init_game_state(0)
        print(f"State with 0 disks: {state_0}")
        self.assertEqual(state_0['A'], [])
        self.assertEqual(state_0['B'], [])
        self.assertEqual(state_0['C'], [])
        self.assertEqual(state_0['D'], [])
        
        # Test with larger disk count
        disk_count = 5
        state_5 = init_game_state(disk_count)
        print(f"State with {disk_count} disks: {state_5}")
        self.assertEqual(len(state_5['A']), disk_count)
        self.assertEqual(state_5['A'], list(range(disk_count, 0, -1)))
        print("✓ Test passed!")

    def test_is_valid_move(self):
        """Test move validation logic"""
        # Initialize a test state
        state = {'A': [3, 2], 'B': [4], 'C': [5, 1], 'D': []}
        
        # Valid moves
        print("Testing valid moves:")
        self.assertTrue(is_valid_move(state, 'A', 'B'))  # 2 onto 4
        self.assertTrue(is_valid_move(state, 'A', 'C'))  # 2 onto 1
        self.assertTrue(is_valid_move(state, 'C', 'B'))  # 1 onto 4
        self.assertTrue(is_valid_move(state, 'A', 'D'))  # 2 onto empty peg
        
        # Invalid moves
        print("Testing invalid moves:")
        self.assertFalse(is_valid_move(state, 'B', 'C'))  # 4 onto 1 (larger onto smaller)
        self.assertFalse(is_valid_move(state, 'B', 'A'))  # 4 onto 2 (larger onto smaller)
        
        # Empty source peg
        empty_state = {'A': [], 'B': [3, 2, 1], 'C': [], 'D': []}
        self.assertFalse(is_valid_move(empty_state, 'A', 'B'))  # Empty source
        self.assertFalse(is_valid_move(empty_state, 'C', 'B'))  # Empty source
        self.assertFalse(is_valid_move(empty_state, 'D', 'B'))  # Empty source
        
        # Same source and destination
        self.assertFalse(is_valid_move(state, 'A', 'A'))  # Same peg
        print("✓ Test passed!")

    def test_apply_move(self):
        """Test applying moves to game state"""
        # Set up test state
        state = {'A': [3, 2, 1], 'B': [], 'C': [], 'D': []}
        
        # Apply valid move and check result
        result = apply_move(state, 'A', 'B')
        print(f"After applying move A->B: {state}")
        self.assertTrue(result)
        self.assertEqual(state['A'], [3, 2])
        self.assertEqual(state['B'], [1])
        
        # Apply another valid move
        result = apply_move(state, 'A', 'C')
        print(f"After applying move A->C: {state}")
        self.assertTrue(result)
        self.assertEqual(state['A'], [3])
        self.assertEqual(state['C'], [2])
        
        # Try invalid move
        original_state = {'A': [3], 'B': [1], 'C': [2], 'D': []}
        state_copy = {k: v[:] for k, v in original_state.items()}  # Deep copy
        result = apply_move(state_copy, 'A', 'B')  # 3 onto 1 (invalid)
        print(f"After applying invalid move A->B: {state_copy}")
        self.assertFalse(result)
        self.assertEqual(state_copy, original_state)  # State should be unchanged
        
        # Edge case: empty source peg
        result = apply_move(state, 'D', 'C')  # Empty source
        self.assertFalse(result)
        print("✓ Test passed!")

    def test_is_solved(self):
        """Test puzzle solved detection"""
        # 3 disk puzzle, solved on peg C
        solved_state = {'A': [], 'B': [], 'C': [3, 2, 1], 'D': []}
        print(f"Testing solved state: {solved_state}")
        self.assertTrue(is_solved(solved_state, 3))
        
        # 3 disk puzzle, not solved
        unsolved_state1 = {'A': [3], 'B': [2], 'C': [1], 'D': []}
        print(f"Testing unsolved state: {unsolved_state1}")
        self.assertFalse(is_solved(unsolved_state1, 3))
        
        # 3 disk puzzle, all on B (not the target peg)
        unsolved_state2 = {'A': [], 'B': [3, 2, 1], 'C': [], 'D': []}
        print(f"Testing disks on wrong peg: {unsolved_state2}")
        self.assertFalse(is_solved(unsolved_state2, 3))
        
        # 3 disk puzzle, solved on peg D with custom destination
        solved_state_d = {'A': [], 'B': [], 'C': [], 'D': [3, 2, 1]}
        print(f"Testing solved state on peg D: {solved_state_d}")
        self.assertTrue(is_solved(solved_state_d, 3, destination='D'))
        
        # Edge case: 0 disk puzzle
        empty_state = {'A': [], 'B': [], 'C': [], 'D': []}
        print(f"Testing empty puzzle: {empty_state}")
        self.assertTrue(is_solved(empty_state, 0))
        print("✓ Test passed!")

    def test_move_sequence(self):
        """Test a full sequence of moves for game completion"""
        # Start with 3 disk state
        state = init_game_state(3)
        print(f"Initial state: {state}")
        
        # Apply a known sequence of moves that solves the puzzle
        moves = [
            ('A', 'C'),  # Move disk 1 from A to C
            ('A', 'B'),  # Move disk 2 from A to B
            ('C', 'B'),  # Move disk 1 from C to B
            ('A', 'C'),  # Move disk 3 from A to C
            ('B', 'A'),  # Move disk 1 from B to A
            ('B', 'C'),  # Move disk 2 from B to C
            ('A', 'C')   # Move disk 1 from A to C
        ]
        
        # Apply each move and track state
        for i, (source, target) in enumerate(moves):
            success = apply_move(state, source, target)
            print(f"Move {i+1}: {source}->{target}, Success: {success}, State: {state}")
            self.assertTrue(success)
        
        # Verify puzzle is solved
        self.assertTrue(is_solved(state, 3))
        print("✓ Test passed - puzzle solved with correct sequence!")

    def test_invalid_move_sequence(self):
        """Test invalid moves in a sequence"""
        # Start with 3 disk state
        state = init_game_state(3)
        print(f"Initial state: {state}")
        
        # Try a sequence with an invalid move
        moves = [
            ('A', 'C'),  # Valid: Move disk 1 from A to C
            ('A', 'C')   # Invalid: Can't move disk 2 onto disk 1
        ]
        
        # First move should succeed
        success = apply_move(state, moves[0][0], moves[0][1])
        self.assertTrue(success)
        print(f"Move 1: {moves[0]}, Success: {success}, State: {state}")
        
        # Second move should fail
        success = apply_move(state, moves[1][0], moves[1][1])
        self.assertFalse(success)
        print(f"Move 2: {moves[1]}, Success: {success}, State: {state}")
        
        # Verify state after failed move
        self.assertEqual(state['A'], [3, 2])
        self.assertEqual(state['C'], [1])
        print("✓ Test passed - invalid move correctly rejected!")

    def test_edge_cases(self):
        """Test edge cases in game logic"""
        # Test with 1 disk
        state_1 = init_game_state(1)
        print(f"State with 1 disk: {state_1}")
        
        # Simple move from A to C
        success = apply_move(state_1, 'A', 'C')
        self.assertTrue(success)
        self.assertTrue(is_solved(state_1, 1))
        
        # Test with mixed peg content
        mixed_state = {'A': [5, 3], 'B': [4, 2], 'C': [], 'D': []}
        print(f"Mixed state: {mixed_state}")
        
        # Valid move
        success = apply_move(mixed_state, 'A', 'C')
        self.assertTrue(success)
        self.assertEqual(mixed_state['A'], [5])
        self.assertEqual(mixed_state['C'], [3])
        
        # Another valid move
        success = apply_move(mixed_state, 'B', 'C')
        self.assertTrue(success)
        self.assertEqual(mixed_state['B'], [4])
        self.assertEqual(mixed_state['C'], [3, 2])
        
        # Invalid move
        success = apply_move(mixed_state, 'A', 'C')
        self.assertFalse(success)  # Can't place 5 on top of 2
        
        print("✓ Test passed!")

    def test_custom_destination(self):
        """Test solving with custom destination peg"""
        # Start with 3 disk state
        state = init_game_state(3)
        print(f"Initial state: {state}")
        
        # Sequence to solve on peg D
        moves = [
            ('A', 'D'),  # Move disk 1 from A to D
            ('A', 'B'),  # Move disk 2 from A to B
            ('D', 'B'),  # Move disk 1 from D to B
            ('A', 'D'),  # Move disk 3 from A to D
            ('B', 'A'),  # Move disk 1 from B to A
            ('B', 'D'),  # Move disk 2 from B to D
            ('A', 'D')   # Move disk 1 from A to D
        ]
        
        # Apply each move
        for i, (source, target) in enumerate(moves):
            success = apply_move(state, source, target)
            print(f"Move {i+1}: {source}->{target}, Success: {success}")
            self.assertTrue(success)
        
        # Verify puzzle is solved on peg D
        self.assertTrue(is_solved(state, 3, destination='D'))
        print("✓ Test passed - puzzle solved on custom destination peg!")


def get_test_runner():
    """Return a test runner with verbose output"""
    return unittest.TextTestRunner(verbosity=2, stream=sys.stdout)


if __name__ == '__main__':
    print("=" * 70)
    print("TOWER OF HANOI GAME LOGIC TESTS")
    print("=" * 70)
    
    # Create a test suite with all tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHanoiGameLogic)
    
    # Run the tests with custom runner
    result = get_test_runner().run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"SUMMARY: Ran {result.testsRun} tests")
    print(f"  Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print("=" * 70)
    
    # Exit with appropriate code
    sys.exit(not result.wasSuccessful())