# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 16:48:31 2025

@author: mt503

Production Sustainability Data Analysis Project
"""

# 1.2 Creating Sample Data Generator #

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Creating Sample data for production & fuel consumption #
def generate_sample_data():
    productions = [
        {'production_name': 'Sunset Boulevard Revival', 'production_type': 'Film', 'location': 'Los Angeles, CA'},
        {'production_name': 'Tech Titans S3', 'production_type': 'TV Series', 'location': 'Atlanta, GA'},
        {'production_name': 'Ocean Depths', 'production_type': 'Documentary', 'location': 'Miami, FL'}
    ]
    
    # Generate fuel consumption with intentional data quality issues
    fuel_data = []
    for prod_id in range(1, 4):
        for day in range(30):
            date = datetime.now() - timedelta(days=day)
            
            # Adding some data quality issues intentionally
            gallons = round(random.uniform(10, 500), 2)
            if random.random() < 0.05:  # 5% chance of outlier
                gallons = gallons * 10  # obvious error
                
            fuel_data.append({
                'production_id': prod_id,
                'date_recorded': date.date(),
                'equipment_type': random.choice(['Generator', 'Vehicle', 'Lighting Truck']),
                'fuel_type': random.choice(['Diesel', 'Gasoline']),
                'gallons_consumed': gallons,
                'hours_operated': round(random.uniform(2, 16), 1)
            })
    
    return productions, fuel_data
    
# 2.1 Data Validation Functions
    
import logging
    
# 'Data Detective Class' - This will spot problems automatically
class DataQualityController:
    def __init__(self, db_connection):
        self.db = db_connection  # Connection to database
        self.quality_rules = {  # Defining what 'Normal' looks like
            'fuel_consumption': {
                'gallons_consumed': {'min': 0, 'max': 1000},
                'hours_operated': {'min': 0, 'max': 24}
            }
        }
    
    def validate_fuel_data(self, df):
        """Run comprehensive data quality checks"""
        issues = []
        
        # Check for outliers
        for column in ['gallons_consumed', 'hours_operated']:
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
            for idx, row in outliers.iterrows():
                issues.append({
                    'record_id': row.get('record_id'),
                    'issue_type': f'{column}_outlier',
                    'issue_description': f'{column} value {row[column]} is outside normal range',
                    'severity': 'Medium'
                })
        
        # Check for missing critical data
        critical_fields = ['production_id', 'date_recorded', 'gallons_consumed']
        for field in critical_fields:
            missing = df[df[field].isnull()]
            if not missing.empty:
                issues.append({
                    'issue_type': 'missing_data',
                    'issue_description': f'Missing {field} in {len(missing)} records',
                    'severity': 'High'
                })
        
        return issues
    
    def log_quality_issues(self, issues):
        """Log issues to database"""
        for issue in issues:
            print(f"LOGGED: {issue['severity']} - {issue['issue_description']}")
        
# 2.2 Automated Data Pipeline

import sqlalchemy
from datetime import datetime

class SustainabilityPipeline:
    def __init__(self, db_url):
        self.engine = sqlalchemy.create_engine(db_url) if db_url else None
        self.quality_controller = DataQualityController(self.engine)
    
    def daily_data_refresh(self):
        """Main pipeline function - run daily"""
        try:
            # Extract New Data
            raw_data = self.extract_daily_data()
            
            # Validate data quality
            issues = self.quality_controller.validate_fuel_data(raw_data)
            
            if issues:
                self.quality_controller.log_quality_issues(issues)
                print(f'⚠️ Found {len(issues)} data quality issues')
                
            # Calculate sustainability metrics
            metrics = self.calculate_sustainability_metrics(raw_data)
            
            # Load to database
            self.load_metrics(metrics)
            
            print("✅ Daily pipeline completed successfully")
        
        except Exception as e:
            print(f"❌ Pipeline failed: {str(e)}")
    
    def calculate_sustainability_metrics(self, df):
        """Calculate carbon footprint and cost metrics"""
        # Carbon emission factors (kg CO2 per gallon)
        emission_factors = {
            'Diesel': 10.15,
            'Gasoline': 8.89
        }
        
        df['carbon_emissions_kg'] = df.apply(
            lambda row: row['gallons_consumed'] * emission_factors.get(row['fuel_type'], 0),
            axis=1
        )
        
        # Calculate Costs (Mock Pricing)
        fuel_costs = {'Diesel': 3.50, 'Gasoline': 3.25}
        df['fuel_cost_usd'] = df.apply(
            lambda row: row['gallons_consumed'] * fuel_costs.get(row['fuel_type'], 0),
            axis=1
        )
        
        return df
    
    def extract_daily_data(self):
        """Extract new data - placeholder for actual implementation"""
        return pd.DataFrame()
    
    def load_metrics(self, metrics):
        """Load metrics to database - placeholder for actual implementation"""
        pass

# 3.1 Streamlit Dashboard
    
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

def main():
    st.title('🌱 Production Sustainability Dashboard')
    st.sidebar.title('Navigation')
    
    page = st.sidebar.selectbox("Choose a page", [
        "Overview", 
        "Data Quality Control", 
        "Carbon Footprint Analysis",
        "Cost Analysis",
        "Training Materials"
    ])
    
    if page == 'Overview':
        show_overview()
    elif page == 'Data Quality Control':
        show_data_quality()
    elif page == 'Carbon Footprint Analysis':
        show_carbon_analysis()
    elif page == 'Cost Analysis':
        show_cost_analysis()
    elif page == 'Training Materials':
        show_training_materials()

def show_overview():
    st.header('Production Sustainability Overview')
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Productions", "12", "2")
    with col2:
        st.metric("Carbon Saved (kg)", "15,420", "1,200")
    with col3:
        st.metric("Cost Savings ($)", "$23,580", "$2,100")
    with col4:
        st.metric("Data Quality Score", "94%", "2%")

    # Sample data for demo
    df = generate_sample_dashboard_data()

    # Timeline chart
    fig = px.line(df, x='date', y='daily_emissions', 
              color='production_name',
              title='Daily Carbon Emissions by Production')
    st.plotly_chart(fig, use_container_width=True)

def show_data_quality():
    st.header("📊 Data Quality Control Center")

    # Data quality metrics
    st.subheader("Quality Score Breakdown")
    quality_data = pd.DataFrame({
        'Metric': ['Completeness', 'Accuracy', 'Consistency', 'Timeliness'],
        'Score': [96, 94, 98, 92],
        'Target': [95, 95, 95, 95]
    })

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Current Score', x=quality_data['Metric'], y=quality_data['Score']))
    fig.add_trace(go.Bar(name='Target', x=quality_data['Metric'], y=quality_data['Target']))
    st.plotly_chart(fig, use_container_width=True)

    # Recent issues
    st.subheader("Recent Data Quality Issues")
    issues_df = pd.DataFrame({
        'Date': ['2025-06-01', '2025-05-31', '2025-05-30'],
        'Production': ['Sunset Boulevard', 'Tech Titans S3', 'Ocean Depths'],
        'Issue Type': ['Fuel Outlier', 'Missing Data', 'Duplicate Entry'],
        'Severity': ['Medium', 'High', 'Low'],
        'Status': ['Resolved', 'Pending', 'Resolved']
    })
    st.dataframe(issues_df, use_container_width=True)

def show_carbon_analysis():
    st.header("🌍 Carbon Footprint Analysis")
    
    # Generate sample carbon data
    carbon_data = generate_carbon_data()
    
    # Emissions breakdown by fuel type
    fuel_summary = carbon_data.groupby('fuel_type')['carbon_emissions'].sum().reset_index()
    
    fig = px.pie(fuel_summary, values='carbon_emissions', names='fuel_type',
                 title='Carbon Emissions by Fuel Type')
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly trends
    monthly_emissions = carbon_data.groupby(['month', 'production_name'])['carbon_emissions'].sum().reset_index()
    
    fig = px.bar(monthly_emissions, x='month', y='carbon_emissions', 
                 color='production_name', title='Monthly Carbon Emissions by Production')
    st.plotly_chart(fig, use_container_width=True)

def show_cost_analysis():
    st.header("💰 Cost Analysis")
    
    cost_data = pd.DataFrame({
        'Month': ['Jan 2025', 'Feb 2025', 'Mar 2025', 'Apr 2025', 'May 2025'],
        'Fuel Costs': [15420, 16780, 14230, 13560, 12890],
        'Target Costs': [14000, 14000, 14000, 14000, 14000]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=cost_data['Month'], y=cost_data['Fuel Costs'],
                             mode='lines+markers', name='Actual Costs'))
    fig.add_trace(go.Scatter(x=cost_data['Month'], y=cost_data['Target Costs'],
                             mode='lines', name='Target Costs'))
    st.plotly_chart(fig, use_container_width=True)

def show_training_materials():
    st.header("📚 Training Materials")

    st.subheader("Data Entry Guidelines")
    st.markdown("""
    ### Fuel Consumption Reporting
    1. **Daily Reporting**: Submit fuel data within 24 hours of consumption
    2. **Required Fields**: Production ID, Date, Equipment Type, Fuel Type, Gallons
    3. **Quality Checks**: Values outside normal ranges will be flagged for review

    ### Common Data Entry Errors
    - **Decimal Places**: Use 2 decimal places for gallons (e.g., 15.75, not 15.753)
    - **Date Format**: Use YYYY-MM-DD format
    - **Equipment Types**: Use standardized categories only

    ### Validation Process
    - Data is automatically validated upon submission
    - Outliers are flagged but not rejected
    - Missing critical fields prevent submission
    """)

    # Interactive training quiz
    st.subheader("Quick Knowledge Check")
    question = st.radio(
        "What should you do if fuel consumption seems unusually high?",
        ["Submit anyway", "Double-check equipment hours and fuel type", "Skip the entry"]
    )

    if question == "Double-check equipment hours and fuel type":
        st.success("✅ Correct! Always verify unusual values before submission.")

def generate_sample_dashboard_data():
    """Generate sample data for dashboard"""
    dates = [datetime.now() - timedelta(days=x) for x in range(30)]
    dates.reverse()
    
    data = []
    productions = ['Sunset Boulevard', 'Tech Titans S3', 'Ocean Depths']
    
    for date in dates:
        for production in productions:
            base_emission = {'Sunset Boulevard': 150, 'Tech Titans S3': 200, 'Ocean Depths': 100}
            daily_emission = base_emission[production] + np.random.normal(0, 20)
            
            data.append({
                'date': date.date(),
                'production_name': production,
                'daily_emissions': max(0, daily_emission)
            })
    
    return pd.DataFrame(data)

def generate_carbon_data():
    """Generate sample carbon emissions data"""
    data = []
    productions = ['Sunset Boulevard', 'Tech Titans S3', 'Ocean Depths']
    fuel_types = ['Diesel', 'Gasoline']
    months = ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05']
    
    for month in months:
        for production in productions:
            for fuel_type in fuel_types:
                emissions = np.random.uniform(1000, 5000)
                data.append({
                    'month': month,
                    'production_name': production,
                    'fuel_type': fuel_type,
                    'carbon_emissions': emissions
                })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    main()