from math import radians, cos, sin, asin, sqrt


class Job:
    """"
    This class constructs job objects that contains all the necessary data
    """
    def __init__(self, job_id, fulfillment_id, label, location, delivery_time_window, store, status,
                 capacity, expected_eta, pickup_time, fulfillment_type, hub_label, address, customer_id, job_type):
        self.id = job_id
        self.fulfillment_id = fulfillment_id
        self.label = label
        self.location = location
        self.delivery_time_window = delivery_time_window
        self.store = store
        self.status  = status
        self.capacity = capacity
        self.expected_eta = expected_eta
        self.pickup_time = pickup_time
        self.fulfillment_type = fulfillment_type
        self.hub_label = hub_label
        self.address = address
        self.customer_id = customer_id
        self.type = job_type

    def get_latitude(self):
        return self.location[0]

    def get_longitude(self):
        return self.location[1]

    def get_store_opening(self):
        return self.store['time_window'][0]

    def get_store_closing(self):
        return self.store['time_window'][1]

    def get_time_start(self):
        return self.delivery_time_window[0]

    def get_time_end(self):
        return self.delivery_time_window[1]

    def __str__(self):
        stringbuilder = list()
        stringbuilder.append('id: ')
        stringbuilder.append(self.__dict__['id'])
        stringbuilder.append(', fulfillment : ')
        stringbuilder.append(self.__dict__['fulfillment_id'])
        stringbuilder.append(', customer_id: ')
        stringbuilder.append(self.__dict__['customer_id'])
        stringbuilder.append(', store_id: ')
        stringbuilder.append(self.__dict__['store'])
        return "JOB(" + "".join(str(x) for x in stringbuilder) + ")"

    def __repr__(self):
        return self.__str__()


class Store:
    """"
    This class constructs store objects that contains all the necessary data
    """
    def __init__(self, label, location, store_id, address):
        self.label = label
        self.location = location
        self.id = store_id
        self.address = address
        self.job = None

    def get_latitude(self):
        return self.location[0]

    def get_longitude(self):
        return self.location[1]

    def set_job(self, j):
        setattr(self, 'job', j)

    def get_job(self):
        return getattr(self, 'job')

    def copy(self):
        return Store(self.label, self.location, self.id, self.address)

    def __str__(self):
        stringbuilder = list()
        stringbuilder.append('id: ')
        stringbuilder.append(self.__dict__['id'])
        if self.job is not None:
            stringbuilder.append(', fulfillment: ')
            stringbuilder.append(self.job.fulfillment_id)
        return "Store(" + "".join(str(x) for x in stringbuilder) + ")"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        equals = False
        if isinstance(self, other.__class__):
            if self.label == other.label and self.location == other.location and self.id == other.id and \
                            self.address == other.address:
                equals = True
        return equals

    def __hash__(self) -> int:
        return self.id


class Deliverer:
    def __init__(self, driver_id, label, start_shift, end_shift, location, location_time_stamp, capacity,
                 pending_jobs, hub_label, contract_type, is_fulltime_driver, vehicle_type):

        self.id = driver_id
        self.label = label
        self.start_shift = start_shift
        self.end_shift = end_shift
        self.location = location
        self.location_time_stamp = location_time_stamp
        self.capacity = capacity
        self.pending_jobs = pending_jobs
        self.hub_label = hub_label
        self.contract_type = contract_type
        self.is_fulltime_driver = is_fulltime_driver
        self.vehicle_type = vehicle_type

    def get_latitude(self):
        return self.location[0]

    def get_longitude(self):
        return self.location[1]

    def get_shift_start(self):
        return self.start_shift

    def get_shift_end(self):
        return self.end_shift

    def __str__(self):
        stringbuilder = list('id: ')
        stringbuilder.append(self.__dict__['id'])
        return "Deliverer(" + "".join(str(x) for x in stringbuilder) + ")"

    def __repr__(self):
        return self.__str__()


class DistancesMatrix:
    def __init__(self, all_locations):
        self.locations = all_locations
        self.distances = self._generate_distances_matrix(all_locations)

    def _generate_distances_matrix(self, locations):
        distances = {}
        for loc1 in locations:
            distances[loc1] = {}
            for loc2 in locations:
                distance = self._calculate_distance(loc1, loc2)
                distances[loc1][loc2] = distance

        return distances

    def _calculate_distance(self, loc1, loc2):
        return self._haversine(loc1.get_longitude(), loc1.get_latitude(), loc2.get_longitude(), loc2.get_latitude())

    def _haversine(self, lon1, lat1, lon2, lat2):
        """
        Calculate the great circle distance between two points on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers. Use 3956 for miles
        return c * r

    def get_distance(self, loc1, loc2):
        return self.distances[loc1][loc2]

    def get_locations_sorted(self, for_, order='asc'):
        pass
        #sort on distance
