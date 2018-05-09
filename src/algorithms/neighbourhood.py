from src.domain import Route
from src.evaluators import DistanceEvaluator
import random
from collections import deque
from src.locations import Store, Job
import time


class HillClimbing:
    def __init__(self, jobs, stores, deliverers, distances_matrix, evaluator, codec, driver_ends_at_start=True,
                 route_initialization_method="random"):
        """"
        Initialzies a hill climbing object

        :param: driver_ends_at_start: boolean Driver returns the starting position to close loop
        :param: route_initialization_method: String options: 'random', 'relaxed_random', 'GRASP', 'greedy'
        """
        self.jobs = jobs
        self.stores = stores
        self.deliverers = deliverers
        self.distances_matrix = distances_matrix
        self.evaluator = evaluator
        self.solution = None
        self.codec = codec
        self.driver_ends_at_start = driver_ends_at_start
        self.route_initialization_method = route_initialization_method

    def generate_initial_solution(self, nr_iterations=2000, use_seed=False, seed=1):
        """"
        Generates a pool of initital solutions and picks the best random solution. Usually this is an infeasible solution.
        This works fine as the hill climbing algorithm optimizes this solution. It is not worth putting in the effort to try
        to find an initial solution that is as good as possible. That is what the algorithm is for.

        See also: https://link.springer.com/content/pdf/10.1007%2Fs10732-008-9083-1.pdf
        """

        best_route = None
        best_score = float('inf')

        for i in range(nr_iterations):
            route = Route(self.jobs, self.stores, self.deliverers, self.distances_matrix, self.evaluator)
            if use_seed:
                route.generate_initial_route(seed=seed, initialization_method=self.route_initialization_method )
            else:
                route.generate_initial_route(seed=i, initialization_method=self.route_initialization_method )

            route_score = route.evaluate()
            if route_score < best_score:
                best_score = route_score
                best_route = route
        # assert best_route == None
        self.solution = best_route
        return best_score, best_route

    def _solve_with_time_windows(self, tabu=False, tabu_size=5, nr_iterations=5, allow_infeasibilites=False):
        if tabu:
            tabu_list = deque(maxlen=tabu_size)
        seed = 1000
        init_route = self.solution.copy()
        rand = random.Random(seed)
        iteration_found_best_sol = None
        best_score = init_route.evaluate(end_with_start_loc=self.driver_ends_at_start)
        best_route = init_route


        for i in range(nr_iterations):

            pairs = init_route.generate_location_pairs(seed)
            rand.shuffle(pairs)
            seed += 1
            nr_iterations_no_changes = 0
            for pair in pairs:
                loc1 = pair[0]
                loc2 = pair[1]

                time_start_loc_1 = HillClimbing.get_time_start(loc1)
                time_start_loc_2 = HillClimbing.get_time_start(loc2)

                if time_start_loc_2 < time_start_loc_1:
                    temp_route = best_route.copy()
                    # temp_route.two_opt_move(pair[0], pair[1])
                    if random.random() >= 0.5:
                        temp_route.swap_destinations_time_window(pair[0], pair[1])
                    else:
                        temp_route.two_opt_move_time_window(pair[0], pair[1])
                    temp_score = temp_route.evaluate(end_with_start_loc=self.driver_ends_at_start)
                    if temp_score < best_score:

                        if tabu:
                            if temp_score not in tabu_list: #make solution tabu
                            # for item in pair: #make move tabu
                            #     if item not in tabu_list:
                                    best_route = temp_route
                                    best_score = temp_score
                                    tabu_list.append(temp_score)
                                    # tabu_list.extend(pair)
                                    iteration_found_best_sol = i

                        else:
                            best_route = temp_route
                            best_score = temp_score

            print('best score', best_score)
        # print(best_score, iteration_found_best_sol, best_route )

        return best_score, best_route, iteration_found_best_sol

    def solve(self, with_time_windows=False, tabu=False, tabu_size=5, nr_iterations=5, allow_infeasibilites=False):
        """"
        Runs the Hill Climbing algorithm. The local search in this algorithm uses both a 2-opt move and a regular swap to change
        positions of two locations in the route. A random value form a uniform distirbution is used to pick the move.
        Experimental analysis shows that this consistently produces better results than exclusively using one or the other.

        :param: with_time_windows: boolean to run the algorithm for the PDTSP with or without time windows
        :param: tabu: boolean run with or without tabu list
        :param: tabu_size: int the tabu list size
        :param: allow_infeasibilites: boolean allowing infeasibilities will help the algorith to escape local optima but there is chance it will return infeasible solutions

        """
        if with_time_windows:
            return self._solve_with_time_windows(tabu=tabu, nr_iterations=nr_iterations, allow_infeasibilites=allow_infeasibilites )
        else:
            if tabu:
                tabu_list = deque(maxlen=tabu_size)
            seed = 1000
            init_route = self.solution.copy()
            rand = random.Random(seed)
            iteration_found_best_sol = None
            best_score = init_route.evaluate(end_with_start_loc=self.driver_ends_at_start)
            best_route = init_route

            nr_iterations_no_changes = 0
            for i in range(nr_iterations):
                pairs = init_route.generate_location_pairs(seed)
                rand.shuffle(pairs)
                seed += 1

                for pair in pairs:
                    temp_route = best_route.copy()
                    # temp_route.two_opt_move(pair[1], pair[0])
                    if random.random() >= 0.5:
                        temp_route.two_opt_move(pair[1], pair[0])
                    else:
                        temp_route.swap_destinations(pair[0], pair[1])
                    temp_score = temp_route.evaluate(end_with_start_loc=self.driver_ends_at_start)
                    if not allow_infeasibilites and temp_score > 1000:
                        temp_route.fix_infeasibilities(self.codec, find_all_occurences=False)
                        temp_score = temp_route.evaluate(end_with_start_loc=self.driver_ends_at_start)
                    if temp_score < best_score:
                        if tabu:
                            # if temp_score not in tabu_list:
                            for item in pair:
                                if item not in tabu_list:
                                    best_route = temp_route
                                    best_score = temp_score
                                    # tabu_list.append(temp_score)
                                    tabu_list.extend(pair)
                                    iteration_found_best_sol = i
                                    nr_iterations_no_changes = 0
                                else:
                                    nr_iterations_no_changes +=1
                        else:
                            best_route = temp_route
                            best_score = temp_score

                print('best score', best_score)
            return best_score, best_route, iteration_found_best_sol

    @staticmethod
    def get_time_start(obj):
        if isinstance(obj, Store):
            job = obj.get_job()
            time_start = job.get_time_start()
        else:
            time_start = obj.get_time_start()

        return time_start


