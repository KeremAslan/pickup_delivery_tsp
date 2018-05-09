from src.locations import Job, Store
import logging


class DistanceEvaluator:
    """"
    This evaluator measures the total tavel distance for the pick up and delivery traveling salesman problem

    It uses a penalty value of 1000 kms for infeasible routes
    """
    @staticmethod
    def evaluate_distance(route, driver_ends_at_start=True):
        deliverer = route.deliverer()
        dist_matrix = route.distances_matrix
        presedence_order_penalty = 1000
        total_distance = 0
        presedence_violations = 0
        if driver_ends_at_start:
            for i in range(len(route.tour)):
                if i == 0:
                    location = route.tour[i]
                    # if isinstance(location, Job):
                    #     index_of_corr_store = find_index_corresponding_store(location, route)
                    #     if index_of_corr_store > i:
                    #         score += 1000 # penalty of 1000 kms for visiting job before store
                    if isinstance(location, Job):
                        presedence_violations += 1
                        total_distance += dist_matrix.get_distance(deliverer, location)
                    else:
                        total_distance += dist_matrix.get_distance(deliverer, location)
                        # dist_matrix.get_distance(deliverer, route.route[i])

                elif i == len(route.tour)-1:
                    location = route.tour[i]
                    total_distance += dist_matrix.get_distance(deliverer, location)
                else:
                    last_location = route.tour[i-1]
                    location = route.tour[i]
                    if isinstance(location, Job):
                        index_of_corr_store = DistanceEvaluator.find_index_corresponding_store(location, route)
                        if index_of_corr_store > i:
                            presedence_violations += 1  # penalty of 1000 kms for visiting job before store
                    total_distance += dist_matrix.get_distance(last_location, location)

            score = total_distance + presedence_violations * presedence_order_penalty
        else:
            for i in range(len(route.tour)):
                if i == 0:
                    location = route.tour[i]
                    # if isinstance(location, Job):
                    #     index_of_corr_store = find_index_corresponding_store(location, route)
                    #     if index_of_corr_store > i:
                    #         score += 1000 # penalty of 1000 kms for visiting job before store
                    if isinstance(location, Job):
                        presedence_violations += 1
                        total_distance += dist_matrix.get_distance(deliverer, location)
                    else:
                        total_distance += dist_matrix.get_distance(deliverer, location)
                        # dist_matrix.get_distance(deliverer, route.route[i])

                else:
                    last_location = route.tour[i - 1]
                    location = route.tour[i]
                    if isinstance(location, Job):
                        index_of_corr_store = DistanceEvaluator.find_index_corresponding_store(location, route)
                        if index_of_corr_store > i:
                            presedence_violations += 1  # penalty of 1000 kms for visiting job before store
                    total_distance += dist_matrix.get_distance(last_location, location)

            score = total_distance + presedence_violations * presedence_order_penalty
        return score

    @staticmethod
    def find_index_corresponding_store(job, route):
        """"
        Returns the index of the store corresponding to the job in the given route
        """
        store_id_to_find = job.store['id']
        index_to_return = None
        for i in range(len(route.tour)):
            location = route.tour[i]
            if isinstance(location, Store):
                store_id = location.id
                if store_id_to_find == store_id:
                    logging.debug("Corresponding store for job " + str(job) + " is " + str(location))
                    index_to_return = i
        if index_to_return == None:
            logging.warning("Couldn't find store for job " + str(job))
        return index_to_return


class TimeEvaluator:
    """"
    A time evaluator. This evaluator measures the score as provided in the instructions for problem 2
    """
    @staticmethod
    def evaluate_distance(route, driver_ends_at_start=True):
        dist_matrix = route.distances_matrix
        time = route.deliverer().get_shift_start()
        speed = 4.1 #m/s
        time_spent_at_customer = 250 #seconds
        tour = route.tour
        presedence_violation = 1000
        score = 0
        for i in range(len(tour)):
            distance = None
            node = tour[i]
            if i == 0:
                if isinstance(node, Job):
                    distance = dist_matrix.get_distance(route.deliverer(), node)  # km
                    distance = distance * presedence_violation
                else:
                    distance = dist_matrix.get_distance(route.deliverer(), node)  # km

            elif i == len(route.tour)-1:
                distance = dist_matrix.get_distance(route.deliverer(), node)  # km
            else:
                last_location = route.tour[i - 1]
                if isinstance(node, Job):
                    index_of_corr_store = TimeEvaluator.find_index_corresponding_store(node, route)
                    if index_of_corr_store > i:
                        distance = dist_matrix.get_distance(route.deliverer(), node)  # km
                        distance = distance * presedence_violation
                    else:
                        distance = dist_matrix.get_distance(route.deliverer(), node)  # km
                else:
                    distance = dist_matrix.get_distance(last_location, node)

            travel_time = distance * 1000 / speed
            arrival_at_customer = time + travel_time
            if isinstance(node, Store):
                job = node.get_job()
                t_customer_start = job.get_time_start()
                time = arrival_at_customer
            elif isinstance(node, Job):
                t_customer_start = node.get_time_start()
                time = arrival_at_customer + time_spent_at_customer
            else:
                raise TypeError('Unknown type')

            node_score = (arrival_at_customer - t_customer_start) ** 2
            score += node_score

        return score

    @staticmethod
    def find_index_corresponding_store(job, route):

        # store_id_to_find = job.store['id']
        index_to_return = None
        for i in range(len(route.tour)):
            location = route.tour[i]
            if isinstance(location, Store):
                # store_id = location.id
                corr_job = location.get_job()
                corr_job_id = corr_job.id
                if corr_job.id == job.id:
                    logging.debug("Corresponding store for job " + str(job) + " is " + str(location))
                    index_to_return = i

        if index_to_return == None:
            logging.warning("Couldn't find store for job " + str(job))

        return index_to_return