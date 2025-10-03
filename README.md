# 🏏 IPL Reference  

A modern web app for exploring **Indian Premier League (IPL)** cricket statistics, featuring detailed player and team analytics. Built with **FastAPI + React**, powered by data from [CricSheets](https://cricsheet.org/).  

🔗 **Live Demo**: [Vercel Frontend](https://ipl-reference.vercel.app)

---

## Features  

- **Smart Player Search** – Instant autocomplete with player names + career span  
- **Detailed Statistics** – Season-by-season & career-wide batting/bowling stats  
- **Team Analysis** – Explore team rosters year by year  
- **Interactive Tables** – Sort stats by runs, wickets, averages, strike rate, etc.  
- **Clean UI** – Responsive, modern design  

---

## Tech Stack  

- **Frontend**: HTML5, CSS3, JavaScript, React (via Babel), deployed on **Vercel**  
- **Backend**: Python, FastAPI, Uvicorn, deployed on **Render**  
- **Data Processing**: Pandas, JSON (CricSheets datasets)  

---

## Project Structure  

```
IPL Reference/
├── api/ # FastAPI backend
├── player_data/ # Processed CSV data
├── ipl_data/ # Raw JSON match data (CricSheets)
├── index.html # Home page
├── player.html # Player profile page
├── players.html # Player directory
├── teams.html # Team players page
├── parse_and_aggregate.py # Raw JSON → CSV processing
└── career_stats.py # Career stats aggregation
```

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ipl-reference.git
   cd ipl-reference
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the backend server**
   ```bash
   python api/run_server.py
   ```

4. **Open the frontend**
   ```bash
   python -m http.server 3000
   ```
   - Then visit `http://localhost:3000`

## API Endpoints

- `GET /players` - Get all players
- `GET /player/{name}/batting` - Get player batting statistics
- `GET /player/{name}/bowling` - Get player bowling statistics
- `GET /player/{name}/career` - Get player career summary

## Key Features

### Player Search & Profiles
- Autocomplete search with player names and years
- Comprehensive batting and bowling statistics
- Career totals and averages
- Team history and season breakdown

### Team Analysis
- Browse players by team selection
- Year-by-year team rosters

### Data Visualization
- Clean, responsive grid layouts
- Easy access to both season and career statistics