class GridSearch:
    def __init__(self, range_iterations_start, range_iterations_end, range_tabu_list_start, range_tabu_list_end,
                 tabu, hc, allow_infeasibilities, step_size=10, with_time_windows=False):
        """"
        Creates a GridSearch object. Ths object enables finds the best parameters to run the hill climbing algorithm with
        """
        self.range_iterations_start = range_iterations_start
        self.range_iterations_end = range_iterations_end
        self.step_size= step_size
        self.range_tabu_list_start = range_tabu_list_start
        self.range_tabu_list_end = range_tabu_list_end
        self.tabu = tabu
        self.allow_infeasibilites = allow_infeasibilities
        self.hc = hc
        self.with_time_windows = with_time_windows

    def run(self):
        """"
        Runs the algorithm with the initialized parameters
        """
        best_score = float('inf')
        best_route = None
        best_nr_iterations = None
        best_tabu_list_size = None
        for i in range(self.range_iterations_start, self.range_iterations_end, 10):
            for j in range(self.range_tabu_list_start, self.range_tabu_list_end):
                print('testing for nr_iterations', i, ' and tabu list size', j)
                self.hc.generate_initial_solution(use_seed=True)
                score, route, iteration = self.hc.solve(tabu=self.tabu, with_time_windows=self.with_time_windows,
                                                        nr_iterations=i, tabu_size=j,
                                                        allow_infeasibilites=self.allow_infeasibilites)

                if score < best_score:
                    best_score = score
                    best_route = route
                    best_nr_iterations = i
                    best_tabu_list_size = j

        print('best results with sore', best_score, best_nr_iterations, best_tabu_list_size )
        return best_score, best_route, best_tabu_list_size


