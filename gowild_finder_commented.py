#!/usr/bin/env python3
# This is called a "shebang" - it tells the system to use python3 to run this script
# When you run ./gowild_finder.py, it knows to use python3 automatically

"""
Simple Frontier GoWild Flight Checker
Just check specific routes for GoWild availability - no complexity!
"""
# This is a docstring - it describes what the entire program does
# It's good practice to put this at the top of every Python file

# Import statements - these bring in external libraries we need
import requests     # For making HTTP requests to websites (like Frontier's booking API)
import json        # For parsing JSON data (JavaScript Object Notation - how APIs send data)
import html        # For unescaping HTML entities (like &amp; becomes &)
import random      # For generating random numbers (used for delays to seem human-like)
import time        # For adding delays between requests (to be respectful to servers)
import argparse    # For parsing command line arguments (like -o SFO -d LGA DEN)
from datetime import datetime, timedelta  # For working with dates and times
from bs4 import BeautifulSoup  # For parsing HTML content (scraping web pages)

class SimpleGoWildChecker:
    # This defines a class - think of it as a blueprint for creating objects
    # Classes group related functions (methods) and data together
    # We use a class here to keep all our flight-checking logic organized
    
    def __init__(self):
        # This is the constructor - it runs when we create a new SimpleGoWildChecker object
        # __init__ is a special Python method that initializes new instances
        
        # Create a requests session - this is like opening a browser and keeping it open
        # Sessions maintain cookies and connection pooling for efficiency
        # Instead of opening/closing a new connection for each request, we reuse one
        self.session = requests.Session()
        
        # Set up headers that make our requests look like they come from a real browser
        # Without these headers, websites might block us as a bot
        self.session.headers.update({
            # User-Agent tells the server what browser/app is making the request
            # We pretend to be Chrome on Windows to avoid bot detection
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            
            # Accept tells the server what content types we can handle
            # This says we prefer HTML, but can accept XML and other formats too
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            
            # Accept-Language tells the server what languages we prefer
            # en-US = American English (first choice), en = any English (backup)
            "Accept-Language": "en-US,en;q=0.5",
            
            # Accept-Encoding tells the server what compression we can handle
            # gzip, deflate, br are compression methods to make responses smaller/faster
            "Accept-Encoding": "gzip, deflate, br",
            
            # Connection: keep-alive means we want to reuse the TCP connection
            # This is more efficient than opening new connections for each request
            "Connection": "keep-alive"
        })
        
        # Dictionary to store airport code to human-readable name mappings
        # This makes the output more user-friendly (shows "Las Vegas, NV" instead of just "LAS")
        # We store this in the class so all methods can access it via self.airport_names
        # Extended with comprehensive Frontier route list
        self.airport_names = {
            # Major US Hubs
            'ATL': 'Atlanta, GA', 'DEN': 'Denver, CO', 'DFW': 'Dallas, TX', 'ORD': 'Chicago, IL',
            'LAX': 'Los Angeles, CA', 'LAS': 'Las Vegas, NV', 'PHX': 'Phoenix, AZ', 'MIA': 'Miami, FL',
            'MCO': 'Orlando, FL', 'TPA': 'Tampa, FL', 'SFO': 'San Francisco, CA', 'SEA': 'Seattle, WA',
            
            # East Coast
            'LGA': 'LaGuardia, NY', 'JFK': 'JFK New York, NY', 'BOS': 'Boston, MA', 'PHL': 'Philadelphia, PA',
            'BWI': 'Baltimore, MD', 'DCA': 'Washington DC', 'CLT': 'Charlotte, NC', 'RDU': 'Raleigh, NC',
            'BUF': 'Buffalo, NY', 'ISP': 'Islip, NY', 'SYR': 'Syracuse, NY', 'PWM': 'Portland, ME',
            'BTV': 'Burlington, VT', 'MDT': 'Harrisburg, PA', 'PIT': 'Pittsburgh, PA', 'CLE': 'Cleveland, OH',
            'CVG': 'Cincinnati, OH', 'CMH': 'Columbus, OH', 'IND': 'Indianapolis, IN', 'DTW': 'Detroit, MI',
            'MSP': 'Minneapolis, MN', 'MKE': 'Milwaukee, WI', 'GRB': 'Green Bay, WI', 'MSN': 'Madison, WI',
            'GRR': 'Grand Rapids, MI', 'ORF': 'Norfolk, VA', 'RIC': 'Richmond, VA', 'CHS': 'Charleston, SC',
            'SAV': 'Savannah, GA', 'JAX': 'Jacksonville, FL', 'PNS': 'Pensacola, FL', 'SRQ': 'Sarasota, FL',
            'FLL': 'Fort Lauderdale, FL', 'RSW': 'Fort Myers, FL', 'PBI': 'West Palm Beach, FL',
            'MYR': 'Myrtle Beach, SC', 'TTN': 'Trenton, NJ', 'EWR': 'Newark, NJ', 'HPN': 'White Plains, NY',
            
            # West Coast  
            'SJC': 'San Jose, CA', 'OAK': 'Oakland, CA', 'SAN': 'San Diego, CA', 'SMF': 'Sacramento, CA',
            'SNA': 'Orange County, CA', 'ONT': 'Ontario, CA', 'BUR': 'Burbank, CA', 'PSP': 'Palm Springs, CA',
            'PDX': 'Portland, OR', 'SLC': 'Salt Lake City, UT', 'RNO': 'Reno, NV', 'BOI': 'Boise, ID',
            'MSO': 'Missoula, MT', 'GEG': 'Spokane, WA', 'FAR': 'Fargo, ND', 'FSD': 'Sioux Falls, SD',
            
            # Central US
            'AUS': 'Austin, TX', 'SAT': 'San Antonio, TX', 'IAH': 'Houston, TX', 'HOU': 'Houston Hobby, TX',
            'ELP': 'El Paso, TX', 'CRP': 'Corpus Christi, TX', 'TUS': 'Tucson, AZ', 'OKC': 'Oklahoma City, OK',
            'TUL': 'Tulsa, OK', 'MCI': 'Kansas City, MO', 'STL': 'St. Louis, MO', 'MSY': 'New Orleans, LA',
            'MEM': 'Memphis, TN', 'BNA': 'Nashville, TN', 'TYS': 'Knoxville, TN', 'LIT': 'Little Rock, AR',
            'XNA': 'Bentonville, AR', 'DSM': 'Des Moines, IA', 'CID': 'Cedar Rapids, IA', 'OMA': 'Omaha, NE',
            
            # International/Caribbean
            'CUN': 'Cancun, Mexico', 'PVR': 'Puerto Vallarta, Mexico', 'SJD': 'Los Cabos, Mexico',
            'SJU': 'San Juan, Puerto Rico', 'BQN': 'Aguadilla, Puerto Rico', 'PSE': 'Ponce, Puerto Rico',
            'STX': 'St. Croix, USVI', 'STT': 'St. Thomas, USVI', 'SXM': 'St. Maarten', 'ANU': 'Antigua',
            'NAS': 'Nassau, Bahamas', 'MBJ': 'Montego Bay, Jamaica', 'KIN': 'Kingston, Jamaica',
            'PUJ': 'Punta Cana, DR', 'SDQ': 'Santo Domingo, DR', 'STI': 'Santiago, DR', 'POP': 'Puerto Plata, DR',
            'SAL': 'San Salvador, El Salvador', 'GUA': 'Guatemala City', 'SJO': 'San Jose, Costa Rica',
            'SAP': 'San Pedro Sula, Honduras', 'BGI': 'Bridgetown, Barbados', 'POS': 'Port of Spain, Trinidad',
            'AUA': 'Aruba', 'PLS': 'Providenciales, Turks & Caicos'
        }

    def check_flight(self, origin, destination, date):
        # This method checks a single flight route for GoWild availability
        # It takes 3 parameters: origin airport, destination airport, and date
        # The docstring below explains what this function does
        """Check a single route for GoWild flights"""
        
        # Print status message so user knows what we're checking
        # .get() method safely looks up airport name, returns the code if not found
        # f-strings (f"...") allow us to embed variables directly in strings
        print(f"Checking {origin} → {destination} ({self.airport_names.get(destination, destination)})...")
        
        # Format the date for Frontier's URL format
        # Frontier expects dates like "Jan%2001,%202025" (URL-encoded)
        # strftime converts datetime to string format, replace() handles URL encoding
        date_str = date.strftime("%b-%d,-%Y").replace("-", "%20")
        
        # Build the URL for Frontier's internal flight search API
        # This is the same URL that gets called when you search on their website
        # o1=origin, d1=destination, dd1=departure date, ADT=1 adult, mon=Monday?, promo=no promo code
        url = f"https://booking.flyfrontier.com/Flight/InternalSelect?o1={origin}&d1={destination}&dd1={date_str}&ADT=1&mon=true&promo="
        
        # Add a random delay to be respectful to Frontier's servers
        # random.uniform(2, 4) gives us a random number between 2 and 4 seconds
        # This makes our requests look more human-like and avoids overwhelming their servers
        time.sleep(random.uniform(2, 4))
        
        # Use try/except to handle potential errors gracefully
        # Network requests can fail for many reasons (timeout, server error, etc.)
        try:
            # Make the HTTP GET request to Frontier's API
            # timeout=30 means give up if no response after 30 seconds
            # self.session.get uses our configured session with headers
            response = self.session.get(url, timeout=30)
            
            # Check if the request was successful
            # HTTP status code 200 means "OK", anything else indicates an error
            if response.status_code != 200:
                # Print error message with the specific HTTP status code
                print(f"  ❌ Error: HTTP {response.status_code}")
                # Return empty list to indicate no flights found
                return []
            
            # If we got a successful response, try to extract GoWild flights from it
            # This calls our helper method (defined below) to parse the HTML/JSON
            flights = self._extract_gowild_flights(response, origin, destination)
            
            # Check if we found any GoWild flights
            if flights:
                # Success! Print how many flights we found
                print(f"  ✅ Found {len(flights)} GoWild flight(s)!")
                
                # Loop through each flight and print its detailed information
                # enumerate(flights, 1) gives us both the flight object and a counter starting at 1
                for i, flight in enumerate(flights, 1):
                    # Print header with flight number, stops, and price
                    print(f"    {i}. {flight['stops']} - ${flight['price']}")
                    
                    # Print departure information
                    print(f"       🛫 Departs: {flight['departure_time']} from {flight['departure_airport']}")
                    
                    # Print arrival information
                    print(f"       🛬 Arrives: {flight['arrival_time']} at {flight['arrival_airport']}")
                    
                    # Print total flight duration
                    print(f"       ⏱️  Total Duration: {flight['duration']}")
                    
                    # Print layover information for connecting flights
                    if flight['layovers']:
                        layover_text = " → ".join(flight['layovers'])
                        print(f"       🔄 Connections: {layover_text}")
                    
                    # Print aircraft and flight number if available
                    if flight['flight_number'] != 'Unknown':
                        aircraft_info = f"Flight {flight['flight_number']}"
                        if flight['aircraft_type'] != 'Unknown':
                            aircraft_info += f" ({flight['aircraft_type']})"
                        print(f"       ✈️  {aircraft_info}")
                    
                    # Print seat availability if known
                    if flight['seats']:
                        print(f"       💺 Seats available: {flight['seats']}")
                    
                    # Add spacing between flights for readability
                    print()
                
                # Return the flights list so calling code can use this data
                return flights
            else:
                # No GoWild flights found on this route
                print(f"  ❌ No GoWild flights found")
                print()
                # Return empty list
                return []
                
        # Catch any exception that might occur during the request or processing
        except Exception as e:
            # Print the error message so we know what went wrong
            print(f"  ❌ Error checking route: {e}")
            print()
            # Return empty list since we couldn't get flight data
            return []

    def _extract_gowild_flights(self, response, origin, destination):
        # This is a private method (indicated by the underscore prefix)
        # It extracts GoWild flight data from Frontier's HTML response
        # The response contains HTML with embedded JavaScript that has the flight data
        """Extract GoWild flights from response"""
        
        try:
            # Parse the HTML response using BeautifulSoup
            # BeautifulSoup creates a tree structure we can search through
            # "html.parser" tells it to use Python's built-in HTML parser
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find all <script> tags that contain JavaScript
            # Frontier embeds the flight data as JSON inside JavaScript code
            scripts = soup.find_all("script", type="text/javascript")
            
            # Loop through each script tag to find the one with flight data
            for script in scripts:
                # Skip empty scripts or scripts that don't contain flight data
                # We look for 'journeys' because that's the key Frontier uses for flight data
                if not script.text or 'journeys' not in script.text:
                    continue
                
                # Unescape HTML entities in the JavaScript code
                # HTML entities like &quot; get converted back to actual quotes
                script_content = html.unescape(script.text)
                
                # Look for JSON data within the JavaScript
                # The flight data is stored as a JSON object inside the script
                if '{' in script_content:
                    # Find where the JSON object starts
                    start = script_content.find('{')
                    # If no opening brace found, skip this script
                    if start == -1:
                        continue
                    
                    # We need to find where the JSON object ends
                    # JSON objects have matching { and } braces
                    # We count braces to find the complete object
                    brace_count = 0
                    end = start
                    
                    # Loop through each character starting from the opening brace
                    for i in range(start, len(script_content)):
                        if script_content[i] == '{':
                            # Found opening brace, increment counter
                            brace_count += 1
                        elif script_content[i] == '}':
                            # Found closing brace, decrement counter
                            brace_count -= 1
                            # When counter reaches 0, we've found the end of the JSON object
                            if brace_count == 0:
                                end = i + 1
                                break
                    
                    # Extract the JSON string from the JavaScript
                    json_str = script_content[start:end]
                    
                    try:
                        # Parse the JSON string into a Python dictionary
                        data = json.loads(json_str)
                        # Call our helper method to extract GoWild flights from the data
                        return self._parse_gowild_flights(data)
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try the next script tag
                        continue
            
            # If we didn't find any valid flight data, return empty list
            return []
            
        except Exception as e:
            # Handle any unexpected errors during extraction
            print(f"Error extracting flight data: {e}")
            return []

    def _parse_gowild_flights(self, data):
        # This private method parses the JSON data structure to find GoWild flights
        # Frontier's JSON has a specific structure: data -> journeys -> flights
        """Parse JSON data for GoWild flights"""
        
        # Initialize empty list to store flight information
        flights = []
        
        try:
            # Check if the data has the expected structure
            # 'journeys' is the top-level key that contains flight information
            if 'journeys' not in data or not data['journeys']:
                # No journey data found, return empty list
                return flights
            
            # Get the first journey (usually there's only one for one-way searches)
            journey = data['journeys'][0]
            
            # Check if this journey has flight data
            if 'flights' not in journey:
                return flights
            
            # Loop through each flight in the journey
            for flight in journey['flights']:
                # Check if this flight has GoWild fare enabled
                # .get() safely gets a value, returns None if key doesn't exist
                if flight.get('isGoWildFareEnabled'):
                    # Get the first leg of the flight (departure info)
                    # Most flights have multiple legs if there are connections
                    leg = flight['legs'][0]
                    
                    # Get the last leg for arrival information (in case of connections)
                    # For nonstop flights, there's only one leg, for connecting flights there are multiple
                    last_leg = flight['legs'][-1] if flight['legs'] else leg
                    
                    # Calculate layover/transit information for connecting flights
                    layover_info = []
                    if len(flight['legs']) > 1:
                        # This is a connecting flight - extract layover details
                        for i in range(len(flight['legs']) - 1):
                            current_leg = flight['legs'][i]
                            next_leg = flight['legs'][i + 1]
                            layover_airport = current_leg.get('arrivalAirport', 'Unknown')
                            # Try to calculate layover time if available
                            layover_duration = "Unknown"
                            # Some responses include layover duration in the flight structure
                            if 'layoverDuration' in current_leg:
                                layover_duration = current_leg['layoverDuration']
                            layover_info.append(f"{layover_airport} ({layover_duration})")
                    
                    # Create a dictionary with comprehensive flight information
                    # We extract specific fields and provide defaults if they're missing
                    flight_info = {
                        'stops': flight.get('stopsText', 'Unknown'),           # "Nonstop", "1 Stop", etc.
                        'price': flight.get('goWildFare', 0),                 # Price in dollars
                        'departure_time': leg.get('departureDateFormatted', 'Unknown'),  # Formatted departure time
                        'departure_airport': leg.get('departureAirport', 'Unknown'),        # Departure airport code
                        'arrival_time': last_leg.get('arrivalDateFormatted', 'Unknown'), # Formatted arrival time
                        'arrival_airport': last_leg.get('arrivalAirport', 'Unknown'),  # Arrival airport code
                        'duration': flight.get('duration', 'Unknown'),        # Total flight time
                        'seats': flight.get('goWildFareSeatsRemaining'),       # Available seats (can be None)
                        'layovers': layover_info,                             # List of layover airports and durations
                        'aircraft_type': leg.get('aircraftType', 'Unknown'),  # Aircraft model if available
                        'flight_number': leg.get('flightNumber', 'Unknown')   # Flight number if available
                    }
                    
                    # Add this flight to our results list
                    flights.append(flight_info)
            
        # Handle potential errors when accessing the nested data structure
        except (KeyError, IndexError, TypeError) as e:
            # KeyError: if a expected key doesn't exist in the dictionary
            # IndexError: if we try to access an index that doesn't exist in a list
            # TypeError: if we try to use a None value as a dictionary or list
            print(f"Error parsing flight data: {e}")
        
        # Return the list of GoWild flights we found
        return flights

    def check_multiple_routes(self, origin, destinations, date):
        # This method checks multiple destinations from a single origin
        # It's the main orchestration method that coordinates checking multiple routes
        """Check multiple routes from one origin"""
        
        # Print header information to show what we're searching for
        # This gives the user context about the search being performed
        print(f"🔍 Checking GoWild flights from {origin} ({self.airport_names.get(origin, origin)})")
        print(f"📅 Date: {date.strftime('%A, %B %d, %Y')}")  # Format: "Monday, January 01, 2025"
        print(f"🎯 Destinations: {', '.join(destinations)}")  # Join list into comma-separated string
        print("=" * 60)  # Print a line separator for visual clarity
        
        # Initialize lists to track results across all routes
        all_flights = []              # Store all flights found across all destinations
        available_destinations = []   # Store destinations that have GoWild flights
        
        # Loop through each destination and check for flights
        for destination in destinations:
            # Skip if destination is the same as origin (can't fly to same airport)
            if destination.upper() == origin.upper():
                print(f"Skipping {destination} (same as origin)")
                continue
                
            # Check this specific route for GoWild flights
            # .upper() ensures airport codes are uppercase (standard format)
            flights = self.check_flight(origin.upper(), destination.upper(), date)
            
            # If we found flights on this route
            if flights:
                # Add all flights from this route to our master list
                all_flights.extend(flights)
                # Add this destination to our list of available destinations
                available_destinations.append(destination.upper())
        
        # Print summary of results after checking all routes
        print("=" * 60)  # Another visual separator
        print(f"📊 SUMMARY")
        print(f"Total routes with GoWild flights: {len(available_destinations)}")
        print(f"Total GoWild flights found: {len(all_flights)}")
        
        # Show available destinations if any were found
        if available_destinations:
            print(f"Available destinations: {', '.join(available_destinations)}")
        else:
            print("❌ No GoWild flights found on any route")
        
        # Return the data so other methods can use it
        return all_flights, available_destinations

    def check_both_days(self, origin, destinations):
        # This method checks both today and tomorrow for GoWild flights
        # It provides a comprehensive view of flight availability across two days
        """Check both today and tomorrow for GoWild flights"""
        
        # Get today's date and tomorrow's date
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        # Print header for the dual-day search
        print("🔍🔍 CHECKING BOTH TODAY AND TOMORROW 🔍🔍")
        print("=" * 80)  # Longer separator for emphasis
        
        # Check today's flights first
        print("\n🌅 TODAY'S FLIGHTS:")
        print("=" * 40)
        # Call our existing method to check today's routes and capture results
        today_flights, today_destinations = self.check_multiple_routes(origin, destinations, today)
        
        # Visual separator between today and tomorrow
        print("\n" + "=" * 80)
        
        # Check tomorrow's flights
        print("\n🌄 TOMORROW'S FLIGHTS:")
        print("=" * 40)
        # Call our existing method to check tomorrow's routes and capture results
        tomorrow_flights, tomorrow_destinations = self.check_multiple_routes(origin, destinations, tomorrow)
        
        # Create a combined summary section
        print("\n" + "=" * 80)
        print("🎯 COMBINED SUMMARY (TODAY + TOMORROW)")
        print("=" * 80)
        
        # Combine destinations from both days (using set to avoid duplicates)
        all_destinations = set(today_destinations + tomorrow_destinations)
        # Calculate total flights across both days
        total_flights = len(today_flights) + len(tomorrow_flights)
        
        # Print comprehensive statistics
        print(f"📊 Total unique destinations with GoWild flights: {len(all_destinations)}")
        print(f"📊 Total GoWild flights found: {total_flights}")
        print(f"   • Today: {len(today_flights)} flights")
        print(f"   • Tomorrow: {len(tomorrow_flights)} flights")
        
        # Show all available destinations across both days
        if all_destinations:
            # Sort destinations alphabetically for consistent display
            print(f"📍 Available destinations: {', '.join(sorted(all_destinations))}")
        else:
            print("❌ No GoWild flights found on any route for either day")

