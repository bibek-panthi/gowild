#!/usr/bin/env python3
"""
GoWild Flight Finder Web Application
Beautiful web interface for finding Frontier GoWild flights
"""

from flask import Flask, render_template, request, jsonify
import sys
import os
from datetime import datetime, timedelta
import json

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the working flight finder logic
from gowild_finder import SimpleGoWildChecker

app = Flask(__name__)

# Create the checker instance
checker = SimpleGoWildChecker()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', airports=checker.airport_names)

@app.route('/api/search', methods=['POST'])
def search_flights():
    """Search for flights API endpoint"""
    try:
        data = request.json
        origin = data.get('origin', '').upper()
        destinations = data.get('destinations', [])
        start_date_str = data.get('startDate')
        end_date_str = data.get('endDate', start_date_str)
        search_type = data.get('searchType', 'specific')
        
        print(f"Search request: {origin}, {start_date_str} to {end_date_str}, type: {search_type}")
        
        # Parse dates
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Generate list of dates to search
        search_dates = []
        current_date = start_date
        while current_date <= end_date:
            search_dates.append(current_date)
            current_date += timedelta(days=1)
        
        all_results = []
        
        if search_type == 'all_domestic':
            print(f"Discovery mode: searching from {origin}")
            # Discovery mode - use the working discover_all_domestic method
            for search_date in search_dates:
                try:
                    print(f"Discovering flights for {search_date.strftime('%Y-%m-%d')}")
                    
                    # Create a custom discovery that's faster for web use
                    destinations_to_check = [airport for airport in checker.domestic_airports[:20] if airport != origin]  # Limit to first 20 for web performance
                    
                    for dest in destinations_to_check:
                        flights = checker.check_flight(origin, dest, search_date, quiet_mode=True)
                        
                        if flights:
                            # Enhance flight data
                            enhanced_flights = []
                            for flight in flights:
                                enhanced_flight = flight.copy()
                                enhanced_flight['departure_airport_name'] = checker.airport_names.get(flight.get('departure_airport', ''), '')
                                enhanced_flight['arrival_airport_name'] = checker.airport_names.get(flight.get('arrival_airport', ''), '')
                                enhanced_flight['search_date'] = search_date.strftime('%Y-%m-%d')
                                enhanced_flights.append(enhanced_flight)
                            
                            all_results.append({
                                'destination': dest,
                                'destination_name': checker.airport_names.get(dest, dest),
                                'flights': enhanced_flights,
                                'search_date': search_date.strftime('%Y-%m-%d')
                            })
                        
                except Exception as e:
                    print(f"Error in discovery for {search_date}: {e}")
                    continue
        else:
            print(f"Specific mode: searching {origin} to {destinations}")
            # Specific destinations
            for search_date in search_dates:
                for dest in destinations:
                    dest = dest.upper()
                    if dest == origin:
                        continue
                    
                    try:
                        # Use the working check_flight method
                        flights = checker.check_flight(origin, dest, search_date, quiet_mode=True)
                        
                        if flights:
                            # Enhance flight data
                            enhanced_flights = []
                            for flight in flights:
                                enhanced_flight = flight.copy()
                                enhanced_flight['departure_airport_name'] = checker.airport_names.get(flight.get('departure_airport', ''), '')
                                enhanced_flight['arrival_airport_name'] = checker.airport_names.get(flight.get('arrival_airport', ''), '')
                                enhanced_flight['search_date'] = search_date.strftime('%Y-%m-%d')
                                enhanced_flights.append(enhanced_flight)
                            
                            all_results.append({
                                'destination': dest,
                                'destination_name': checker.airport_names.get(dest, dest),
                                'flights': enhanced_flights,
                                'search_date': search_date.strftime('%Y-%m-%d')
                            })
                    except Exception as e:
                        print(f"Error checking {origin} to {dest} on {search_date}: {e}")
                        continue
        
        # Group results by destination to avoid duplication
        grouped_results = {}
        for result in all_results:
            key = result['destination']
            if key not in grouped_results:
                grouped_results[key] = {
                    'destination': result['destination'],
                    'destination_name': result['destination_name'],
                    'flights': []
                }
            grouped_results[key]['flights'].extend(result['flights'])
        
        final_results = list(grouped_results.values())
        
        print(f"Found {len(final_results)} destinations with flights")
        
        # Format date range for response
        if start_date == end_date:
            date_display = start_date.strftime('%A, %B %d, %Y')
        else:
            date_display = f"{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}"
        
        return jsonify({
            'success': True,
            'results': final_results,
            'origin': origin,
            'origin_name': checker.airport_names.get(origin, origin),
            'startDate': start_date_str,
            'endDate': end_date_str,
            'date': date_display
        })
        
    except Exception as e:
        print(f"API Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
