import sys
import copy
import numpy as np
import hashlib

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
        self.possibilities = np.ones([9,9,9],"L")
        self.known_values = np.zeros([9,9],"L")
        self.forced_invalid = False
        self._creation_hash = ""

    def format_guess(guess):
        return f"[({guess[0]},{guess[1]})=={guess[2]}]"
    
    # def print_board_old_code(self):
    #     board_string = ""
    #     board_string += "-"*(3*3 + 4) + "\n"
    #     for super_row in range(3):
    #         for row in range(3):
    #             board_string += "|"
    #             for super_col in range(3):
    #                 for col in range(3):
    #                     board_string += f"{self.current_state[super_row*3+row][super_col*3+col]}"
    #                 board_string += "|"
    #             board_string += "\n"
    #         board_string += "-"*(3*3 + 4) + "\n"
    #     return board_string
    
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
    
    def mark_creation_hash(self):
        self._creation_hash = hashlib.sha256(self.known_values.tobytes(), usedforsecurity=False).hexdigest()[0:8]

    def creation_hash(self):
        return self._creation_hash

    def valid(self):

        # There are three methods a board can be invalid, we'll test them all returning False if we find them

        # Method 1 - if the outer loop has already exhausted all guesses on a board, we mark that board as invalid
        if self.forced_invalid == True: return False

        # Method 2 - The known values array can be contradictory. You can get here when the stack tests find the same
        # one and only one option for the same value in the same mask (i.e. two cells in row N must be value V)
        if (SudokuBoard.check_board_array(self.known_values) == False):
            print(f"The board({self.creation_hash()}) is INVALID due to the known_values being contradictory.")
            return False

        # Method 3 - The unknown cells might have zero options for an unknown cell (i.e. overdetermined system)
        non_zero_possibilities = np.logical_or(np.sum(self.possibilities,axis=2),self.known_values)
        validity_count = np.sum(non_zero_possibilities)
        if validity_count != 9*9:
            #print(f"The board({self.creation_hash()}) is INVALID with {9*9 - validity_count} cell(s) with zero possibilities.")
            return False
        
        # Board is valid by all known tests
        return True
        
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
        
        # step 5A - precheck the board
        # if SudokuBoard.check_board_array(self.known_values) == False:
        #     print(f"Error. Pre-application board is invalid")
        #     sys.exit(1)
        
        # step 5B - replace the "one" value in the correct cell
        self.known_values[row,col] = value

        # step 5C - postcheck the board
        if SudokuBoard.check_board_array(self.known_values) == False:
            print(f"INFO: Post-application board is invalid when setting [({row},{col}) = {value}]")

    def apply_exclusion_tests(self):
        confirmed_value_list = self.run_exclusion_tests()

        print(f"Adding the following confirmed values to the board.")
        print(f"Board:")
        print(self.print_board())
        for position_value in confirmed_value_list:
                print(position_value)
                print(f"Applying {position_value[3]} at [({position_value[0]},{position_value[1]})]")
                self.apply_known_value(position_value[0],position_value[1],position_value[3])
        
    def run_exclusion_tests(self):

        #this is where we store the confirmed possibilities of each test, using logical OR 
        # operations (more than one rule can confirm a possibility)
        confirmed_possibilities = np.zeros([9,9,9],dtype=bool)

        #for each of the 81*4 masks and sum the matrix
        for mask in self.masks:
            masked_possibities = self.possibilities * mask
        
            #if sum is 1, logically OR the confirmation matrix
            if np.sum(masked_possibities) == 1:
                np.logical_or(confirmed_possibilities,masked_possibities,confirmed_possibilities)
                
                # for each board cell, count how many values are "confirmed" for that cell. More than 
                # one is clearly in invalid board.
                confirmed_value_count = np.sum(confirmed_possibilities,axis=2,dtype='uint64')
                if (np.max(confirmed_value_count) > 1):
                    print(f"Suspected Invalid Board.")
                    np.array2string()

        # squash back to a 2D grid with confirmed values
        stack_of_values = np.asarray([1,2,3,4,5,6,7,8,9],"L").reshape([1,1,9])
        confirmed_possibilities_values = confirmed_possibilities.astype(int) * stack_of_values
        confirmed_value_array = np.sum(confirmed_possibilities_values,2).astype(int)

        # another tye of board invalidity can show up here. your possibilites matrix was valid, 
        # and you ran the exclusion tests and TWO cells in the same mask wanted to be the same value
        # an example would be if a row test showed that both (4,4) and (4,7) wanted to be a 3, so the row mask 
        # didn't trigger, but then the stack test for (4,4) and (4,7) showed that those cells could only be a 3
        # so both of those stack tests fired. I think only stack tests can generate this error, because row, col, 
        # and neighborhood tests are directly testing game validity criteria.
        #
        # I think this can be seen by looking for contradictions in the "confirmed values" only, without 
        # comparing to the known values. This seems counterintuitive but that information is already encoded 
        # in the "possibilities matrix"
        # 
        # to check the contradictions, we are going to put the answer in list form rather than array form, 
        # this will make the calling functions simpler
        
        confirmed_value_list = []
        contradiction = False
        iter = np.nditer(confirmed_value_array,["multi_index"],["readonly"])

        for value in iter:
            cell_value = value.tolist()
            assert(type(cell_value) == type(1))
            assert(cell_value <= 9)
            
            
            if cell_value != 0:
                row = iter.multi_index[0]
                col = iter.multi_index[1]
                neighborhood = (row // 3)*3 + (col // 3)
                if(cell_value <=9):
                    print(confirmed_value_array)
                    assert(cell_value)

                assert(cell_value >=1)
                assert(row<9)
                assert(col<9)
                assert(neighborhood<9)
                print(f"Adding [r:{row},col:{col},neighborhood:{neighborhood}]={cell_value} to the confirmed_value_list")
                confirmed_value_list.append((row,col,neighborhood,cell_value))

        return confirmed_value_list


        # row_check = {}
        # for row in range(9): row_check[row] = []
        # col_check = {}
        # for col in range(9): col_check[col] = []
        # neighborhood_check = {}
        # for neighborhood in range(9): neighborhood_check[neighborhood] = []

        # for value in iter:
        #     if value != 0:
        #         row = iter.multi_index[0]
        #         col = iter.multi_index[1]
        #         neighborhood = (row // 3)*3 + (col // 3)

        #         if value in row_check[row]:
        #             contradiction = True
        #             break
        #         else:
        #             row_check[row].append(value)
                
        #         if value in col_check[col]:
        #             contradiction = True
        #             break
        #         else:
        #             col_check[col].append(value)

        #         if value in neighborhood_check[neighborhood]:
        #             contradiction = True
        #             break
        #         else:
        #             neighborhood_check[neighborhood].append(value)

        #         confirmed_value_list.append((row,col,neighborhood,value))

        # if contradiction:
        #     print(f"Contradiction. Board Invalid due to [r:{row},col:{col},neighborhood:{neighborhood}]={value}")
        #     print(f"Current Confirmed List is:")
        #     for confirmed_value in confirmed_value_list:
        #         print(f"[({confirmed_value[0]},{confirmed_value[1]})](n:{confirmed_value[2]}) = {confirmed_value[3]}")
        #     return (False,[])
        # else:
        #     return (True, confirmed_value_list)

    def tuple_elimination_tests(self):
        # apply the idea that if two cells in a set have only A and B as possibilities, then no
        # other cell in the set can have A and B as possibilities. Example: if cell 1:(A,B), cell 2(A,B),
        # and cell 3(A,B,C) then cell 3 must be actualy by C since cell 1 and cell 2 "need" the A and B
        
        #don't know how to code this yet ;)
        pass

    def force_invalid(self):
        self.forced_invalid = True
    
    def check_board_array(board_array):
        #scan rows columns and neighborhoods looking for duplicates
        for row in range(9):
            existing_values = {}
            for col in range(9):
                value = board_array[row,col]
                if value == 0: continue
                if value in existing_values:
                    # print(f"Board found invalid scanning row {row}.")
                    # print(f"({row},{col})={value} which already exists.")
                    # print(np.array2string(board_array))
                    return False
                else:
                    existing_values[value] = True
        
        for col in range(9):
            existing_values = {}
            for row in range(9):
                value = board_array[row,col]
                if value == 0: continue
                if value in existing_values:
                    # print(f"Board found invalid scanning col {col}.")
                    # print(f"({row},{col})={value} which already exists.")
                    # print(self.print_board())
                    return False
                else:
                    existing_values[value] = True
        
        for super_row in range(3):
            for super_col in range(3):
                existing_values = {}
                for row in range(3):
                    for col in range(3):
                        check_row = super_row*3 + row
                        check_col = super_col*3 + col
                        value = board_array[check_row,check_col]  
                        if value == 0: continue
                        if value in existing_values:
                            # print(f"Board found invalid scanning neighborhood ({super_row},{super_col}).")
                            # print(f"({check_row},{check_col})={value} which already exists.")
                            # print(self.print_board())
                            return False
                        else:
                            existing_values[value] = True
        return True
    
    def check_board(self):
        return SudokuBoard.check_board_array(self.known_values)

    def check_board2(self):

        check_masks = []

        zero = np.zeros([9,9],"L")
    
        # 9 row possibilities
        for row in range(9):
            mask = zero.copy()
            mask[row,:] = 1
            assert(mask.sum() == 9)
            check_masks.append(mask)
        # 9 column possibilities
        for col in range(9):
            mask = zero.copy()
            mask[:,col] = 1
            assert(mask.sum() == 9)
            check_masks.append(mask)
        # 9 neighborhood possibilities
        for super_row in range(3):
            for super_col in range(3):
                mask = zero.copy()
                mask[super_row*3:(super_row+1)*3,super_col*3:(super_col+1)*3] = 1
                assert(mask.sum() == 9)
                check_masks.append(mask)
    

        for mask in check_masks:
            mask_sum = np.sum(self.known_values * mask)
            if mask_sum != sum(range(1,10)):
                print("Invalid Board")
                print("Mask is")
                print(np.array2string(mask,max_line_width=120))
                print("Board is")
                print(np.array2string(self.known_values,max_line_width=120))
                return False
        return True

class GameGraph:
    def __init__(self):
        self.boards = {}
    
    def add_board(self, board):
        self.boards[board.creation_hash()] = {"board":board,"forward_refs":[], "backward_refs":[]}

    # reference from A to B
    def add_edge(self, board_a, board_b, edge_label):
        self.boards[board_a.creation_hash()]["forward_refs" ].append((board_b.creation_hash(),edge_label))
        self.boards[board_b.creation_hash()]["backward_refs"].append((board_a.creation_hash(),edge_label))
    
    def get_board(self, board_hash):
        return self.boards[board_hash]["board"]
    
    def __contains__(self,guess_board_hash):
        return guess_board_hash in self.boards
    
    def get_matching_board(self,board_hash):
        return self.boards[board_hash]["board"]
    
    def best_back_reference(self,board_hash):
        # define a quick function that can take a hash and return the unfilled cells of that board
        unfilled_cells_from_board_hash = lambda y: self.boards[y[0]]["board"].unfilled_cells()

        # use the min function, keyed with the above function to find the best board
        # print(f"best_back_reference: board({board_hash}) has {len(self.boards[board_hash]['backward_refs'])} ",
        #       f"back references.")
        best_back_ref_hash,edge_label = min(self.boards[board_hash]["backward_refs"],key=unfilled_cells_from_board_hash)

        # return the reference to that board
        return (best_back_ref_hash,edge_label)
    

class SudokuGame:
    def __init__(self):
        self.game_graph = GameGraph()
    
    def run_game(self,board_file):
        iteration_count = 0

        # populate the node
        current_board = SudokuBoard()
        current_board.import_file(board_file)
        current_board.mark_creation_hash()

        # populate the game graph
        self.game_graph.add_board(current_board)

        while(True):
            iteration_count += 1
            # run exclusion on the current board
            no_contradiction = current_board.apply_exclusion_tests()

            print(f"*** At iteration {iteration_count} the board({current_board.creation_hash()}) has",
                  f"{current_board.unfilled_cells()} unfilled cells.")
            
            # this is very gross, but we may need edges for guessing and for excluding, 
            # because they get different board states.
            # TODO: do we need this? since we added the creation_hash fixity?
            if current_board.creation_hash() not in self.game_graph:
                print(f"Adding current_board({current_board.creation_hash()}) after exclusions")
                self.game_graph.add_board(current_board)

            # if board is complete:
            if current_board.unfilled_cells() == 0:
                print(f"Board is solved.")
                if current_board.check_board():
                    print("Board is valid.")
                else:
                    print("Board is invalid.")
                break

            # now we need to see if we excluded ourselves into invalidity
            if current_board.valid() == False:
                # time to backtrack
                (best_back_ref_hash,edge_label) = self.game_graph.best_back_reference(current_board.creation_hash())
                print(f"backtracking to board({best_back_ref_hash}, reversing the guess {SudokuBoard.format_guess(edge_label)})")
                current_board = self.game_graph.get_matching_board(best_back_ref_hash)
            else:
                for i in range(9*9):
                    # ask for the ith guess (i.e. assume the ith possibility is true)
                    guess_board, guess_info = current_board.guess(i)
                    
                    if guess_board == None:
                        # there are no guesses left, that means we need to mark this board invalid and backtrack
                        current_board.force_invalid()
                        print(f"Run out of guesses after {i} attempts. ",
                              f"Marking board({current_board.creation_hash()}) invalid.")
                        # Lazy backtrack: exit this loop, and let the above validity check kick it off
                        break

                    # the guess exists, to mark the creation hash
                    guess_board.mark_creation_hash()
                        
                    # if guess board is in the graph already
                    if guess_board in self.game_graph:
                        # if guess board is valid
                        if self.game_graph.get_matching_board(guess_board).valid():
                            print(f"Critical Error. Guess board({guess_board.creation_hash()}) from guess ",
                                  f"{guess_info} exists and is valid. Exiting.")
                            sys.exit(0)
                        else:
                            # expected case after backtracking, we've tried this before, it didn't work
                            print(f"Rejecting guess {guess_info} yielding board({guess_board.creation_hash()}) ",
                                  f"since known to be invalid.")
                            continue
                    else:
                        # this is a novel board
                        #print(f"Loading guess_board({guess_board.creation_hash()})")
                        self.game_graph.add_board(guess_board)
                        print(f"Adding a guess[{SudokuBoard.format_guess(guess_info)}] between current_board({current_board.creation_hash()})",
                              f"and guess_board({guess_board.creation_hash()})")
                        self.game_graph.add_edge(current_board,guess_board,guess_info)
                        current_board = guess_board
                        # so we break out of the for loop and start again
                        # print(f"Guess {i} was {guess_info} yielding novel board({guess_board.creation_hash()}). ",
                        #       f"Making this board the current board.")
                        break        
                 
    

    # How are we going to handle the guesses?
    # 1/ keep several boards in a graph, nodes are boards states, edges are guesses
    # 2/ When the apply exclusion tests loop terminates, then make a guess
    # 3/ guesses are good until marked bad
    # 4/ a bad guess is one where the possibilities matrix has zeros in the stacks where no value is known
    # 5/ when you get a bad guess, go backwards down the graph and make a choice that's not to a bad board


if __name__ == "__main__":        
        
    board_file = open(sys.argv[1])

    the_game = SudokuGame()
    the_game.run_game(board_file)
    sys.exit(0)

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
    
    