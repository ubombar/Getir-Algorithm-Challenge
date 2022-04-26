import sys
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

def preprocess_matrix(matrix, jobs):
    '''
    The distance matrix should only contain the indexes given in jobs. If not,
    the solver also calculates routes for locations that does not have a job.
    As an easy fix, I will set the distances from and to these redundant locations
    to 0.

    I am also specifying the ending location. I also create a virtual location and make
    the cost of going there zero. This can be done by padding the matrix.
    '''
    # Convert the matrix into numpy array
    matrix = np.array(matrix, dtype=int)
    
    # Padd the matrix only bottom and right
    matrix = np.pad(matrix, 1, constant_values=0)[1:, 1:]

    # Find the redundant indexes and make their cost zero
    all_locs = {i for i in range(len(matrix))}
    jobs_locs = {job['location_index'] for job in jobs}
    redundant_locs = all_locs.difference(jobs_locs)

    for loc_index in redundant_locs:
        matrix[loc_index, :] = 0
        matrix[:, loc_index] = 0

    # We are done now we can use our matrix
    return matrix


def solve_vrp(vehicles, jobs, matrix):    
    # Preprocess the matrix and get the desired version
    matrix = preprocess_matrix(matrix=matrix, jobs=jobs)

    # Get the number of vehicles and number of locations including the virtual one
    num_vehicles = len(vehicles)
    num_locations = len(matrix)

    # Set starting locations of the vehicles
    starting_location = [v['start_index'] for v in vehicles]

    # Set the ending locations to the virtual location we created that has no cost
    ending_location = [num_locations - 1 for _ in vehicles]

    # This is for getting the id of the job from its order location
    location_index_to_job_id = {job['location_index']:job['id'] for job in jobs}

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(
        num_locations, 
        num_vehicles, 
        starting_location, 
        ending_location)

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    
    # Create and register a transit callback. This is for calculatiing
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Distance constraint.
    # Maximum time for any vehicle is set to the sum of the matrix. By this way there won't be a
    # limitation on time.
    routing.AddDimension(
        transit_callback_index,
        0,
        int(matrix.sum()), 
        True,
        'Time')
    distance_dimension = routing.GetDimensionOrDie('Time')
    distance_dimension.SetGlobalSpanCostCoefficient(100)

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    return process_solution(manager, routing, solution, vehicles, location_index_to_job_id)


def  process_solution(manager, routing, solution, vehicles, location_index_to_job_id):
    total_delivery_duration = 0
    routes = {}

    # Iterate on the vehicle list
    for vehicle_object_index, vehicle_object in enumerate(vehicles):
        # Get the vehicle id
        vehicle_id = vehicle_object['id']
        index = routing.Start(vehicle_object_index)

        # Create a list for jobs and integer for the duration
        jobs = []
        delivery_duration = 0

        # Start iteration on the routes. Whith while loop we dont come to the last index.
        # Which is the virtual location's index.
        while not routing.IsEnd(index):
            # Get the location of the node
            location_index = manager.IndexToNode(index)

            # If the index is contained in 'location_index_to_job_id' which means current
            # location is not redundant and has a cost. In this case find it's job_id.
            if location_index in location_index_to_job_id:
                jobs.append(location_index_to_job_id[location_index])

            # Now calculate the next index. This is for calculating the cost between current and the next.
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            delivery_duration += routing.GetArcCostForVehicle(previous_index, index, vehicle_object_index)

        # Then set the vehicle_id's to a new dictionaty. This will be in the format as in the question. 
        routes[vehicle_id] = dict(
            jobs=jobs,
            delivery_duration=delivery_duration)

    # This is for calculating the total delivery time. Simple for loop.
    for vehicle_id in routes:
        total_delivery_duration += routes[vehicle_id]['delivery_duration']

    # Now return it as a dict in the requested format.
    return dict(
        total_delivery_duration=total_delivery_duration, 
        routes=routes)