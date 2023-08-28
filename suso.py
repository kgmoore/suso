import sys
import copy
import numpy as np
import hashlib
import time



class SudokuBoard:
    # class variables up here
    # create mask patterns in the 9x9x9 possibilites grid (do this once)
    masks = []
    zero = np.zeros([9,9,9],"L")
    
    # 81 row possibilities
    for stack in range(9):
        for row in range(9):
            mask = zero.copy()
            mask[row,:,stack] = 1
            assert(mask.sum() == 9)
            masks.append(mask)
    # 81 column possibilities
    for stack in range(9):
        for col in range(9):
            mask = zero.copy()
            mask[:,col,stack] = 1
            assert(mask.sum() == 9)
            masks.append(mask)
    # 81 stack possibilites
    for row in range(9):
        for col in range(9):
            mask = zero.copy()
            mask[row,col,:]=1
            assert(mask.sum() == 9)
            masks.append(mask)
    # 81 neighborhood possibilities
    for stack in range(9):
        for super_row in range(3):
            for super_col in range(3):
                mask = zero.copy()
                mask[super_row*3:(super_row+1)*3,super_col*3:(super_col+1)*3,stack] = 1
                assert(mask.sum() == 9)
                masks.append(mask)

    def __init__(self):
        self.known_values = np.zeros([9,9],"L")
        self._creation_hash = ""

    def initialize_board_from_string(self,input_string):
        for row in range(9):
            for col in range(9):
                value = int(input_string[row*9+col])
                self.known_values[row][col] = value

    def format_guess(guess):
        return f"[({guess[0]},{guess[1]})=={guess[2]}]"
    
    def print_board(self):
        grid_string = ""
        for slice in range(9):
            #grid_string += f"** Possibilities Slice Value {slice+1} **\n"
            #grid_string += np.array2string(self.possibilities[:,:,slice],max_line_width=120,precision=4)
            #grid_string += "\n"
            continue
        
        #grid_string += f"**** Known Values ****\n"
        grid_string += np.array2string(self.known_values,max_line_width=120,precision=4) 
        return grid_string
    
    def print_board_string(self):
        return_string = ""
        for row in range(9):
            for col in range(9):
                return_string += str(self.known_values[row][col])
        return return_string

    def print_possibilities(possibilities):
        # +---+---+
        # |123|123|
        # |456|456|
        # |789|789|
        # +---+---+

        retval = ("+---"*9 + "+" + "\n")
            
        for row in range(9):
            row_string = ""
            for stack_major in range(3):
                row_string = "|"
                for col in range(9):
                    for stack_minor in range(3):
                        stack = stack_major*3 + stack_minor
                        if possibilities[row][col][stack] == 1:
                            row_string += str(stack+1)
                        else:
                            row_string += " "
                    row_string += "|"
                retval += (row_string + "\n")
            retval += ("+---"*9 + "+" + "\n")
        
        return retval
        

                        

        
    
    def get_board(self):
        return self.known_values

    def possibilities_sum(self):
        return np.sum(self.possibilities)
    
    def filled_cells(self):
        return np.sum(self.known_values != np.zeros([9,9],"L"))
    
    def unfilled_cells(self):
        return np.sum(self.known_values == np.zeros([9,9],"L"))
    
    def mark_creation_hash(self):
        self._creation_hash = hashlib.sha256(self.known_values.tobytes(), usedforsecurity=False).hexdigest()[0:8]

    def creation_hash(self):
        return self._creation_hash

    def valid(self):
        # a board is valid if there are non-zero possibilities for all cells.
        possibilities = SudokuBoard.convert_known_values_to_possibilities(self.known_values)
        possibility_counts = np.sum(possibilities,axis=2)
        minimum_possibilities = np.min(possibility_counts)
        return (minimum_possibilities != 0)
    

    def guess(self, guess_index):
        # simplest thing that could possibly work: 
        # 1/iterate, row, column, stack.
        # 2/find the ith possibility, clone the board, apply the guess as truth
        # 3/return the new board and the guess signature

        guess_counter = 0
        for row in range(9):
            for col in range(9):
                for stack in range(9):
                    if self.possibilities[row,col,stack] == 1:
                        if guess_counter == guess_index:
                            # make a copy
                            board_copy = copy.deepcopy(self)
                            # apply the guess (turning the "possibility" into known)
                            board_copy.apply_known_value(row,col,stack+1)
                            return (board_copy,(row,col,stack+1))
                        else:
                            guess_counter += 1
        # this means we simply couldn't find enough guesses to satisfy, so return None
        return (None,None)

    # mutating function all below here
    def import_file(self, fileObj):
        for i in range(9):
            line = fileObj.readline()
            for j in range(9):
                if line[j] == "*":
                    continue
                else:
                    self.apply_known_value(i,j,int(line[j]))

    def apply_known_value(self, row, col, value):
        value_type = type(value)
        row_type = type(row)
        assert(type(value) == type(1))
        assert(row < 9)
        assert(col < 9)
        assert(value <= 9)
        assert(value >= 1)

        # step 5A - precheck the board
        # if SudokuBoard.check_board_array(self.known_values) == False:
        #     print(f"Error. Pre-application board is invalid")
        #     sys.exit(1)
        
        # step 5B - replace the "one" value in the correct cell
        self.known_values[row,col] = value

        # step 5C - postcheck the board
        #if SudokuBoard.check_board_array(self.known_values) == False:
        #    print(f"INFO: Post-application board is invalid when setting [({row},{col}) = {value}]")

    def apply_known_cell_to_possibilities(row,col,value,possibilities):
        assert(type(value) == type(1))
        assert(row<9)
        assert(col<9)
        assert(value>=1)
        assert(value<=9)

        super_row = row // 3
        super_col = col // 3

        # step one - clear out column
        possibilities[row,:,value-1] = 0
        # step two - clear out row
        possibilities[:,col,value-1] = 0
        # step three - clear out z stack
        possibilities[row,col,:] = 0 
        # step four - clear out neighborhood
        possibilities[super_row*3:(super_row+1)*3,super_col*3:(super_col+1)*3,value-1] = 0
        # step five - restore the "possibility" in the known location
        possibilities[row,col,value-1] = 1

    def convert_possibilities_to_known_values(possibilities):
        assert(possibilities.shape == (9,9,9))
        
        # these are the cells we know, because they have only one possibility 
        possibilities_per_cell = np.sum(possibilities,axis=2)
        known_cells = (possibilities_per_cell == np.ones([9,9],dtype=np.uint))
        
        # then we take it back to a 9x9x9 array (so the known values become stacks)
        known_cell_stacks = known_cells.reshape([9,9,1]) * np.ones([9,9,9],dtype=np.uint)

        # then mask out the possibilities that are not "known"
        confirmed_possibilites = known_cell_stacks * possibilities

        # quick check to confirm that there are zero or one possibilities per stack
        assert(np.max(np.sum(confirmed_possibilites,axis=2)) <= 1)

        # build a stack of incrementing values
        stack_values = np.arange(1,10,dtype=np.uint).reshape([1,1,9])
        
        # use that stack to convert positions to values
        confirmed_values = confirmed_possibilites*stack_values

        # reduce to a 2d array again
        known_values = np.sum(confirmed_values,axis=2)

        return known_values
    
    def convert_known_values_to_possibilities(known_values):
        # create the possibilities grid
        confirmed_possibilities = np.ones([9,9,9],dtype=bool)

        # apply each known value
        for row in range(9):
            for col in range(9):
                value = known_values[row][col]
                if value != 0:
                    SudokuBoard.apply_known_cell_to_possibilities(row,col,int(value),confirmed_possibilities)

        return confirmed_possibilities

    def find_implied_cells(known_values):
        confirmed_possibilities = SudokuBoard.convert_known_values_to_possibilities(known_values)    
        known_and_implied_values = SudokuBoard.convert_possibilities_to_known_values(confirmed_possibilities)
        return known_and_implied_values

    def apply_constraints_iteratively(self):
        starting = 0
        ending = 81
        iterations = 0
        while (starting < ending) and (self.valid()):
            starting = self.filled_cells()
            self.known_values = SudokuBoard.find_implied_cells(self.known_values)
            iterations += 1
            ending = self.filled_cells()
        return iterations
    
    def check_solution_string(self,solution_string):
        for row in range(9):
            for col in range(9):
                solution_value = int(solution_string[row*9+col])
                board_value = self.known_values[row][col]
                if board_value != 0:
                    if board_value != solution_value:
                        assert(0)
                        return False
        return True
                 
    def convert_possibilities_to_guesses(possibilities):
        # mask out all possibilities where the sum in a stack is 1
        # iterate over all possibilities
        # return the guess_iterationth possibilites
        guess_cells = (np.sum(possibilities,axis=2) > 1)

        # then we take it back to a 9x9x9 array (so the known values become stacks)
        guess_cell_stacks = guess_cells.reshape([9,9,1]) * np.ones([9,9,9],dtype=np.uint)

        # then mask the possibilities
        guess_possibilities = guess_cell_stacks*possibilities

        guesses = []
        it = np.nditer(guess_possibilities, flags=['multi_index'])
        for x in it:
            row,col,stack = it.multi_index
            if guess_possibilities[row][col][stack] == 1:
                guesses.append((row,col,stack+1))
        return guesses
    
    def guesses(self):
        possibilities = SudokuBoard.convert_known_values_to_possibilities(self.known_values)
        current_guesses = SudokuBoard.convert_possibilities_to_guesses(possibilities)
        return current_guesses
                    
