import utils
from tomtom_api import TomTomRouteFinder


tomtom = TomTomRouteFinder()
print(tomtom.get_remaining_requests())

origin, des = utils.get_random_od()

data = tomtom.get_route_json(origin, des)
utils.process_tomtom_routes(data)

print(tomtom.get_remaining_requests())
