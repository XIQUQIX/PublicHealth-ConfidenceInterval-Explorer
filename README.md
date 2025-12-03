# BRFSS Interactive Dashboard

An interactive web-based dashboard for exploring CDC's Behavioral Risk Factor Surveillance System (BRFSS) data. Built with Python Dash and Plotly, this application enables dynamic analysis of public health trends across demographics, geography, and time.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Dash](https://img.shields.io/badge/dash-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎯 Features

- **Multi-level Filtering**: Hierarchical navigation through Class → Topic → Question
- **7 Analytical Dimensions**: 
  - Overall statistics
  - Gender breakdown
  - Age groups (with adjustable granularity)
  - Education levels
  - Income brackets
  - Geographic distribution (US map)
  - Temporal trends
- **Statistical Rigor**: Confidence intervals recalculated from raw sample data
- **Interactive Visualizations**: Grouped bar charts with error bars and choropleth maps
- **Responsive Design**: Clean, user-friendly interface

## 📊 Dataset

The dashboard uses aggregated BRFSS survey data stored in Parquet format for optimal performance:
- **Size**: 2.7M+ records
- **Time span**: Multiple years of survey data
- **Geographic coverage**: All US states and territories
- **Variables**: Demographics, health conditions, risk behaviors

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/brfss-dashboard.git
cd brfss-dashboard
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Prepare your data:
   - Place your `cleaned.parquet` file in the project directory
   - Update `DATA_PATH` in the script to point to your data file

4. Run the application:
```bash
python dashboard_app.py
```

5. Open your browser and navigate to:
```
http://127.0.0.1:8050/
```

## 📦 Dependencies

```txt
pandas>=1.3.0
numpy>=1.21.0
dash>=2.0.0
plotly>=5.0.0
```

Create a `requirements.txt` file with:
```bash
pandas
numpy
dash
plotly
pyarrow  # Required for Parquet support
```

## 📁 Project Structure

```
brfss-dashboard/
│
├── dashboard_app.py          # Main application file
├── cleaned.parquet           # Data file (not included)
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎨 Dashboard Components

### 1. Overall Panel
Displays response distribution for the selected question across all participants.

### 2. By Gender
Compares responses between male and female participants with confidence intervals.

### 3. By Age
Shows age-based trends with two viewing modes:
- **More**: 7 detailed age groups (18-24, 25-34, 35-44, 45-54, 55-64, 65-74, 75+)
- **Less**: 3 broad categories (18-34, 35-64, 65+)

### 4. By Education
Analyzes responses across four education levels from less than high school to college graduate.

### 5. By Income
Breaks down responses by household income brackets.

### 6. By Location (Map)
Interactive US choropleth map showing state-level variations for "Yes" responses.

### 7. By Year (Temporal)
Tracks changes over time for longitudinal trend analysis.

## 🔧 Technical Highlights

### Confidence Interval Recalculation
The dashboard doesn't simply average existing percentages. Instead, it:
1. Aggregates raw sample sizes and person counts
2. Recalculates proportions from aggregated data
3. Computes new 95% confidence intervals using standard error formula

```python
se = sqrt(p * (1-p) / n)
CI = p ± 1.96 * se
```

This ensures statistical validity when filtering or grouping data.

### Data Format
- **Parquet**: Used for fast loading and efficient storage (10x faster than CSV)
- **Type Safety**: All numeric columns validated and cast to appropriate types
- **Missing Data**: Handled gracefully with informative "no data" messages

## 🎓 Use Cases

- **Public Health Research**: Identify health disparities across demographics
- **Policy Analysis**: Compare state-level health outcomes
- **Trend Analysis**: Track changes in health behaviors over time
- **Educational Tool**: Teach data visualization and public health concepts

## 🛠️ Configuration

### Changing the Data Source
Edit line 12 in `dashboard_app.py`:
```python
DATA_PATH = r"path/to/your/cleaned.parquet"
```

### Changing the Port
Modify the last line:
```python
if __name__ == "__main__":
    app.run(debug=True, port=8080)  # Change port here
```

### Customizing Age Groups
Modify the `make_age_panel()` function to adjust age group boundaries.

## 📝 Data Requirements

Your Parquet file must contain these columns:
- `Year`: Survey year
- `Locationabbr`: State/territory abbreviation
- `Class`: High-level category
- `Topic`: Specific health topic
- `Question`: Survey question text
- `Response`: Answer option (e.g., "Yes", "No")
- `Break_Out`: Specific demographic value (e.g., "Male", "18-24")
- `Break_Out_Category`: Demographic type (e.g., "Sex", "Age Group")
- `Sample_Size`: Number of respondents
- `Data_value`: Percentage value
- `Confidence_limit_Low`: Lower CI bound
- `Confidence_limit_High`: Upper CI bound
- `proportion`: Decimal proportion
- `persons`: Number of people with this response

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- **Your Name** - *Initial work* - [YourGitHub](https://github.com/yourusername)

## 🙏 Acknowledgments

- CDC BRFSS for providing the public health survey data
- Plotly Dash community for excellent documentation
- DS5110 course for project guidance

## 📧 Contact

For questions or feedback, please open an issue on GitHub or contact [your.email@example.com]

## 🔗 Links

- [CDC BRFSS Official Site](https://www.cdc.gov/brfss/)
- [Dash Documentation](https://dash.plotly.com/)
- [Plotly Python](https://plotly.com/python/)

---

**Note**: This dashboard is for educational and research purposes. Always verify findings with official CDC reports for policy decisions.