class SudokuGuesser:
    def __init__(self):
        self.boards = {}
        self.board_graph = {}
    
    def add_board(self, new_board : SudokuBoard, origin_board : SudokuBoard, guess):
        # preconditions to adding guesses
        # 1/ the board is valid
        assert(new_board.valid())
        # 2/ the new board is not complete
        before = new_board.filled_cells()
        assert(before < 81)
        # 3/ the board is iterated to the final state
        new_board.apply_constraints_iteratively()
        after = new_board.filled_cells()
        assert(before == after)

        # store the board keyed by it's string
        self.boards[new_board.print_board_string()] = new_board
        self.board_graph[new_board.print_board_string()] = []

        # on the initial add, we allow no origin, since this is the root node
        if origin_board is None:
            assert(len(self.boards) == 1)
        else:
            # add the graph entry
            self.board_graph[origin_board.print_board_string()] = (new_board.print_board_string(), guess)

    def process_board(self,board_string) -> (SudokuBoard, list[SudokuBoard]):
        # get the board
        board: SudokuBoard = self.boards[board_string]
        # get all it's guesses
        guesses = board.guesses()
        good_guess_boards = []
        for guess in guesses:
            #clone the board
            clone = copy.deepcopy(board)
            #apply the guess
            clone.apply_known_value(guess[0],guess[1],guess[2])
            #advance the board
            clone.apply_constraints_iteratively()
            #check for invalidity or completeness
            if not clone.valid():
                # print(f"guess {guess} led to an invalid board")
                continue
            if clone.filled_cells() == 81:
                # print(f"guess {guess} got the answer with all 81 solved ")
                return (clone,good_guess_boards)
            good_guess_boards.append(clone)
        # print(f"There were {len(guesses)} and {len(good_guess_boards)} of them were good")
        return (None,good_guess_boards)
        
