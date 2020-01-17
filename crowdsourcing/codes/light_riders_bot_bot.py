# Use the game by - pip install git+https://github.com/wonderworks-software/PyFlow.git@master

# document links https://EvanMark/light_riders_bot
class Bot:
    def __init__(self): #initialise
        self.game = None
        self.last_move = None

    def setup(self, game):
        self.game = game

    """
    returns the next possible position  / direction 
    """

    def next_pos(self, direction, pos=None):
        if direction == "up":
            if pos is None:
                return self.game.my_player().row - 1, self.game.my_player().col
            else:
                row, col = pos
                return row - 1, col
        elif direction == "down":
            if pos is None:
                return self.game.my_player().row + 1, self.game.my_player().col
            else:
                row, col = pos
                return row + 1, col
        elif direction == "left":
            if pos is None:
                return self.game.my_player().row, self.game.my_player().col - 1
            else:
                row, col = pos
                return row, col - 1
        elif direction == "right":
            if pos is None:
                return self.game.my_player().row, self.game.my_player().col + 1
            else:
                row, col = pos
                return row, col + 1

    """
    applies the flood fill algorithm for the given position
    """

    def flood_use(self, position):
        visited = []
        return self.flood_fill(position, visited)

  
    # works on a two dimensional data matrix (each of size 8) generated from light rider bot module 
    def flood_fill(self, position, visited):
        row, col = position
       
        if row < 0 or col < 0 or row > self.game.field_width - 1 or \
                        col > self.game.field_height - 1 or position in visited \
                or not self.game.field.is_legal_tuple(position, self.game.my_botid):
            return 0  # count is 0

        visited.append(position)  
        return 1 + self.flood_fill((row - 1, col), visited) \
               + self.flood_fill((row + 1, col), visited) \
               + self.flood_fill((row, col - 1), visited) \
               + self.flood_fill((row, col + 1), visited)

    def do_turn(self):
        my_row = self.game.my_player().row
        my_col = self.game.my_player().col
        legal = self.game.field.legal_moves(self.game.my_botid, self.game.players)
        print(legal)

        # with open('log.txt', 'a') as file:
        #     file.write("Round: " + str(self.game.round) + " Begin!\n" + "length of legal_dirs: " + str(len(legal)) + "\n")
     
        if len(legal) == 0:
            desired_direction = "pass"
        else:
 
            legal_dirs = []  
            for _, direction in legal:
                legal_dirs.append(direction)
            if self.game.round == 0:
                dist_to_walls = {}
                dist_to_walls["up"] = my_row
                dist_to_walls["down"] = self.game.field_height - my_col
                dist_to_walls["left"] = my_col
                dist_to_walls["right"] = self.game.field_width - my_row

                # find min distance based on dist_to_walls 
                desired_direction = min(dist_to_walls, key=dist_to_walls.get)

            # if not on first round
            else:
                # TODO Maybe add dead end check? (only needed when next move is "pass")
                # TODO Maybe can add it before issue_order_pass

                # Remove unallowed moves (it seems that is_legal wasn't good enough)

                if self.last_move == "up":
                    try:
                #NOTE: this is *horrendous*, but seems to be the only way to check for legal moves
                        legal_dirs.remove("down")
                    except ValueError: 
                    
                        pass
                elif self.last_move == "down":
                    try:
                        legal_dirs.remove("up")
                    except ValueError:
                        pass
                elif self.last_move == "left":
                    try:
                        legal_dirs.remove("right")
                    except ValueError:
                        pass
                elif self.last_move == "right":
                    try:
                        legal_dirs.remove("left")
                    except ValueError:
                        pass


                my_id = self.game.my_botid
                if not self.game.field.is_legal_tuple((my_row - 1, my_col), my_id):
                    try:
                        legal_dirs.remove("up")
                    except ValueError:
                        pass
                if not self.game.field.is_legal_tuple((my_row + 1, my_col), my_id):
                    try:
                        legal_dirs.remove("down")
                    except ValueError:
                        pass
                if not self.game.field.is_legal_tuple((my_row, my_col - 1), my_id):
                    try:
                        legal_dirs.remove("left")
                    except ValueError:
                        pass
                if not self.game.field.is_legal_tuple((my_row, my_col + 1), my_id):
                    try:
                        legal_dirs.remove("right")
                    except ValueError:
                        pass

                if len(legal_dirs) == 1:
                    desired_direction = legal_dirs[0]


                elif len(legal_dirs) == 2:
                    first_move = legal_dirs[0]
                    second_move = legal_dirs[1]
                    first_move_next = self.next_pos(first_move)
                    second_move_next = self.next_pos(second_move)
                    next_moves_counts = {}
                    next_moves_counts[first_move] = self.flood_use(first_move_next)
                    next_moves_counts[second_move] = self.flood_use(second_move_next)

                    if next_moves_counts[first_move] == next_moves_counts[second_move]:
                        next_moves_dists = {}
                        next_moves_dists[first_move] = self.dist_to_obstacle(first_move)
                        next_moves_dists[second_move] = self.dist_to_obstacle(second_move)
                        desired_direction = max(next_moves_dists, key=next_moves_dists.get)
                    else:  # this probably never comes up - not sure
                        desired_direction = max(next_moves_counts, key=next_moves_counts.get)


                elif len(legal_dirs) == 3:
                    first_move = legal_dirs[0]
                    second_move = legal_dirs[1]
                    third_move = legal_dirs[2]
                    first_move_next = self.next_pos(first_move)
                    second_move_next = self.next_pos(second_move)
                    third_move_next = self.next_pos(third_move)
                    next_moves_counts = {}
                    next_moves_counts[first_move] = self.flood_use(first_move_next)
                    next_moves_counts[second_move] = self.flood_use(second_move_next)
                    next_moves_counts[third_move] = self.flood_use(third_move_next)
                    if next_moves_counts[first_move] != next_moves_counts[second_move] or \
                                    next_moves_counts[first_move] != next_moves_counts[third_move] or \
                                    next_moves_counts[second_move] != next_moves_counts[third_move]:
                        desired_direction = max(next_moves_counts, key=next_moves_counts.get)
                    else:
                        desired_direction = self.voronoi(legal_dirs)
                else: 
                    desired_direction = "pass"


        if desired_direction == "pass":
            self.last_move = "pass"
            self.game.issue_order_pass()
        else:
            self.last_move = desired_direction
            self.game.issue_order(desired_direction)