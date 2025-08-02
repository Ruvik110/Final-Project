Old Bailey Online Visual Analytics

Tech Stack
- Backend: Flask, Pandas
- Frontend: D3.js, HTML, CSS
- Data: CSV files

Data Files Description
- filled2_final.csv: Base case data
- imprison_filled_correct.csv: Imprisonment-related data
- merged_habitual_sentence.csv: Habitual offender sentencing data
- subset_with_hisco_classified.csv: Social class classification data

Project Structure
vis_app/
├── app.py              # Main Flask application
├── data/               # CSV data files
├── static/             # CSS and JavaScript files
└── templates/          # HTML templates

API
- /api/<key>: Get different datasets
- /api/options: Get filter options
- /api/line_data: Get trend line data
- /api/bar_data: Get bar chart data
- /api/imprison_data: Get imprisonment data
- /api/acts: Get historical acts data
- /api/campaigns: Get campaign data
- /api/transportation: Get transportation data

Usage
1. Select filters from the dropdown menus
2. Toggle historical events checkboxes
3. Explore different time periods and categories
4. Analyze punishment distributions by offence category or social class
