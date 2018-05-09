import random
import logging
from src.locations import Job, Store
from collections import Counter
import os
import json


class Route:
    """"
    The route class represents a route that is to be traversed by the deliverer
    """
    id_to_obj_map = {}

    def __init__(self, jobs, stores, deliverers, distances, evaluator):
        """

        :param jobs: list - all locations of customers needs to visit
        :papram: stores: list - all locations of stores that need to be viit in this route
        :param distances: locations.DistanceMatrix
        :param deliverer: list list of deliverers - in this case length of this list should be 1
        """
        self.locations = {
            'jobs': jobs,
            'stores': stores,
            'deliverers': deliverers
        }
        self.requests = self._generate_requests()
        self.distances_matrix = distances
        self.tour = [] #self._generate_random_route(self.locations)
        self.evaluator = evaluator

    def _generate_requests(self):
        """"
        A request is a pick up and delivery match. This is generated for convenience in problem 2.
        """
        requests = []
        for job in self.jobs():
            pick_up_location = job.store['id']
            for store in self.stores():
                if pick_up_location == store.id:
                    requests.append(Request(store, job))
                    break
        return requests

    @staticmethod
    def _generate_map(jobs, stores, deliverers):
        """"
        Generates a dict of ids and the corresponding object
        """
        for job in jobs:
            Route.id_to_obj_map[job.id] = job

        for store in stores:
            Route.id_to_obj_map[store.id] = store

        for driver in deliverers:
            Route.id_to_obj_map[driver.id] = driver

    def _generate_random_route(self, seed):
        rand = random.Random(seed)
        tour = []
        for k, v in self.locations.items():
            if k != 'deliverers':
                tour.extend(v)

        rand.shuffle(tour)
        return tour

    def _generate_relaxed_random_route(self, seed):
        rand = random.Random(seed)
        tour = []
        stores = []
        for request in self.requests:
            store = request.pick_up.copy()
            job = request.drop_off
            store.set_job(job)
            stores.append(store)
            tour.extend([store, job])

        self.locations['stores'] = stores
        rand.shuffle(tour)
        return tour

    def generate_initial_route(self, initialization_method='random', seed=1):
        """"
        Initializes the first route by the given initializatoin method.

        Options:
        - greedy: a greedy route construction
        - grasp: Greedy Randomized Adaptive Search
        - random: a completely random route generation. Use this for problem 1
        - relaxed_random: a completely random route generation. This problem relaxes the tsp condition that each destination is to be visited exactly once for store.
        Use this for problem 2

        """
        if initialization_method == 'greedy':
            self.tour = self._grasp()
        elif initialization_method == 'GRASP':
            self.tour = self._greedy()
        elif initialization_method == 'random':
            self.tour = self._generate_random_route(seed)
        elif initialization_method == 'relaxed_random':
            self.tour = self._generate_relaxed_random_route(seed)

    def _grasp(self):
        raise NotImplementedError('Not yet implemented')

    def _greedy(self):
        raise NotImplementedError('Not yet implemented')

    def two_opt_move(self, loc1, loc2):
        """"
        Modifes the tour by a 2-opt move.
        """
        index1 = self.tour.index(loc1)
        index2 = self.tour.index(loc2)
        i = min(index1, index2)
        k = max(index1, index2)

        tour = self.tour
        assert i >= 0 and i < (len(tour) - 1)
        assert k > i and k < len(tour)
        new_tour = tour[0:i]
        new_tour.extend(reversed(tour[i:k + 1]))
        new_tour.extend(tour[k + 1:])
        assert len(new_tour) == len(tour)
        self.tour = new_tour

    @staticmethod
    def two_opt_by_index(list_, index1, index2):
        i = min(index1, index2)
        k = max(index1, index2)
        assert i >= 0 and i < (len(list_) - 1)
        assert k > i and k < len(list_)
        new_tour = list_[0:i]
        new_tour.extend(reversed(list_[i:k + 1]))
        new_tour.extend(list_[k + 1:])
        assert len(new_tour) == len(list_)

        return new_tour

    def get_total_distance(self):
        """"
        Calculates the total length of the route. Data is taken from self.DistancesMatrix.
        The total distance is calculated from the location of the deliverer as a starting point
        @deprecated.....
        """
        distance = 0
        for i in range(len(self.tour)):
            if i == 0:
                distance += self.distances_matrix.get_distance(self.deliverer, self.tour[i])
            else:
                # calculate distance from last city to current city
                from_ = self.tour[i - 1]
                to_ = self.tour[i]
                distance += self.distances_matrix.get_distance(from_, to_)
        # self.distance = distance
        return distance

    def swap_destinations(self, loc1, loc2):
        """"
        Swaps the position of two to-be-visited locations

        :param: pos1: a locations.Job or locations.Store that is in the route
        :param: pos2: a locations.Job or locations.Store that is in the route
        """
        index1 = self.find_index_of_job(loc1)
        index2 = self.find_index_of_job(loc2)

        self.tour[index1], self.tour[index2] = self.tour[index2], self.tour[index1]

    def swap_destinations_time_window(self, loc1, loc2):
        """"
        Swaps the position of two to-be-visited locations

        :param: pos1: a locations.Job or locations.Store that is in the route
        :param: pos2: a locations.Job or locations.Store that is in the route
        """
        # index1 = 0
        # index2 = 0

        if isinstance(loc1, Job) and isinstance(loc2, Job):
            index1 = self.find_index_of_job(loc1)
            index2 = self.find_index_of_job(loc2)
        elif isinstance(loc1, Store) and isinstance(loc2, Store):
            index1 = self.find_index_of_store(loc1)
            index2 = self.find_index_of_store(loc2)
        elif isinstance(loc1, Store) and isinstance(loc2, Job) :
            index1 = self.find_index_of_store(loc1)
            index2 = self.find_index_of_job(loc2)
        elif isinstance(loc1, Job) and isinstance(loc2, Store):
            index1 = self.find_index_of_job(loc1)
            index2 = self.find_index_of_store(loc2)
        else:
            string = 'Swapping not defined objects '
            string += loc1 + " " + loc2
            raise TypeError(string)

        self.tour[index1], self.tour[index2] = self.tour[index2], self.tour[index1]

    def two_opt_move_time_window(self, loc1, loc2):
        """"
        Does the 2-opt move for a tour with time windows. Reason for needing a seperate functoin is because a tour with time windows
        includes duplicate stores.
        """
        if isinstance(loc1, Job) and isinstance(loc2, Job):
            index1 = self.find_index_of_job(loc1)
            index2 = self.find_index_of_job(loc2)
        elif isinstance(loc1, Store) and isinstance(loc2, Store):
            index1 = self.find_index_of_store(loc1)
            index2 = self.find_index_of_store(loc2)
        elif isinstance(loc1, Store) and isinstance(loc2, Job):
            index1 = self.find_index_of_store(loc1)
            index2 = self.find_index_of_job(loc2)
        elif isinstance(loc1, Job) and isinstance(loc2, Store):
            index1 = self.find_index_of_job(loc1)
            index2 = self.find_index_of_store(loc2)
        else:
            string = 'Swapping not defined objects '
            string += loc1 + " " + loc2
            raise TypeError(string)

        self.tour = Route.two_opt_by_index(self.tour, index1, index2)

    def find_index_of_store(self, obj):
        index = 0
        job = obj.get_job()
        for i in range(len(self.tour)):
            node = self.tour[i]
            if isinstance(node, Store):
                if node.id == obj.id:
                    if job.id == node.get_job().id:
                        index = i
        return index

    def find_index_of_job(self, obj):
        index = 0
        for i in range(len(self.tour)):
            item = self.tour[i]
            if item.id == obj.id:
                index = i

        return index

    def generate_location_pairs(self, seed=123):
        pairs = []
        rand = random.Random(seed)
        all_locations = self.get_all_locations()
        rand.shuffle(all_locations)
        for i in range(len(all_locations)):
            for j in range(i+1, len(all_locations)):
                if all_locations[i] is all_locations[j]:
                    logging.warning('adding', all_locations[i], all_locations[j] )
                pairs.append( (all_locations[i], all_locations[j]) )

        return pairs

    def get_all_locations(self, incl_deleverer=False):
        all_locations = []
        for k, locations in self.locations.items():
            if incl_deleverer:
                all_locations.extend(locations)
            else:
                if k != "deliverers":
                    all_locations.extend(locations)

        return all_locations

    def fix_infeasibilities(self, codec, find_all_occurences=False):
        encoded = codec.encode_route(self)
        decoded_route = codec.decode_route(encoded, find_all_occurences=find_all_occurences )
        self.tour = decoded_route.tour

    def copy(self):
        route = Route(self.jobs(), self.stores(), [self.deliverer()], self.distances_matrix,
                      self.evaluator)
        route.tour = []
        route.tour.extend(self.tour)
        return route

    def evaluate(self, end_with_start_loc=True):
        """"
        Score the tour by self.evaluator
        """
        return self.evaluator.evaluate_distance(self, end_with_start_loc)

    def __str__(self):
        stringbuilder = list()
        stringbuilder.extend(self.__dict__['tour'])
        return "Route[" + ", ".join(str(x) for x in stringbuilder) + "]"

    def __repr__(self):
        return self.__str__()

    def pretty_print(self):
        stringbuilder = []
        for dest in self.tour:
            stringbuilder.append(dest.id)
        return "Route[" + ", ".join(str(x) for x in stringbuilder) + "]"

    def jobs(self):
        return self.locations['jobs']

    def stores(self):
        return self.locations['stores']

    def deliverer(self):
        return self.locations['deliverers'][0]

    @staticmethod
    def get_node_by_id(id):
        if len(Route.id_to_obj_map) == 0:
            raise NotImplementedError('Please run Route._generate_map() first')
        else:
            return Route.id_to_obj_map[id]

    def id(self):
        id = 0
        for node in self.tour:
            id += int(node.id)

        return id

    def dump(self, file_path = None, file_name=None, append_to=None, time_window=False):
            if file_path is None:
                file_path = os.getcwd()
                file_path =  file_path.replace("\src", "")
                file_path += "\solutions\\"

            if file_name is None:
                if append_to is not None:
                    file_name = file_path + str(self.id()) + "_" + str(append_to) + '.json'
                else:
                    file_name = file_path + str(self.id()) + '.json'

            if not os.path.exists(file_path):
                os.mkdir(file_path)


            val = list()
            val.append({
                "label": "init_loc",
                "lat": self.deliverer().get_latitude(),
                "lon": self.deliverer().get_longitude(),
                "fulfillment_id": "null"
            })

            for node in self.tour:
                if isinstance(node, Job):
                    dic = {
                        "label": node.label,
                        "lat": node.get_latitude(),
                        "lon": node.get_longitude(),
                        "fulfillment_id": node.fulfillment_id
                    }
                    val.append(dic)
                elif isinstance(node, Store):
                    if not time_window:
                        fullfilment_ids = self.match_data(node)
                        for f_id in fullfilment_ids[node.id]:
                            dic = {
                                "label": node.label,
                                "lat": node.get_latitude(),
                                "lon": node.get_longitude(),
                                "fulfillment_id": f_id
                            }
                            val.append(dic)
                    else:
                        job = node.get_job()
                        dic = {
                            "label": node.label,
                            "lat": node.get_latitude(),
                            "lon": node.get_longitude(),
                            "fulfillment_id": job.fulfillment_id
                        }
                        val.append(dic)
                else:
                    raise TypeError("Node is of unfamiliar type")

            val.append({
                "label": "end_loc",
                "lat": self.deliverer().get_latitude(),
                "lon": self.deliverer().get_longitude(),
                "fulfillment_id": "null"
            })

            f = {"route": val}
            with open(file_name, 'w') as outfile:
                json.dump(f,outfile, indent=4)

    def match_data(self, node):
        matched = {}
        for store in self.stores():
            if store.id == node.id:
                for job in self.jobs():
                    if node.id == job.store['id']:
                        if store.id in matched:
                            matched[store.id].append(job.id)
                        else:
                            matched[store.id] = [job.id]
        return matched


