import sys
import numpy as np

class SudokuBoard:
    def __init__(self):
        self.possibilities = np.ones([9,9,9],"L")
        self.known_values = np.zeros([9,9],"L")                   
    
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

    def run_exclusion_tests(self):

        # create mask patterns in the 9x9x9 possibilites grid (do this once)
        # 81 column possibilities
        # 81 neighborhood possibilities

        self.masks = []
        zero = np.zeros([9,9,9],"L")
        
        # 81 row possibilities
        for stack in range(9):
            for row in range(9):
                mask = zero.copy()
                mask[row,:,stack] = 1
                assert(mask.sum() == 9)
                self.masks.append(mask)
        # 81 column possibilities
        for stack in range(9):
            for col in range(9):
                mask = zero.copy()
                mask[:,col,stack] = 1
                assert(mask.sum() == 9)
                self.masks.append(mask)
        # 81 stack possibilites
        for row in range(9):
            for col in range(9):
                mask = zero.copy()
                mask[row,col,:]=1
                assert(mask.sum() == 9)
                self.masks.append(mask)
        # 81 neighborhood possibilities
        for stack in range(9):
            for super_row in range(3):
                for super_col in range(3):
                    mask = zero.copy()
                    mask[super_row*3:(super_row+1)*3,super_col*3:(super_col+1)*3,stack] = 1
                    assert(mask.sum() == 9)
                    self.masks.append(mask)

        #this is where we store the confirmed possibilities of each test, using logical OR 
        # operations (more than one rule can confirm a possibility)
        confirmed_possibilities = np.zeros([9,9,9],dtype=bool)

        #for each of the 243 stamp and sum the matrix
        for mask in self.masks:
            masked_possibities = self.possibilities * mask
        
            #if sum is 1, logically OR the confirmation matrix
            if np.sum(masked_possibities) == 1:
                np.logical_or(confirmed_possibilities,masked_possibities,confirmed_possibilities)
        
        # squash back to a 2D grid with confirmed values
        stack_of_values = np.asarray([1,2,3,4,5,6,7,8,9],"L").reshape([1,1,9])
        confirmed_possibilities_values = confirmed_possibilities.astype(int) * stack_of_values
        confirmed_values = np.sum(confirmed_possibilities_values,2).astype(int)

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
    
    