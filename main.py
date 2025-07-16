import argparse
import sys
import utils
import random 
import time

def main():
    parser = argparse.ArgumentParser(description="Route scraping tool")

    # API type
    parser.add_argument(
        "--api_type",
        type=str,
        choices=["mapbox", "tomtom", "here"],
        required=True,
        help="API type to use: mapbox, tomtom, or here"
    )

    # Scrape mode
    parser.add_argument(
        "--scrape_mode",
        type=str,
        choices=["random_od_place", "random_od_seg", "specific"],
        required=True,
        help=(
            "Type of scraping task to perform. "
            "For 'specific', you must have an 'input.txt' file "
            "in the same directory with at least 2 non-empty lines. "
            "Each line should be either a place/segment name or lat,lon depending on your usage."
        )
    )

    # Number of routes to scrape (or 'schedule' mode)
    parser.add_argument(
        "--num_route",
        type=str,
        default="schedule",
        help="Number of routes to scrape or 'schedule' to follow daily time slots"
    )

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)


    args = parser.parse_args()

    # Validate specific mode requirements
    if args.scrape_mode in ["specific_seg", "specific_place"]:
        utils.validate_input_file("input.txt")


    # Print parsed args
    print("Parsed arguments:")
    print(f"  API type    : {args.api_type}")
    print(f"  Scrape mode : {args.scrape_mode}")
    print(f"  Num routes   : {args.num_route}")


    org, des = None, None


    if args.api_type == "mapbox": 
        from mapbox_api import MapboxRouteFinder

        mapbox = MapboxRouteFinder()
        remaining = mapbox.get_remaining_requests()

        if args.num_route == "schedule":
            # TODO: Handle time-slot schedule logic
            print("TODO: Scheduled scraping mode not implemented yet")
            return
        
        try:
            num = int(args.num_route)
        except ValueError:
            print("num_route must be an integer or 'schedule'")
            sys.exit(1)

        if num > remaining:
            print(f"Not enough request quota left. Requested: {num}, Remaining: {remaining}")
            sys.exit(1)

        print(f"Proceeding to scrape {num} routes using Mapbox API...")

        for _ in range(num):

            org, des = utils.get_od(args.scrape_mode)

            data = mapbox.get_route_json(org, des)
            if data is None:
                print("Failed to get route data from Mapbox API")
                continue
            utils.process_mapbox_routes(data)

            # Simulate delay to avoid hitting rate limits
            delay = random.uniform(0.5, 1.5)
            time.sleep(delay)
            print(f"Calling Mapbox API for route {_ + 1}")
    
    elif args.api_type == "tomtom":
        from tomtom_api import TomTomRouteFinder

        tomtom = TomTomRouteFinder()
        remaining = tomtom.get_remaining_requests()

        if args.num_route == "schedule":
            print("TODO: Scheduled scraping mode not implemented yet")
            return
        
        try:
            num = int(args.num_route)
        except ValueError:
            print("num_route must be an integer or 'schedule'")
            sys.exit(1)

        if num > remaining:
            print(f"Not enough request quota left. Requested: {num}, Remaining: {remaining}")
            sys.exit(1)

        print(f"Proceeding to scrape {num} routes using TomTom API...")

        for i in range(num):
            org, des = utils.get_od(args.scrape_mode)
            data = tomtom.get_route_json(org, des)
            if data is None:
                print("Failed to get route data from TomTom API")
                continue

            utils.process_tomtom_routes(data)

            delay = random.uniform(0.5, 1.5)
            time.sleep(delay)
            print(f"TomTom route {i + 1} processed")
    
if __name__ == "__main__":
    main()
