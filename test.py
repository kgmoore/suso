import sys
import numpy as np

class SudokuBoard:
    def __init__(self):
        self.possibilities = np.ones([9,9,9],"L")
        self.known_values = np.zeros([9,9],"L")
        # for row in range(9):
        #     for col in range(9):
        #         for slice in range(9):
        #             self.possibilities[row][col][slice] += 0.0100*row
        #             self.possibilities[row][col][slice] += 0.0010*col
        #             self.possibilities[row][col][slice] += 0.0001*slice
                    
    
    def import_file(self, fileObj):
        for i in range(9):
            line = fileObj.readline()
            for j in range(9):
                if line[j] == "*":
                    continue
                else:
                    self.apply_known_value(i,j,int(line[j]))

    def print_board_old_code(self):
        board_string = ""
        board_string += "-"*(3*3 + 4) + "\n"
        for super_row in range(3):
            for row in range(3):
                board_string += "|"
                for super_col in range(3):
                    for col in range(3):
                        board_string += f"{self.current_state[super_row*3+row][super_col*3+col]}"
                    board_string += "|"
                board_string += "\n"
            board_string += "-"*(3*3 + 4) + "\n"
        return board_string
    
    def print_board(self):
        board_string = ""
        for slice in range(9):
            #board_string += f"** Possibilities Slice Value {slice+1} **\n"
            #board_string += np.array2string(self.possibilities[:,:,slice],max_line_width=120,precision=4)
            #board_string += "\n"
            continue
        
        #board_string += f"**** Known Values ****\n"
        board_string += np.array2string(self.known_values,max_line_width=120,precision=4) 
        return board_string
    
    def possibilities_sum(self):
        return np.sum(self.possibilities)
    
    def filled_cells(self):
        return np.sum(self.known_values != np.zeros([9,9],"L"))
    
    def unfilled_cells(self):
        return np.sum(self.known_values == np.zeros([9,9],"L"))
    
    def apply_known_value(self, row, col, value):
        
        assert(row < 9)
        assert(col < 9)
        assert(value <= 9)
        assert(value >= 1)

        super_row = row // 3
        super_col = col // 3

        pre_size = np.sum(self.possibilities)

        # step one - clear out column
        self.possibilities[row,:,value-1] = 0
        # step two - clear out row
        self.possibilities[:,col,value-1] = 0
        # step three - clear out z stack
        self.possibilities[row,col,:] = 0 
        # step four - clear out neighborhood
        self.possibilities[super_row*3:(super_row+1)*3,super_col*3:(super_col+1)*3,value-1] = 0
        # step five - replace the "one" value in the correct cell
        self.known_values[row,col] = value

    def apply_exclusion_tests(self):
        confirmed_values = self.run_exclusion_tests()

        #iterate over each one and apply it if non zero
        iter = np.nditer(confirmed_values,["multi_index"],["readonly"])

        for value in iter:
            #print("%d <%s>" % (value, iter.multi_index), end=' ')
            if value != 0:
                self.apply_known_value(iter.multi_index[0],iter.multi_index[1],value)

        post_size = np.sum(self.possibilities)

    def run_exclusion_tests(self):
        # exclusion tests means we look in each dimension of the possibilities cube for 1 and only 1 value in a dimension
        # one and only one in a row means we know the value (basic sudoku rule #1 - rows)
        # one and only one in a col means we know the value (basic sudoku rule #2 - columns)
        # one and only one in a stack means we know the value (basic elimination)

        axis_names = {0:"row",1:"col",2:"stack"}

        confirmed_possibilities = np.zeros([9,9,9],dtype=bool)

        for axis_to_test in [0,1,2]:
            test_result = np.sum(self.possibilities,axis = axis_to_test) == np.ones([9,9],"L")
            test_result_count = np.sum(test_result)
            #print(f"There are {test_result_count} known values from the {axis_names[axis_to_test]} test.")
            
            # now we need to get the 9x9 sum matrix back into a 1x9x9, 9x1x9, or 9x9x1 matrix so that we can
            # broadcast it across the possibility cube for filtering 
            repack_shape_template = [9,9,9]
            repack_shape = repack_shape_template.copy()
            repack_shape[axis_to_test] = 1
            repack_test_result = np.reshape(test_result, repack_shape)
            
            # now expand it back to a 9x9x9 through replication (cells of "1" become vectors of "1")
            broadcast_test_result = np.broadcast_to(repack_test_result,[9,9,9])

            # now multiply to take only confirmed possibilities
            partial_confirmed_possibilities = broadcast_test_result * self.possibilities
            
            # check to make sure that no additional cells were selected
            test_result_count_check = np.sum(partial_confirmed_possibilities)
            assert(test_result_count-test_result_count_check==0)

            # boolean accumulation of partial possibilities
            partial_confirmed_possibilities_bool = partial_confirmed_possibilities.astype(bool)
            np.logical_or(confirmed_possibilities,partial_confirmed_possibilities_bool,confirmed_possibilities)
            #print(f"There are {np.sum(partial_confirmed_possibilities_bool.astype(int))} from this partial test.")
            #print(f"There are {np.sum(confirmed_possibilities.astype(int))} from all tests to date.")


        #print(f"There are {np.sum(confirmed_possibilities.astype(int))} known values from all tests.")

        # squash back to a 2D grid with values
        stack_of_values = np.asarray([1,2,3,4,5,6,7,8,9],"L").reshape([1,1,9])
        confirmed_possibilities_values = confirmed_possibilities.astype(int) * stack_of_values
        confirmed_values = np.sum(confirmed_possibilities_values,2).astype(int)
        #print(np.array2string(confirmed_values,max_line_width=120,precision=4))

        return confirmed_values

    def tuple_elimination_tests(self):
        # apply the idea that if two cells in a set have only A and B as possibilities, then no
        # other cell in the set can have A and B as possibilities. Example: if cell 1:(A,B), cell 2(A,B),
        # and cell 3(A,B,C) then cell 3 must be actualy by C since cell 1 and cell 2 "need" the A and B
        
        #don't know how to code this yet ;)
        pass


if __name__ == "__main__":        
        
    board_file = open(sys.argv[1])

    iteration_count = 0
    the_board = SudokuBoard()

    the_board.import_file(board_file)

    while(True):
        iteration_count += 1
        initial_filled_cells = the_board.filled_cells()
        print(f"***** Iteration {iteration_count} ******")
        print(f"[Filled:{the_board.filled_cells()}]")
        print(f"[Unfilled:{the_board.unfilled_cells()}]")
        print(f"[Possibilies:{the_board.possibilities_sum()}]")
        print(f"The Board:")
        print(the_board.print_board())

        the_board.apply_exclusion_tests()
        current_filled_cells = the_board.filled_cells()

        if initial_filled_cells == current_filled_cells:
            print(f"no cells were filled in in this iteration. Exiting.")
            break
    
    