def main():
    # This is the main function that runs when the script is executed
    # It handles command-line arguments and coordinates the overall program flow
    
    # Create argument parser to handle command-line options
    # argparse makes it easy to create professional command-line interfaces
    parser = argparse.ArgumentParser(description='Check specific routes for Frontier GoWild flights')
    
    # Define required argument for origin airport
    # required=True means the program won't run without this argument
    parser.add_argument('-o', '--origin', required=True, help='Origin airport code (e.g., LGA)')
    
    # Define required argument for destination airports
    # nargs='+' means it accepts one or more values (you can specify multiple destinations)
    parser.add_argument('-d', '--destinations', required=True, nargs='+', help='Destination airport codes (e.g., SJC SFO DEN)')
    
    # Define optional argument for how many days from today
    # type=int converts the string input to an integer
    # default=1 means if not specified, it defaults to 1 (tomorrow)
    parser.add_argument('--days', type=int, default=1, help='Days from today (default: 1 = tomorrow)')
    
    # Define optional argument to check both today and tomorrow
    # action='store_true' means this is a flag - if present, it's True, otherwise False
    parser.add_argument('--both', action='store_true', help='Check both today and tomorrow')
    
    # Parse the command-line arguments
    # This processes sys.argv and creates an object with the argument values
    args = parser.parse_args()
    
    # Create an instance of our flight checker class
    # This runs the __init__ method we defined earlier
    checker = SimpleGoWildChecker()
    
    # Check if the user wants to search both today and tomorrow
    if args.both:
        # Use the special method that checks both days and provides combined results
        checker.check_both_days(args.origin.upper(), args.destinations)
    else:
        # Standard single-day search
        # Calculate the flight date based on the days argument
        # datetime.now() gets current date/time, timedelta adds the specified days
        flight_date = datetime.now() + timedelta(days=args.days)
        
        # Run the main flight checking logic for a single date
        # .upper() ensures the origin is uppercase, destinations list is passed as-is
        checker.check_multiple_routes(args.origin.upper(), args.destinations, flight_date)

# This is a Python idiom that runs main() only if this script is executed directly
# If this file is imported as a module, main() won't run automatically
# __name__ == "__main__" is True only when the script is run directly (not imported)
if __name__ == "__main__":
    main()
