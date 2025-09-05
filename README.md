# GoWild Flight Finder ✈️

A beautiful, feature-rich web application to find Frontier GoWild flight deals with advanced filtering, sorting, and date range selection capabilities.

![GoWild Flight Finder](https://img.shields.io/badge/Status-Live-brightgreen) ![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Flask](https://img.shields.io/badge/Flask-2.3.3-red)

## 🌟 Features

### ✨ Core Functionality
- **🔍 Smart Flight Search** - Find GoWild deals from any US domestic airport
- **📅 Flexible Date Selection** - Single date or date range picker with calendar UI
- **🎯 Two Search Modes**:
  - **Specific Destinations**: Choose exact airports you want to visit
  - **Discover All**: Find all available GoWild flights from your origin

### 🎛️ Advanced Filters & Sorting
- **💰 Price Range Filter** - Set min/max budget (e.g., $50-$200)
- **⏱️ Duration Filter** - Maximum flight duration in hours
- **✈️ Stops Filter** - Non-stop only, 1 stop max, or 2 stops max
- **🔎 Destination Search** - Type to filter by city/airport name
- **📊 Smart Sorting**:
  - Price (Low to High / High to Low)
  - Duration (Short to Long)
  - Departure Time
  - Destination (Alphabetical)

### 🎨 User Experience
- **🔍 Searchable Dropdowns** - Type to find airports instantly
- **🏷️ Full Airport Names** - Display format: "SFO (San Francisco, CA) → ATL (Atlanta, GA)"
- **📱 Mobile Responsive** - Works perfectly on all devices
- **⚡ Real-time Filtering** - Results update instantly as you change filters
- **📈 Live Statistics** - Total flights, destinations, lowest/average prices

## 🚀 Live Demo

**Local Development**: `http://localhost:8000`

## 🛠️ Tech Stack

- **Backend**: Python 3.9+ with Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **UI Framework**: Bootstrap 5
- **Components**: 
  - Select2 (searchable dropdowns)
  - Flatpickr (date range picker)
  - Font Awesome (icons)
- **Web Scraping**: BeautifulSoup4, Requests
- **Deployment**: Vercel-ready

## 📦 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- pip package manager

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/bibek-panthi/gowild.git
cd gowild
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python3 app.py
# OR use the convenient start script
python3 start.py
```

4. **Open in browser**
```
http://localhost:8000
```

## 🌐 Deployment

### Vercel Deployment (Recommended)

1. **Fork/Clone this repository to your GitHub**
2. **Connect to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - Vercel will automatically detect the configuration
3. **Deploy**: Vercel handles the rest!

### Manual Deployment
The app includes `vercel.json` configuration and is ready for deployment on any Python-supporting platform.

## 📖 Usage Guide

### Basic Search
1. **Select Origin Airport** - Type to search (e.g., "San Francisco" or "SFO")
2. **Choose Travel Dates** - Click calendar for date range selection
3. **Pick Search Mode**:
   - **Specific**: Select destination airports
   - **Discover**: Find all available destinations
4. **Search**: Click "Find GoWild Flights"

### Advanced Filtering
1. **Click "Show Filters"** after getting results
2. **Set Price Range** - Min/max budget
3. **Filter by Duration** - Maximum flight time
4. **Choose Stops** - Non-stop, 1 stop, or 2 stops max
5. **Search Destinations** - Type city/airport names
6. **Sort Results** - By price, duration, time, or destination
7. **Apply Filters** - Results update in real-time

### Example Searches
```
Origin: SFO (San Francisco)
Dates: Dec 10-15, 2024
Mode: Discover All
→ Shows all domestic GoWild flights from SFO

Origin: LGA (LaGuardia)  
Destinations: ATL, MIA, DEN
Date: Dec 20, 2024
Filters: $50-$150, Non-stop only
→ Shows filtered specific routes
```

## 🏗️ Project Structure

```
gowild/
├── app.py                 # Main Flask application
├── gowild_finder.py       # Core flight finder logic (CLI version)
├── gowild_finder_commented.py  # Commented version for learning
├── start.py               # Convenient startup script
├── templates/
│   └── index.html         # Main web interface
├── requirements.txt       # Python dependencies
├── vercel.json           # Vercel deployment config
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔧 API Endpoints

### `GET /`
- **Description**: Main web interface
- **Returns**: HTML page with flight search form

### `POST /api/search`
- **Description**: Search for flights
- **Body**:
```json
{
  "origin": "SFO",
  "startDate": "2024-12-10",
  "endDate": "2024-12-12",
  "searchType": "all_domestic",
  "destinations": ["ATL", "MIA"]
}
```
- **Returns**: JSON with flight results, stats, and metadata

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Commit: `git commit -m 'Add amazing feature'`
5. Push: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- **Frontier Airlines** for the GoWild pass program
- **Bootstrap** for the beautiful UI framework
- **Select2** for enhanced dropdown functionality
- **Flatpickr** for the elegant date picker

## ⚠️ Disclaimer

This tool is for personal use only. Please be respectful to Frontier Airlines' servers and use reasonable delays between requests. The tool includes built-in rate limiting and politeness measures.

---

**Built with ❤️ by [Bibek Panthi](https://github.com/bibek-panthi)**

*Happy flight hunting! ✈️*
