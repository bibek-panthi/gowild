#!/usr/bin/env python3
"""
Simple Frontier GoWild Flight Checker
Just check specific routes for GoWild availability - no complexity!
"""

import requests
import json
import html
import random
import time
import argparse
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class SimpleGoWildChecker:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        })
        
        # Domestic US airports for --all-domestic search
        self.domestic_airports = [
            'ATL', 'DEN', 'DFW', 'ORD', 'LAX', 'LAS', 'PHX', 'MIA', 'MCO', 'TPA', 'SFO', 'SEA',
            'LGA', 'JFK', 'BOS', 'PHL', 'BWI', 'DCA', 'CLT', 'RDU', 'BUF', 'ISP', 'SYR', 'PWM',
            'BTV', 'MDT', 'PIT', 'CLE', 'CVG', 'CMH', 'IND', 'DTW', 'MSP', 'MKE', 'GRB', 'MSN',
            'GRR', 'ORF', 'RIC', 'CHS', 'SAV', 'JAX', 'PNS', 'SRQ', 'FLL', 'RSW', 'PBI',
            'MYR', 'TTN', 'EWR', 'SJC', 'OAK', 'SAN', 'SMF', 'SNA', 'ONT', 'BUR', 'PSP',
            'PDX', 'SLC', 'RNO', 'BOI', 'MSO', 'GEG', 'FAR', 'FSD', 'AUS', 'SAT', 'IAH', 'HOU',
            'ELP', 'CRP', 'TUS', 'OKC', 'TUL', 'MCI', 'STL', 'MSY', 'MEM', 'BNA', 'TYS', 'LIT',
            'XNA', 'DSM', 'CID', 'OMA'
        ]
        
        # Airport names for display - comprehensive Frontier route list
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

    def check_flight(self, origin, destination, date, quiet_mode=False):
        """Check a single route for GoWild flights"""
        if not quiet_mode:
        print(f"Checking {origin} → {destination} ({self.airport_names.get(destination, destination)})...")
        
        # Format date for URL
        date_str = date.strftime("%b-%d,-%Y").replace("-", "%20")
        
        # Build URL
        url = f"https://booking.flyfrontier.com/Flight/InternalSelect?o1={origin}&d1={destination}&dd1={date_str}&ADT=1&mon=true&promo="
        
        # Add some delay to be respectful
        time.sleep(random.uniform(2, 4))
        
        try:
            # Make request
            response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"  ❌ Error: HTTP {response.status_code}")
                return []
            
            # Extract flight data
            flights = self._extract_gowild_flights(response, origin, destination)
            
            if flights:
                if not quiet_mode:
                print(f"  ✅ Found {len(flights)} GoWild flight(s)!")
                for i, flight in enumerate(flights, 1):
                    print(f"    {i}. {flight['stops']} - ${flight['price']}")
                        
                        # Show detailed leg-by-leg information
                        if 'all_legs' in flight and len(flight['all_legs']) > 1:
                            # Multi-leg flight - show each segment
                            for leg_idx, leg in enumerate(flight['all_legs']):
                                dep_airport = leg.get('departureStation', 'Unknown')
                                arr_airport = leg.get('arrivalStation', 'Unknown') 
                                dep_time = leg.get('departureDateFormatted', 'Unknown')
                                arr_time = leg.get('arrivalDateFormatted', 'Unknown')
                                
                                if leg_idx == 0:
                                    print(f"       🛫 Departs: {dep_time} from {dep_airport}")
                                
                                print(f"       ✈️  Leg {leg_idx + 1}: {dep_airport} → {arr_airport}")
                                print(f"           Arrives: {arr_time} at {arr_airport}")
                                
                                # Show layover info if not the last leg
                                if leg_idx < len(flight['all_legs']) - 1:
                                    next_leg = flight['all_legs'][leg_idx + 1]
                                    next_dep_time = next_leg.get('departureDateFormatted', 'Unknown')
                                    layover_duration = self._calculate_layover_duration(arr_time, next_dep_time)
                                    print(f"           🔄 Layover at {arr_airport}: {layover_duration}")
                                    print(f"           🛫 Next departure: {next_dep_time}")
                            
                            # Final arrival
                            final_leg = flight['all_legs'][-1]
                            final_arr_time = final_leg.get('arrivalDateFormatted', 'Unknown')
                            final_arr_airport = final_leg.get('arrivalStation', 'Unknown')
                            print(f"       🛬 Final arrival: {final_arr_time} at {final_arr_airport}")
                        else:
                            # Single leg flight
                            print(f"       🛫 Departs: {flight['departure_time']} from {flight['departure_airport']}")
                            print(f"       🛬 Arrives: {flight['arrival_time']} at {flight['arrival_airport']}")
                        
                        print(f"       ⏱️  Total Duration: {flight['duration']}")
                        
                        if flight['flight_number'] != 'Unknown':
                            aircraft_info = f"Flight {flight['flight_number']}"
                            if flight['aircraft_type'] != 'Unknown':
                                aircraft_info += f" ({flight['aircraft_type']})"
                            print(f"       ✈️  {aircraft_info}")
                        
                    if flight['seats']:
                            print(f"       💺 Seats available: {flight['seats']}")
                        
                        print()
                print()
                return flights
            else:
                print(f"  ❌ No GoWild flights found")
                print()
                return []
                
        except Exception as e:
            print(f"  ❌ Error checking route: {e}")
            print()
            return []

    def _extract_gowild_flights(self, response, origin, destination):
        """Extract GoWild flights from response"""
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            scripts = soup.find_all("script", type="text/javascript")
            
            for script in scripts:
                if not script.text or 'journeys' not in script.text:
                    continue
                
                # Find JSON data
                script_content = html.unescape(script.text)
                
                # Look for the flight data
                if '{' in script_content:
                    # Find the JSON object
                    start = script_content.find('{')
                    if start == -1:
                        continue
                    
                    # Count braces to find the end
                    brace_count = 0
                    end = start
                    
                    for i in range(start, len(script_content)):
                        if script_content[i] == '{':
                            brace_count += 1
                        elif script_content[i] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end = i + 1
                                break
                    
                    json_str = script_content[start:end]
                    
                    try:
                        data = json.loads(json_str)
                        return self._parse_gowild_flights(data)
                    except json.JSONDecodeError:
                        continue
            
            return []
            
        except Exception as e:
            print(f"Error extracting flight data: {e}")
            return []

    def _parse_gowild_flights(self, data):
        """Parse JSON data for GoWild flights"""
        flights = []
        
        try:
            if 'journeys' not in data or not data['journeys']:
                return flights
            
            journey = data['journeys'][0]
            if 'flights' not in journey:
                return flights
            
            for flight in journey['flights']:
                if flight.get('isGoWildFareEnabled'):
                    legs = flight['legs']
                    first_leg = legs[0]
                    last_leg = legs[-1] if legs else first_leg
                    
                    # Calculate layover information for connecting flights
                    layover_info = []
                    if len(legs) > 1:
                        for i in range(len(legs) - 1):
                            current_leg = legs[i]
                            next_leg = legs[i + 1]
                            
                            # Get layover airport (using correct key)
                            layover_airport = current_leg.get('arrivalStation', 'Unknown')
                            
                            # Calculate layover duration by parsing times
                            layover_duration = "Unknown"
                            try:
                                arrival_time_str = current_leg.get('arrivalDateFormatted', '')
                                departure_time_str = next_leg.get('departureDateFormatted', '')
                                
                                if arrival_time_str and departure_time_str:
                                    layover_duration = self._calculate_layover_duration(arrival_time_str, departure_time_str)
                            except:
                                layover_duration = "Unknown"
                                
                            layover_info.append(f"{layover_airport} ({layover_duration})")
                    
                    flight_info = {
                        'stops': flight.get('stopsText', 'Unknown'),
                        'price': flight.get('goWildFare', 0),
                        'departure_time': first_leg.get('departureDateFormatted', 'Unknown'),
                        'departure_airport': first_leg.get('departureStation', 'Unknown'),
                        'arrival_time': last_leg.get('arrivalDateFormatted', 'Unknown'),
                        'arrival_airport': last_leg.get('arrivalStation', 'Unknown'),
                        'duration': flight.get('duration', 'Unknown'),
                        'seats': flight.get('goWildFareSeatsRemaining'),
                        'layovers': layover_info,
                        'aircraft_type': first_leg.get('aircraftType', 'Unknown'),
                        'flight_number': first_leg.get('flightNumber', 'Unknown'),
                        'all_legs': legs  # Store all legs for detailed display
                    }
                    flights.append(flight_info)
            
        except (KeyError, IndexError, TypeError) as e:
            print(f"Error parsing flight data: {e}")
        
        return flights

    def _calculate_layover_duration(self, arrival_time_str, departure_time_str):
        """Calculate layover duration between two time strings"""
        try:
            from datetime import datetime
            import re
            
            # Parse times like "7:32 AM" and "8:32 PM"
            def parse_time(time_str):
                # Handle formats like "7:32 AM", "12:16 AM", etc.
                time_str = time_str.strip()
                match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str)
                if match:
                    hour, minute, ampm = match.groups()
                    hour = int(hour)
                    minute = int(minute)
                    
                    # Convert to 24-hour format
                    if ampm == 'PM' and hour != 12:
                        hour += 12
                    elif ampm == 'AM' and hour == 12:
                        hour = 0
                        
                    return hour * 60 + minute  # Return minutes since midnight
                return None
            
            arrival_minutes = parse_time(arrival_time_str)
            departure_minutes = parse_time(departure_time_str)
            
            if arrival_minutes is not None and departure_minutes is not None:
                # Handle next-day departures
                if departure_minutes < arrival_minutes:
                    departure_minutes += 24 * 60  # Add 24 hours
                
                layover_minutes = departure_minutes - arrival_minutes
                
                if layover_minutes < 60:
                    return f"{layover_minutes}m"
                else:
                    hours = layover_minutes // 60
                    minutes = layover_minutes % 60
                    if minutes == 0:
                        return f"{hours}h"
                    else:
                        return f"{hours}h {minutes}m"
            
            return "Unknown"
        except Exception as e:
            return "Unknown"

    def check_multiple_routes(self, origin, destinations, date):
        """Check multiple routes from one origin"""
        print(f"🔍 Checking GoWild flights from {origin} ({self.airport_names.get(origin, origin)})")
        print(f"📅 Date: {date.strftime('%A, %B %d, %Y')}")
        print(f"🎯 Destinations: {', '.join(destinations)}")
        print("=" * 60)
        
        all_flights = []
        available_destinations = []
        
        for destination in destinations:
            if destination.upper() == origin.upper():
                print(f"Skipping {destination} (same as origin)")
                continue
                
            flights = self.check_flight(origin.upper(), destination.upper(), date)
            if flights:
                all_flights.extend(flights)
                available_destinations.append(destination.upper())
        
        # Summary
        print("=" * 60)
        print(f"📊 SUMMARY")
        print(f"Total routes with GoWild flights: {len(available_destinations)}")
        print(f"Total GoWild flights found: {len(all_flights)}")
        
        if available_destinations:
            print(f"Available destinations: {', '.join(available_destinations)}")
        else:
            print("❌ No GoWild flights found on any route")
        
        return all_flights, available_destinations

    def check_both_days(self, origin, destinations):
        """Check both today and tomorrow for GoWild flights"""
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        
        print("🔍🔍 CHECKING BOTH TODAY AND TOMORROW 🔍🔍")
        print("=" * 80)
        
        # Check today
        print("\n🌅 TODAY'S FLIGHTS:")
        print("=" * 40)
        today_flights, today_destinations = self.check_multiple_routes(origin, destinations, today)
        
        print("\n" + "=" * 80)
        
        # Check tomorrow  
        print("\n🌄 TOMORROW'S FLIGHTS:")
        print("=" * 40)
        tomorrow_flights, tomorrow_destinations = self.check_multiple_routes(origin, destinations, tomorrow)
        
        # Combined summary
        print("\n" + "=" * 80)
        print("🎯 COMBINED SUMMARY (TODAY + TOMORROW)")
        print("=" * 80)
        
        all_destinations = set(today_destinations + tomorrow_destinations)
        total_flights = len(today_flights) + len(tomorrow_flights)
        
        print(f"📊 Total unique destinations with GoWild flights: {len(all_destinations)}")
        print(f"📊 Total GoWild flights found: {total_flights}")
        print(f"   • Today: {len(today_flights)} flights")
        print(f"   • Tomorrow: {len(tomorrow_flights)} flights")
        
        if all_destinations:
            print(f"📍 Available destinations: {', '.join(sorted(all_destinations))}")
        else:
            print("❌ No GoWild flights found on any route for either day")

    def discover_all_domestic(self, origin, date):
        """Discover all domestic GoWild flights from an origin airport"""
        print(f"🔍🌎 DISCOVERING ALL DOMESTIC GOWILD FLIGHTS FROM {origin}")
        print(f"📅 Date: {date.strftime('%A, %B %d, %Y')}")
        print(f"🎯 Searching {len(self.domestic_airports)} domestic destinations...")
        print("=" * 80)
        print("⚠️  This will take a while - being respectful to Frontier's servers")
        print("=" * 80)
        
        # Filter out the origin airport from domestic list
        destinations_to_check = [airport for airport in self.domestic_airports if airport != origin.upper()]
        
        all_flights = []
        available_destinations = []
        total_checked = 0
        
        for i, destination in enumerate(destinations_to_check, 1):
            print(f"\n[{i}/{len(destinations_to_check)}] Checking {origin} → {destination} ({self.airport_names.get(destination, destination)})...")
            
            # Add respectful delays between each check
            if i > 1:  # Don't delay before the first request
                print("   ⏳ Pausing to be respectful to servers...")
                time.sleep(random.uniform(5, 8))  # Longer delays for discovery mode
            
            flights = self.check_flight(origin.upper(), destination, date, quiet_mode=True)
            total_checked += 1
            
            if flights:
                all_flights.extend(flights)
                available_destinations.append(destination)
                print(f"   ✅ Found {len(flights)} GoWild flights!")
            else:
                print(f"   ❌ No GoWild flights")
        
        # Final comprehensive summary
        print("\n" + "=" * 80)
        print("🎯 DOMESTIC DISCOVERY COMPLETE!")
        print("=" * 80)
        print(f"📊 Checked {total_checked} domestic destinations")
        print(f"📊 Found GoWild flights to {len(available_destinations)} destinations")
        print(f"📊 Total GoWild flights discovered: {len(all_flights)}")
        
        if available_destinations:
            # Group by price for better overview
            price_groups = {}
            for flight in all_flights:
                price = flight['price']
                if price not in price_groups:
                    price_groups[price] = []
                price_groups[price].append(flight)
            
            print(f"\n💰 PRICE BREAKDOWN:")
            for price in sorted(price_groups.keys()):
                flights_at_price = price_groups[price]
                destinations_at_price = set()
                for flight in flights_at_price:
                    destinations_at_price.add(flight['arrival_airport'])
                
                print(f"   ${price}: {len(flights_at_price)} flights to {len(destinations_at_price)} destinations")
                dest_list = sorted(list(destinations_at_price))
                print(f"      Destinations: {', '.join(dest_list[:10])}")
                if len(dest_list) > 10:
                    print(f"      + {len(dest_list) - 10} more...")
            
            print(f"\n📍 ALL AVAILABLE DESTINATIONS:")
            sorted_destinations = sorted(available_destinations)
            # Print in rows of 8 for better readability
            for i in range(0, len(sorted_destinations), 8):
                row = sorted_destinations[i:i+8]
                dest_with_names = [f"{code}({self.airport_names.get(code, code)[:3]})" for code in row]
                print(f"   {' | '.join(dest_with_names)}")
        else:
            print("❌ No GoWild flights found to any domestic destination")

