#!/usr/bin/env python3
"""
GoWild Flight Finder Web Application
Beautiful web interface for finding Frontier GoWild flights
"""

from flask import Flask, render_template, request, jsonify
import json
import requests
import html
import random
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor
import threading

app = Flask(__name__)

class GoWildAPI:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        })
        
        # Airport data
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
            'MYR': 'Myrtle Beach, SC', 'TTN': 'Trenton, NJ', 'EWR': 'Newark, NJ',
            
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
        }

    def check_flight(self, origin, destination, date):
        """Check a single route for GoWild flights"""
        try:
            # Format date for URL
            date_str = date.strftime("%b-%d,-%Y").replace("-", "%20")
            
            # Build URL
            url = f"https://booking.flyfrontier.com/Flight/InternalSelect?o1={origin}&d1={destination}&dd1={date_str}&ADT=1&mon=true&promo="
            
            # Add delay to be respectful
            time.sleep(random.uniform(1, 2))
            
            # Make request
            response = self.session.get(url, timeout=30)
            
            if response.status_code != 200:
                return []
            
            # Extract flight data
            flights = self._extract_gowild_flights(response)
            return flights
            
        except Exception as e:
            print(f"Error checking {origin} to {destination}: {e}")
            return []

    def _extract_gowild_flights(self, response):
        """Extract GoWild flights from response"""
        try:
            soup = BeautifulSoup(response.text, "html.parser")
            scripts = soup.find_all("script", type="text/javascript")
            
            for script in scripts:
                if not script.text or 'journeys' not in script.text:
                    continue
                
                script_content = html.unescape(script.text)
                
                if '{' in script_content:
                    start = script_content.find('{')
                    if start == -1:
                        continue
                    
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
                    
                    # Calculate layover information
                    layovers = []
                    if len(legs) > 1:
                        for i in range(len(legs) - 1):
                            current_leg = legs[i]
                            next_leg = legs[i + 1]
                            layover_airport = current_leg.get('arrivalStation', 'Unknown')
                            arrival_time = current_leg.get('arrivalDateFormatted', '')
                            departure_time = next_leg.get('departureDateFormatted', '')
                            duration = self._calculate_layover_duration(arrival_time, departure_time)
                            layovers.append({
                                'airport': layover_airport,
                                'duration': duration
                            })
                    
                    flight_info = {
                        'stops': flight.get('stopsText', 'Unknown'),
                        'price': flight.get('goWildFare', 0),
                        'departure_time': first_leg.get('departureDateFormatted', 'Unknown'),
                        'departure_airport': first_leg.get('departureStation', 'Unknown'),
                        'arrival_time': last_leg.get('arrivalDateFormatted', 'Unknown'),
                        'arrival_airport': last_leg.get('arrivalStation', 'Unknown'),
                        'duration': flight.get('duration', 'Unknown'),
                        'seats': flight.get('goWildFareSeatsRemaining'),
                        'layovers': layovers,
                        'flight_number': first_leg.get('flightNumber', 'Unknown')
                    }
                    flights.append(flight_info)
            
        except (KeyError, IndexError, TypeError) as e:
            pass
        
        return flights

    def _calculate_layover_duration(self, arrival_time_str, departure_time_str):
        """Calculate layover duration between two time strings"""
        try:
            import re
            
            def parse_time(time_str):
                time_str = time_str.strip()
                match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str)
                if match:
                    hour, minute, ampm = match.groups()
                    hour = int(hour)
                    minute = int(minute)
                    
                    if ampm == 'PM' and hour != 12:
                        hour += 12
                    elif ampm == 'AM' and hour == 12:
                        hour = 0
                        
                    return hour * 60 + minute
                return None
            
            arrival_minutes = parse_time(arrival_time_str)
            departure_minutes = parse_time(departure_time_str)
            
            if arrival_minutes is not None and departure_minutes is not None:
                if departure_minutes < arrival_minutes:
                    departure_minutes += 24 * 60
                
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
        except:
            return "Unknown"

# Create API instance
api = GoWildAPI()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', airports=api.airport_names)

@app.route('/api/search', methods=['POST'])
def search_flights():
    """Search for flights API endpoint"""
    try:
        data = request.json
        origin = data.get('origin', '').upper()
        destinations = data.get('destinations', [])
        date_str = data.get('date')
        search_type = data.get('searchType', 'specific')
        
        # Parse date
        flight_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        results = []
        
        if search_type == 'all_domestic':
            # Discovery mode - search all domestic airports
            destinations_to_check = [airport for airport in api.domestic_airports if airport != origin]
            
            # Use threading for faster searches (but still respectful)
            def check_destination(dest):
                flights = api.check_flight(origin, dest, flight_date)
                if flights:
                    # Use the ACTUAL destination from flight data, not the requested one
                    actual_dest = flights[0].get('arrival_airport', dest) if flights else dest
                    return {
                        'destination': actual_dest,
                        'destination_name': api.airport_names.get(actual_dest, actual_dest),
                        'flights': flights
                    }
                return None
            
            # Check up to 10 destinations in parallel to speed up discovery
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(check_destination, dest) for dest in destinations_to_check[:20]]  # Limit for demo
                
                # Group flights by actual destination to avoid mixing different airports
                destination_groups = {}
                
                for future in futures:
                    result = future.result()
                    if result:
                        actual_dest = result['destination']
                        if actual_dest not in destination_groups:
                            destination_groups[actual_dest] = {
                                'destination': actual_dest,
                                'destination_name': result['destination_name'],
                                'flights': []
                            }
                        destination_groups[actual_dest]['flights'].extend(result['flights'])
                
                # Remove duplicate flights within each destination group
                for dest_group in destination_groups.values():
                    unique_flights = []
                    seen_flights = set()
                    
                    for flight in dest_group['flights']:
                        # Create a unique identifier for each flight
                        flight_id = (
                            flight.get('flight_number', ''),
                            flight.get('departure_time', ''),
                            flight.get('arrival_time', ''),
                            flight.get('departure_airport', ''),
                            flight.get('arrival_airport', ''),
                            flight.get('price', 0)
                        )
                        
                        if flight_id not in seen_flights:
                            seen_flights.add(flight_id)
                            unique_flights.append(flight)
                    
                    dest_group['flights'] = unique_flights
                
                # Convert grouped results back to list
                results = list(destination_groups.values())
        else:
            # Specific destinations
            for dest in destinations:
                dest = dest.upper()
                if dest == origin:
                    continue
                     
                flights = api.check_flight(origin, dest, flight_date)
                if flights:
                    # Remove duplicates for specific searches too
                    unique_flights = []
                    seen_flights = set()
                    
                    for flight in flights:
                        flight_id = (
                            flight.get('flight_number', ''),
                            flight.get('departure_time', ''),
                            flight.get('arrival_time', ''),
                            flight.get('departure_airport', ''),
                            flight.get('arrival_airport', ''),
                            flight.get('price', 0)
                        )
                        
                        if flight_id not in seen_flights:
                            seen_flights.add(flight_id)
                            unique_flights.append(flight)
                    
                    results.append({
                        'destination': dest,
                        'destination_name': api.airport_names.get(dest, dest),
                        'flights': unique_flights
                    })
        
        return jsonify({
            'success': True,
            'results': results,
            'origin': origin,
            'origin_name': api.airport_names.get(origin, origin),
            'date': flight_date.strftime('%A, %B %d, %Y')
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
