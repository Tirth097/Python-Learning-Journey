# EuroBank Customer Segmentation & Churn Analytics Dashboard

## Overview

The EuroBank Customer Segmentation & Churn Analytics Dashboard is an interactive business intelligence application developed using Python and Streamlit. It provides comprehensive insights into customer behavior, churn trends, demographic distribution, and high-value customer risk using a European banking dataset.

The dashboard enables business users and analysts to explore customer segments, identify churn patterns, evaluate geographical performance, and generate actionable recommendations through an intuitive and responsive interface.

---

## Features

### Dashboard Overview
- Customer churn KPIs
- Customer retention statistics
- Average balance analysis
- Credit score analysis
- Salary insights
- Active member percentage
- Interactive KPI cards

### Geography Analysis
- European choropleth map
- Country-wise churn comparison
- Customer distribution
- Churn analysis by geography

### Age & Tenure Analysis
- Churn by age groups
- Churn by tenure
- Customer demographic analysis
- Customer distribution visualizations

### High Value Explorer
- High-value customer identification
- Revenue at risk analysis
- Premium customer segmentation
- High-value churn monitoring

### Customer Segmentation
- Customer segmentation based on financial and demographic attributes
- Credit score analysis
- Product ownership analysis
- Activity status analysis

### Customer Table
- Interactive customer records
- Advanced filtering
- Search functionality
- CSV export

### Insights & Recommendations
- Automated business insights
- Customer retention recommendations
- Churn risk analysis
- Strategic business recommendations

---

## Technologies Used

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Matplotlib
- HTML
- CSS

---

## Project Structure

```text
Dashboard/
│
├── app.py
├── data/
│   └── European_Bank.csv
│
├── pages/
│   ├── 0_Overview.py
│   ├── 1_Geography.py
│   ├── 2_Age_and_Tenure.py
│   ├── 3_High_Value_Explorer.py
│   ├── 4_Customer_Segmentation.py
│   ├── 5_Customer_Table.py
│   └── 6_Insights_Recommendations.py
│
├── utils/
│   ├── data_loader.py
│   └── styling.py
│
├── images/
├── requirements.txt
└── README.md
```

---

## Dataset

The dashboard utilizes a European banking customer dataset containing information such as:

- Customer ID
- Geography
- Gender
- Age
- Credit Score
- Balance
- Estimated Salary
- Tenure
- Number of Products
- Credit Card Ownership
- Active Member Status
- Customer Churn Status

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/your-repository.git
```

### Navigate to the Project Directory

```bash
cd Dashboard
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
streamlit run app.py
```

---

## Dashboard Modules

- Overview
- Geography Analysis
- Age & Tenure Analysis
- High Value Explorer
- Customer Segmentation
- Customer Table
- Insights & Recommendations

---

## Key Capabilities

- Interactive customer churn analysis
- Customer segmentation
- Geographic performance analysis
- Revenue risk identification
- Dynamic dashboard filtering
- Business insight generation
- CSV export
- Responsive dashboard interface

---

## Business Value

The dashboard supports data-driven decision making by helping organizations:

- Identify customers with a high likelihood of churn.
- Analyze churn across different countries and customer segments.
- Monitor high-value customers and potential revenue loss.
- Develop targeted customer retention strategies.
- Generate meaningful business insights through interactive visualizations.

---

## Future Enhancements

- Machine Learning-based churn prediction
- Customer Lifetime Value (CLV) estimation
- Real-time database integration
- PDF report generation
- User authentication
- Predictive analytics and forecasting

---

## License

This project is developed for educational, research, and portfolio purposes.

---

## Author

**Tirth Maheshwari**

B.Tech Computer Science Engineering (AI & Edge Computing)  
MIT ADT University, Pune

Data Analytics Intern  
Unified Mentor Pvt. Ltd.
