import unittest
import suso
import numpy as np

class TestSuso(unittest.TestCase):

    def test_numpy_broadcasting(self):
        d2 = np.zeros([9,9],dtype=np.uint)
        d2[2][3] = 6
        d2[4][5] = 20

        d3 = d2.reshape([9,9,1]) * np.ones([9,9,9],dtype=np.uint)

        for i in range(9):
            self.assertTrue(d3[2][3][i] == d2[2][3])
            self.assertTrue(d3[4][5][i] == d2[4][5])
            
    def test_stack_counting(self):
        possibilities = np.zeros([3,3,3],dtype=np.uint)
        # the [0,0] cell has two possibilities (value = 0 or 1) 
        possibilities[0][0][0] = 1
        possibilities[0][0][1] = 1
        # the [1,1] cell has one possibility (value = 1)        
        possibilities[1][1][1] = 1
        self.assertEqual(np.sum(possibilities),3, "correct number not set")

        known_cells = (np.sum(possibilities,axis=2) == np.ones([3,3],dtype=np.uint))
        self.assertEqual(known_cells[0][0],False,"Cell (0,0) not flagged false")
        self.assertEqual(known_cells[1][1],True, "Cell (1,1) not flagged true")

    def test_apply_known_value_one(self):
        # basic test
        test_board = suso.SudokuBoard()
        test_board.apply_known_value(2,3,1)
        result_array = test_board.get_board()
        expected_array = np.zeros([9,9],dtype=np.uint)
        expected_array[2][3] = 1
        self.assertTrue(np.array_equal(result_array, expected_array), 'The single known element board is wrong')

    def test_apply_known_value_overwrite(self):
        # overwrite test
        test_board = suso.SudokuBoard()
        test_board.apply_known_value(2,3,1)
        test_board.apply_known_value(2,3,3)
        result_array = test_board.get_board()
        expected_array = np.zeros([9,9],dtype=np.uint)
        expected_array[2][3] = 3
        self.assertTrue(np.array_equal(result_array, expected_array), 'The overwrite element board is wrong')

    def test_apply_known_value_triple(self):
        # three element test
        test_board = suso.SudokuBoard()
        test_board.apply_known_value(2,3,1)
        test_board.apply_known_value(8,8,8)
        test_board.apply_known_value(3,4,5)
        result_array = test_board.get_board()
        expected_array = np.zeros([9,9],dtype=np.uint)
        expected_array[2][3] = 1
        expected_array[8][8] = 8
        expected_array[3][4] = 5
        self.assertTrue(np.array_equal(result_array, expected_array), 'The triple element board is wrong')

    def test_possibilities_to_known_values_simple(self):
        possibilities = np.zeros([9,9,9],dtype=np.uint)
        possibilities[3][3][4] = 1 # stack index 4 means value == 5

        expected_values = np.zeros([9,9],dtype=np.uint)
        expected_values[3][3] = 5

        known_values = suso.SudokuBoard.convert_possibilities_to_known_values(possibilities)
        self.assertTrue(np.array_equal(known_values,expected_values), "known and expected don't match")

    def test_find_implied_values_simple(self):  
        # fill in the first row except the last cell, counting 1 to 8
        known_values = np.zeros([9,9],dtype=np.uint)
        for i in range(8):
            known_values[0][i] = i+1

        # check for the implied last cell in first row
        implied_values = suso.SudokuBoard.find_implied_cells(known_values)
        self.assertEqual(implied_values[0][8],9,"The last cell of the first row was not found")
        
        # fill in the first col except the last cell, counting 1 to 8
        known_values = np.zeros([9,9],dtype=np.uint)
        for i in range(8):
            known_values[i][0] = i+1

        # check for the implied last cell in first col
        implied_values = suso.SudokuBoard.find_implied_cells(known_values)
        self.assertEqual(implied_values[8][0],9,"The last cell of the first col was not found")

        # fill in the first neighborhood except the last cell, counting 1 to 8
        known_values = np.zeros([9,9],dtype=np.uint)
        for i in range(8):
            row = i // 3
            col = i %  3
            known_values[row][col] = i+1

        # check for the implied last cell in first neighborhood
        implied_values = suso.SudokuBoard.find_implied_cells(known_values)
        self.assertEqual(implied_values[2][2],9,"The last cell of the first neighborhood was not found")

    def test_implied_values_string(self):
        board_string =    '040100050107003960520008000000000017000906800803050620090060543600080700250097100'
        solution_string = '346179258187523964529648371965832417472916835813754629798261543631485792254397186'
        
        board = suso.SudokuBoard()
        board.initialize_board_from_string(board_string)
        known_values = board.get_board()
        
        # check for the implied last cell in first neighborhood
        implied_values = suso.SudokuBoard.find_implied_cells(known_values)
        for row in range(9):
            for col in range(9):
                solution_value = int(solution_string[row*9+col])
                implied_value = implied_values[row][col]
                if implied_value != 0:
                    self.assertEqual(implied_value,
                                     solution_value,
                                     f"inferred the wrong cell at ({row},{col}) was {implied_value} expected {solution_value}")

    def test_implied_values_string_hard(self):
        board_string    = '473605109891070526600000403000568902200713654500492008754836291900200365362159847'
        solution_string = '473625189891374526625981473147568932289713654536492718754836291918247365362159847'

        board = suso.SudokuBoard()
        board.initialize_board_from_string(board_string)
        starting = board.filled_cells()
        board.apply_constraints_iteratively()
        ending = board.filled_cells()
        self.assertNotEqual(starting, ending, "Constraints failed to process")

    def test_validity_simple(self):

        board_string = '002100049400900800800060320700080005050000001063004700201050670006719050080002000'

        board = suso.SudokuBoard()
        board.initialize_board_from_string(board_string)
        self.assertTrue(board.valid())
        board.apply_known_value(1,2,6)
        self.assertFalse(board.valid())
    
        board = suso.SudokuBoard()
        board.initialize_board_from_string(board_string)
        board.apply_known_value(1,2,6)
        self.assertFalse(board.valid())

    def test_guessing_simple(self):
        board_string = '002100049400900800800060320700080005050000001063004700201050670006719050080002000'
        board = suso.SudokuBoard()
        board.initialize_board_from_string(board_string)
        possibilities = suso.SudokuBoard.convert_known_values_to_possibilities(board.known_values)
        guesses = suso.SudokuBoard.convert_possibilities_to_guesses(possibilities)
        self.assertEqual(guesses[0],(0,0,3),"First guess did not match expected")
    
    def test_guessing_to_invalidity(self):
        
        # load a hard board and advance it
        board_string = '002100049400900800800060320700080005050000001063004700201050670006719050080002000'
        board = suso.SudokuBoard()
        board.initialize_board_from_string(board_string)
        board.apply_constraints_iteratively()

        while board.valid():
            # print(f"*** Board has {board.filled_cells()} filled cells.***")
            # print(board.print_board())
            possibilities = suso.SudokuBoard.convert_known_values_to_possibilities(board.known_values)
            guesses = suso.SudokuBoard.convert_possibilities_to_guesses(possibilities)
            guess = guesses[0]
            # print(f"Old Board Possibilities:")
            # print(suso.SudokuBoard.print_possibilities(possibilities))
            # print(f"\tApplying guess {guess}")
            board.apply_known_value(guess[0],guess[1],guess[2])
            # print(f"\tBoard validity is {board.valid()}")
            
            # possibilities = suso.SudokuBoard.convert_known_values_to_possibilities(board.known_values)
            # print(f"New Board Possibilities:")
            # print(suso.SudokuBoard.print_possibilities(possibilities))
            
            # print(f"\tApplying iterative contraints")
            board.apply_constraints_iteratively()
            # print(f"\tBoard now has has {board.filled_cells()} filled cells.")
            # print(f"\tBoard validity is {board.valid()}")
                
        # possibilities = suso.SudokuBoard.convert_known_values_to_possibilities(board.known_values)
        # print(suso.SudokuBoard.print_possibilities(possibilities))
        self.assertFalse(board.valid())
            
    def test_evaluating_all_guesses(self):
         # load a hard board and advance it
        board_string = '002100049400900800800060320700080005050000001063004700201050670006719050080002000'
        board = suso.SudokuBoard()
        board.initialize_board_from_string(board_string)
        board.apply_constraints_iteratively()

        guesser = suso.SudokuGuesser()
        guesser.add_board(board,None,None)
        (solution,good_guesses) = guesser.process_board(board.print_board_string())

        self.assertIsNotNone(solution, "checking all guesses did not yield a solution")

        solved









                



if __name__ == "__main__":
    try:
        unittest.main()
    except SystemExit:
        print(f"Caught exception. Exiting.")