def main():
    parser = argparse.ArgumentParser(description='Check specific routes for Frontier GoWild flights')
    parser.add_argument('-o', '--origin', required=True, help='Origin airport code (e.g., LGA)')
    parser.add_argument('-d', '--destinations', nargs='+', help='Destination airport codes (e.g., SJC SFO DEN)')
    parser.add_argument('--days', type=int, default=1, help='Days from today (default: 1 = tomorrow)')
    parser.add_argument('--both', action='store_true', help='Check both today and tomorrow')
    parser.add_argument('--all-domestic', action='store_true', help='Check all domestic US destinations from origin (discovers all GoWild options)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.all_domestic and not args.destinations:
        parser.error("Either --destinations or --all-domestic must be specified")
    
    # Create checker
    checker = SimpleGoWildChecker()
    
    if args.all_domestic:
        # Domestic discovery mode
        if args.both:
            # Discovery mode for both days
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            
            print("🔍🔍 DOMESTIC DISCOVERY FOR BOTH TODAY AND TOMORROW 🔍🔍")
            print("=" * 80)
            
            print("\n🌅 TODAY'S DOMESTIC DISCOVERY:")
            print("=" * 50)
            checker.discover_all_domestic(args.origin.upper(), today)
            
            print("\n" + "=" * 80)
            
            print("\n🌄 TOMORROW'S DOMESTIC DISCOVERY:")
            print("=" * 50)
            checker.discover_all_domestic(args.origin.upper(), tomorrow)
        else:
            # Single day domestic discovery
            flight_date = datetime.now() + timedelta(days=args.days)
            checker.discover_all_domestic(args.origin.upper(), flight_date)
    elif args.both:
        # Check both today and tomorrow for specific destinations
        checker.check_both_days(args.origin.upper(), args.destinations)
    else:
        # Check single date for specific destinations
        flight_date = datetime.now() + timedelta(days=args.days)
    checker.check_multiple_routes(args.origin.upper(), args.destinations, flight_date)

if __name__ == "__main__":
    main()