class Request:
    def __init__(self, pick_up, drop_off):
        self.pick_up = pick_up
        self.drop_off = drop_off

    def get_pair(self):
        return [self.pick_up, self.drop_off]



class Codec:
    def __init__(self, jobs, stores, deliverer, dist_matrix, evaluator):
        self.jobs = jobs
        self.stores = stores
        self.deliverer = deliverer
        self.distances_matrix = dist_matrix
        self.evaluator = evaluator
        self._encoded, self._decoded = self._run()


    def _run(self):
        matched = {}
        decoded = {}
        encoded = {}
        for store in self.stores:
            for job in self.jobs:
                if store.id == job.store['id']:
                    if store in matched:
                        matched[store].append(job)
                    else:
                        matched[store] = [job]
        i = 1
        for k, v in matched.items():
            items = {}
            items['store'] = k
            items['jobs'] = v
            decoded[i] = items
            encoded[k] = i
            for job in v:
                encoded[job] = i
            i += 1

        return encoded, decoded

    def _encode_node(self, obj):
        return self._encoded[obj]

    def _decode_node(self, code, encounter, store=True):
        if store:
            return self._decoded[code]['store'] #return store
        else:
            return self._decoded[code]['jobs'][encounter] #return list with jobs

    def encode_route(self, route):
        encoded_tour = []
        for location in route.tour:
            encoded_tour.append(self._encode_node(location))

        return encoded_tour

    def decode_route(self, encoded_tour, find_all_occurences=False):
        decoded_tour = []
        encounters = {}
        counter = Counter(encoded_tour)
        decoded_tours = []

        for code in encoded_tour:
            if code in encounters:
                encountered = encounters[code]
                decoded_tour.append(self._decode_node(code, encountered, store=False))
                encounters[code] = encountered + 1
            else:
                encountered = 0
                encounters[code] = encountered
                decoded_tour.append(self._decode_node(code, encountered, store=True))

        if find_all_occurences:
            decoded_tours.append(decoded_tour)
            for node, occurence in counter.items():
                if occurence > 2:
                    indices = [i for i, x in enumerate(encoded_tour) if x == node]
                    to_swap = indices[1:]

                    pairs = Codec.make_pairs(to_swap)
                    for _ in range(len(pairs)):
                        copy = list(decoded_tour)
                        # copy.extend(decoded_tour)
                        decoded_tours.append(copy)

            best_route = None
            best_score = float('inf')
            for tour in decoded_tours:
                route = Route(self.jobs, self.stores,
                              self.deliverer, self.distances_matrix, self.evaluator)
                route.tour = tour
                score = route.evaluate()
                if score < best_score:
                    best_score = score
                    best_route = route

            return best_route
        else:
            route = Route(self.jobs, self.stores,
                          self.deliverer, self.distances_matrix, self.evaluator)
            route.tour = decoded_tour
            return route

    @staticmethod
    def make_pairs(items):
        pairs = []
        for i in range(len(items)):
            for j in range(i+1, len(items)):
                if items[i] != items[j]:
                    pairs.append((items[i], items[j]))

        return pairs