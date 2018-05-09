import json
import logging
from src.locations import Job, Store, Deliverer, DistancesMatrix
from src.algorithms.neighbourhood import  HillClimbing, GridSearch
from src.domain import Route, Codec
from src.evaluators import DistanceEvaluator, TimeEvaluator
import pandas as pd
import os


def load_data(datafile_location = '../data/problem.json'):
    """"
    Loads json data from the provided path and returns a dictionary containing that data

    :param datafile_location: str the path to read from
    :return data: dict the loaded data as a dictionary
    """
    if datafile_location[-4:] != "json":
        logging.warning("File being read is nog json")
    with open(datafile_location) as datafile:

        data = json.load(datafile)

    return data


def match_data(jobs, stores):
    grouped = {}
    for store in stores:
        for job in jobs:
            if store['id']== job['store']['id']:
                if store['id'] in grouped:
                    grouped[store['id']].append(job['id'])
                else:
                    grouped[store['id']] = [job['id']]
    return grouped

def split_and_retrieve_data(data):
    jobs = []
    stores = []
    deliverers = []
    # grouped = match_data(jobs, stores)

    for job in data['jobs']:
        a_job = Job(job['id'], job['fulfillment_id'], job['label'], job['location'], job['delivery_time_window'],
                    job['store'], job['status'], job['capacity'], job['expected_eta'], job['pickup_time'],
                    job['fulfillment_type'],job['hub_label'], job['address'], job['customer_id'], job['type'])
        jobs.append(a_job)

    for store in data['stores']:
        a_store = Store(store['label'], store['location'], store['id'], store['address'])
        stores.append(a_store)

    for deliverer in data['drivers']:
        a_deliverer = Deliverer(deliverer['id'], deliverer['label'], deliverer['start_shift'],
                                deliverer['end_shift'], deliverer['location'], deliverer['location_time_stamp'],
                                deliverer['capacity'], deliverer['pending_jobs'], deliverer['hub_label'],
                                deliverer['contract_type'], deliverer['is_fulltime_driver'], deliverer['vehicle_type'])
        deliverers.append(a_deliverer)

    print('number of jobs', len(jobs))
    print('number of stores', len(stores))
    print('number of deliverers', len(deliverers))

    return jobs, stores, deliverers


def read_run_statistics(file_path=None, file_name=None):
    if file_path is None:
        file_path = os.getcwd()
        file_path = file_path.replace("\src", "")
        file_path = file_path.replace("\\tsp.py", "")
        file_path += "\solutions\\"

    if file_name is None:
        file_name = file_path + "solution_statistics" + '.csv'
    else:
        file_name = file_path + str(file_name) + '.csv'

    if os.path.exists(file_name) :
        df = pd.read_csv(file_name, index_col=False)
    else:
        df = pd.DataFrame(columns=['scores_problem1', 'scores_problem2'])

    return df


def main():
    df_statistics = read_run_statistics()
    data = load_data()
    jobs, stores, deliverers = split_and_retrieve_data(data)

    all_locations = []
    all_locations.extend(jobs)
    all_locations.extend(stores)
    all_locations.extend(deliverers)

    distances_matrix = DistancesMatrix(all_locations)
    codec = Codec(jobs, stores, deliverers, distances_matrix, DistanceEvaluator )

    Route._generate_map(jobs, stores, deliverers)


    # hc = HillClimbing(jobs, stores, deliverers, distances_matrix, TimeEvaluator, codec,
    #                   route_initialization_method='relaxed_random')
    # hc.generate_initial_solution(use_seed=True)
    # h = hc.solve(with_time_windows=True, tabu=True, nr_iterations=10, tabu_size=7,
    #                                                     allow_infeasibilites=True)

    run_problem_1 = False
    run_problem_2 = True
    solutions_1 = []
    solutions_2 = []
    best_sol_problem_1 = None
    best_score_problem_1 = float('inf')
    best_sol_problem_2 = None
    best_score_problem_2 = float('inf')
    dump = True
    for i in range(10):

        if run_problem_1:
            print('running grid search for problem 1')
            #problem 1
            hc = HillClimbing(jobs, stores, deliverers, distances_matrix, DistanceEvaluator, codec,
                              route_initialization_method='random')

            gs = GridSearch(tabu=True, range_iterations_start=10, range_iterations_end=20, range_tabu_list_start=1,
                            range_tabu_list_end=10, hc=hc, allow_infeasibilities=True)

            score, route_problem1, tabu_list_size = gs.run()
            print('score', score)
            solutions_1.append(score)
            if score < best_score_problem_1:
                best_sol_problem_1 = route_problem1
                best_score_problem_1 = score
            # route_problem1.dump(append_to='_best_sol_problem_1_')

        #problem 2
        if run_problem_2:
            print('iteration', i)
            print('running grid search for problem 2')


            hc = HillClimbing(jobs, stores, deliverers, distances_matrix, TimeEvaluator, codec,
                              route_initialization_method='relaxed_random')

            # hc.generate_initial_solution(use_seed=True)
            # score, route_problem2, iteration = hc.solve(tabu=True, with_time_windows=True,
            #                                        nr_iterations=25, tabu_size=j,
            #                                        allow_infeasibilites=True)
            gs = GridSearch(tabu=True, range_iterations_start=20, range_iterations_end=30, range_tabu_list_start=2,
                            range_tabu_list_end=9, hc=hc, allow_infeasibilities=True, with_time_windows=True)


            score, route_problem2, tabu_list_size = gs.run()
            print('seconds', score)
            solutions_2.append(score)
            if score < best_score_problem_2:
                best_sol_problem_2 = route_problem2
                best_score_problem_2 = score

            # route_problem2.dump(append_to='_best_sol_problem_2_')

    if dump:
        if best_sol_problem_1 is not None:
            print('best_score 1', best_score_problem_1)
            best_sol_problem_1.dump(append_to='_best_sol_problem_1_')

        if best_sol_problem_2 is not None:
            print('best_score 2', best_score_problem_2)
            best_sol_problem_2.dump(append_to='_best_sol_problem_2', time_window=True)

        df = pd.DataFrame(columns=['scores_problem1', 'scores_problem2'])
        df['scores_problem1'] = solutions_1
        df['scores_problem2'] = solutions_2

        df_statistics = pd.concat([df_statistics, df])
        df_statistics.to_csv('../solutions/solution_statistics.csv', index=False)


if __name__ == "__main__":
    main()