def run_many_games(count):
    game_file = open("boards/finnish.csv")
    hard_game_file = open("boards/hardgames.csv",mode="w")

    header = game_file.readline()
    hard_game_file.write(header)

    final_filled_array = np.zeros([count],dtype=int)
    iterations_array = np.zeros([count],dtype=int)
    
    start_time = time.time()

    for i in range(count):
        game = game_file.readline()
        try:
            board_string, solution = game.split(",")
        except ValueError:
            print("Ran out of games in input file")
            break
        sb = SudokuBoard()
        sb.initialize_board_from_string(board_string)
        starting = sb.filled_cells()
        iterations = sb.apply_constraints_iteratively()
        ending = sb.filled_cells()
        assert(sb.check_solution_string(solution))
        final_filled_array[i] = ending
        iterations_array[i] = iterations
        
        if ending != 81:
            guesser = SudokuGuesser()
            guesser.add_board(sb,None,None)
            (solution,good_guesses) = guesser.process_board(sb.print_board_string())
            if solution is not None:
                print(f"***** Board {i} solved with one guess_pass")
            else:
                print(f"***** Board {i} not solved with one guess_pass, but {len(good_guesses)} good guesses exist")
                print(f"\tBoard {i} started with {starting} cells, and ended with {ending} cells ")
                guesses_filled_cells = {}
                for val in [guess.filled_cells() for guess in good_guesses]:
                    if val in guesses_filled_cells:
                        guesses_filled_cells[val] += 1
                    else:
                        guesses_filled_cells[val] = 1
                print(f"\tGuesses had the following filled_cells histogram:{guesses_filled_cells}")
                
        if i % (count // 1000) == 0:
            print(f"iteration {i}")

    end_time = time.time()

    final_bincount = np.bincount(final_filled_array)   
    print(f"Final Results:")
    print(final_bincount)

    iter_bincount  = np.bincount(iterations_array)   
    print(f"Iterations:")
    print(iter_bincount)

    elapsed = end_time - start_time
    print(f"Processed {i} games in {elapsed:.2f} seconds. ({i/elapsed:.2f} games per second)")
    
    hard_game_file.close()

if __name__ == "__main__":        
    run_many_games(1000000)
