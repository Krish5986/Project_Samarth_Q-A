import os
import pandas as pd
import numpy as np
import streamlit as st

# --- 1. CONFIGURATION AND DATA LOADING ---

DATA_FILE = "Combined_Agri_and_Rainfall.csv"

# Attempt to load the data using the simple filename
try:
    # CRITICAL: This assumes the CSV is in the same directory as app.py
    master_df = pd.read_csv(DATA_FILE)
    
except FileNotFoundError:
    # If the file is not found, display a fatal error message and stop the app.
    st.error(f"FATAL ERROR: Data file '{DATA_FILE}' not found. Please ensure it is in the same folder as app.py")
    st.stop() 

# --- 2. GLOBAL MAPPING AND VARIABLES ---

# Define Query Function for Top crops
crop_category_map = {
    'Rice': 'Cereal', 'Wheat': 'Cereal', 'Maize': 'Cereal', 'Jowar': 'Cereal', 'Bajra': 'Cereal', 
    'Ragi': 'Cereal', 'Barley': 'Cereal', 'Total Foodgrain': 'Aggregate', 'Millets Total': 'Aggregate',
    'Arhar': 'Pulse', 'Moong': 'Pulse', 'Black Gram': 'Pulse', 'Lentil': 'Pulse', 'Gram': 'Pulse', 
    'Peas & Beans': 'Pulse', 'Other Pulses': 'Pulse', 'Pulses Total': 'Aggregate',
    'Groundnut': 'Oilseed', 'Rapeseed & Mustard': 'Oilseed', 'Soyabean': 'Oilseed', 'Sunflower': 'Oilseed', 
    'Oilseeds Total': 'Aggregate', 'Castor Seed': 'Oilseed', 'Sesamum': 'Oilseed', 'Niger Seed': 'Oilseed', 
    'Linseed': 'Oilseed', 'Sugarcane': 'Commercial', 'Cotton': 'Commercial', 'Jute': 'Commercial', 
    'Sannhamp': 'Commercial', 'Potato': 'Vegetable', 'Onion': 'Vegetable', 'Tomato': 'Vegetable', 
    'Cabbage': 'Vegetable', 'Brinjal': 'Vegetable', 'Garlic': 'Vegetable', 'Bhindi': 'Vegetable', 
    'Peas': 'Vegetable', 'Other Vegetables': 'Vegetable', 'Mango': 'Fruit', 'Banana': 'Fruit', 
    'Citrus Fruit': 'Fruit', 'Other Fruits': 'Fruit', 'Papaya': 'Fruit', 'Watermelon': 'Fruit',
    'Turmeric': 'Spice', 'Ginger': 'Spice', 'Chillies': 'Spice', 'Black Pepper': 'Spice', 'Cardamom': 'Spice',
}

# Apply the mapping to create the new 'crop_type' column
master_df['crop_type'] = master_df['crop'].map(crop_category_map)

# Define global lists for UI selection
ALL_STATES = sorted(master_df['state_name'].unique())
ALL_CROP_TYPES = sorted(master_df['crop_type'].dropna().unique())
ALL_CROPS = sorted(master_df['crop'].dropna().unique())
MAX_YEAR_SPAN = master_df['crop_year'].max() - master_df['crop_year'].min()
ALL_SINGLE_CROPS = sorted([c for c in master_df['crop'].unique() if c not in ['Oilseeds Total',' Total Foodgrain', 'Pulses Total']])


# ---------------------------------------------------------------------------------------------------
# --- 3. CORE ANALYTICAL FUNCTIONS ---
# ---------------------------------------------------------------------------------------------------

def compare_recent_avg_rainfall(df,state_list,n_years):
    # Calculates the average annual rainfall for a list of states
    latest_year = df['crop_year'].max()
    start_year = latest_year - n_years + 1
    filtered_df = df[(df['state_name'].isin(state_list)) & (df['crop_year'] >= start_year )].copy()
    state_annual_rainfall = filtered_df.groupby(['state_name','crop_year'])['annual_rainfall_mm'].mean().reset_index()
    avg_rainfall_result = state_annual_rainfall.groupby("state_name")['annual_rainfall_mm'].mean().round(2)
    return avg_rainfall_result.to_dict()

def get_top_m_crops(df,state_list, crop_type , n_years, M):
    # Identifies the top M crops (by production) of a specified crop_type
    latest_year = df['crop_year'].max()
    start_year = latest_year - n_years + 1
    filtered_df = df[(df['state_name'].isin(state_list)) & (df['crop_type'] == crop_type) & (df['crop_year'] >= start_year)]
    production_summary = filtered_df.groupby(['state_name','crop'])['production'].sum().reset_index()
    top_crops_by_state = {}
    for state in state_list:
        state_data = production_summary[production_summary['state_name'] == state]
        top_m = state_data.sort_values(by='production',ascending = False).head(M)['crop'].tolist()
        top_crops_by_state[state] = top_m
    return top_crops_by_state

def answer_question_1(df,state_x , state_y,n_years,crop_type_c,m_crops):
    # Synthesizes the answer for the first complex question (Q1)
    rainfall_results = compare_recent_avg_rainfall(df, state_list=[state_x,state_y], n_years= n_years)
    top_crop_results = get_top_m_crops(df, state_list=[state_x,state_y], crop_type = crop_type_c, n_years = n_years, M = m_crops)
    rainfall_x = rainfall_results.get(state_x,'N/A')
    rainfall_y = rainfall_results.get(state_y,'N/A')
    crops_x = ', '.join(top_crop_results.get(state_x,['N/A']))
    crops_y = ', '.join(top_crop_results.get(state_y,['N/A']))
    response = f"--- Analysis for Last {n_years} Years --\n\n"
    response += f"1.Average Annual Rainfall Comparison: \n"
    response += f"  - **{state_x}:** {rainfall_x} mm\n"
    response += f"  - **{state_y}:** {rainfall_y} mm\n"
    if rainfall_x > rainfall_y:
        higher_state = state_x
    elif rainfall_y > rainfall_x:
        higher_state = state_y
    else:
        higher_state = "Neither"
    response += f" *Conclusion: *{higher_state} recorded the higher average rainfall over the period .\n\n"
    response += f"2. Top {m_crops} {crop_type_c} Crops by Production Volume:\n"
    response += f"   - **{state_x}:** {crops_x}\n"
    response += f"   - **{state_y}:** {crops_y}\n\n"
    response += f"**Data Source Citattion:** All data synthesized from the integrated master dataset from the Ministry of Agriculture & Farmer Welfate and the India Meteorlogical Department (IMD) from the data.gov.in portal."
    return response

def get_max_min_district_production(df,state_x,state_y,crop_z):
    # Identifies the district with the highest/lowest production (Q2)
    latest_year = df['crop_year'].max()
    filtered_df = df[(df['crop_year'] == latest_year) & (df['crop'] == crop_z)].copy()
    district_summary = filtered_df.groupby(['state_name','district_name'])['production'].sum().reset_index()
    df_x = district_summary[district_summary['state_name'] == state_x]
    if df_x.empty:
        max_district, max_production = 'N/A', 0.0
    else:
        max_row = df_x.loc[df_x['production'].idxmax()]
        max_district, max_production = max_row['district_name'], max_row['production']
    df_y = district_summary[district_summary['state_name'] == state_y]
    if df_y.empty:
        min_district, min_production = 'N/A', 0.0
    else:
        df_y_producers = df_y[df_y['production'] > 0]
        min_row = df_y_producers.loc[df_y['production'].idxmin()] if not df_y_producers.empty else df_y.loc[df_y['production'].idxmin()]
        min_district, min_production = min_row['district_name'], min_row['production']
    return {'latest_year' : latest_year, state_x : {'district': max_district, 'production': max_production}, state_y : {'district': min_district, 'production': min_production}}

def answer_question_2(production_dict, state_x, state_y, crop_z):
    # Synthesizes the answer for Q2
    latest_year = production_dict['latest_year']
    x_data, y_data = production_dict[state_x], production_dict[state_y]
    max_district, max_production = x_data['district'], x_data['production']
    min_district, min_production = y_data['district'], y_data['production']
    response = f"--- District Production Analysis for {crop_z} (Latest Year: {latest_year}) --\n\n"
    response += f"1. Highest Production District in {state_x}: \n - The district with the maximum production of {crop_z} was **{max_district}** (Total Production: {max_production:,.2f} units).\n\n"
    response += f"2. Lowest Production District in {state_y}: \n - The district with the minimum production of {crop_z} was **{min_district}** (Total Production: {min_production:,.2f} units). \n\n"
    production_difference = max_production - min_production
    response += f"3. Comparative Summary: \n  - Th highest producing district in {state_x} produced approximately ** {production_difference:,.2f}** more units than the lowest producing district in {state_y} in {latest_year}."
    return response

def get_yield_and_rainfall_trend(df, state_name, crop_type, n_years):
    # Calculates the annual average crop yield and rainfall (Q3/Q4 helper)
    df_with_yield = df[df['area'] > 0].copy()
    df_with_yield['yield'] = df_with_yield['production'] / df_with_yield['area']
    latest_year = df_with_yield['crop_year'].max()
    start_year = latest_year - n_years + 1
    filtered_df = df_with_yield[(df_with_yield['state_name'] == state_name) & (df_with_yield['crop_type'] == crop_type) & (df_with_yield['crop_year'] >= start_year)]
    if filtered_df.empty: return pd.DataFrame()
    trend_df = filtered_df.groupby('crop_year').agg(average_yield = ('yield','mean'), average_rainfall = ('annual_rainfall_mm','mean')).reset_index()
    return trend_df

def calculate_correlation(trend_df, metric_1 = 'average_yield', metric_2 = 'average_rainfall'):
    # Calculates the Pearson correlation coefficient
    if trend_df.empty or len(trend_df) < 2: return np.nan
    correlation = trend_df[metric_1].corr(trend_df[metric_2])
    return correlation

def answer_question_3(trend_df, correlation_value , state_name, crop_type):
    # Synthesizes the answer and plots for Q3
    if trend_df.empty: return f"Analysis failed: No data found for {crop_type} in {state_name} over the requested period."
    start_year, end_year = trend_df['crop_year'].min(), trend_df['crop_year'].max()
    corr_abs = abs(correlation_value)
    if corr_abs >= 0.7: strength = "strong"
    elif corr_abs >= 0.4: strength = "moderate"
    else: strength = "weak or negligible"
    if correlation_value >0: direction, impact_summary = "positive", "Suggests that higher rainfall years tend to coincide with higer average yields."
    elif correlation_value <0: direction, impact_summary = "negative", "Suggests that higher rainfall years tend to coincide with lower average yields (possibly due to flooding or excess moisture)."
    else: direction, impact_summary = "no linear", "No clear linear relationship is apparent in the historical data."
    avg_yield, avg_rainfall = trend_df['average_yield'].mean(), trend_df['average_rainfall'].mean()
    response = f"--- Correlation Analysis: {crop_type} in {state_name} ({start_year}-{end_year}) ---\n\n"
    
    st.markdown("### Trend Visualization:")
    st.line_chart(trend_df, x = 'crop_year', y='average_yield', color='#4CAF50')
    st.caption('Annual Average Yield Trend (Units per Area)')
    st.line_chart(trend_df, x='crop_year', y='average_rainfall', color='#0077b6')
    st.caption('Annual Average Rainfall (mm)')
    
    response += f"1. Correlation Summary:\n  - **Pearson Correlation Coefficient (Yield vs. Rainfall):**{correlation_value:.4f}\n  - **Interpretation: ** The relationship between annual average yield and annual average rainfall is {strength} and {direction}.\n\n"
    response += f"2. Apparent Impact:\n  - The data shows a {strength} {direction} correlation.{impact_summary}\n  - Over the analyzed period, the average annual yield was {avg_yield:.3f} units, corresponding to an average annual rainfall of {avg_rainfall:.2f} mm.\n\n"
    response += "3. Trend Data Summary (Visualization):\n  -Year with high yield/rainfall volatility should be further investigated (e.g., 2012, which had the lowest rainfall ({trend_df['average_rainfall'].min():.2f} mm) but an anomalous spike in yield ({trend_df['average_yield'].max():.3f})).\n"
    return response

def get_single_crop_trend(df,state_name, crop_name, n_years):
    # Calculates the annual average crop yield and rainfall for a single crop (Q4 helper)
    df_with_yield = df[df['area'] >0].copy()
    df_with_yield['yield'] = df_with_yield['production'] / df_with_yield['area']
    latest_year = df_with_yield['crop_year'].max()
    start_year = latest_year - n_years + 1
    filtered_df = df_with_yield[(df_with_yield['state_name'] == state_name) & (df_with_yield['crop'] == crop_name) & (df_with_yield['crop_year'] >= start_year)]
    if filtered_df.empty: return pd.DataFrame()
    trend_df = filtered_df.groupby("crop_year").agg(average_yield = ('yield', 'mean'), average_rainfall = ('annual_rainfall_mm', 'mean')).reset_index()
    return trend_df

def answer_question_4(df, region_y, crop_a,crop_b, n_years):
    # Synthesizes the policy arguments and plots for Q4
    trend_a = get_single_crop_trend(df, region_y, crop_a, n_years)
    trend_b = get_single_crop_trend(df, region_y, crop_b, n_years)
    if trend_a.empty or trend_b.empty:
        missing_crop = ""
        if trend_a.empty: missing_crop += f"{crop_a} "
        if trend_b.empty: missing_crop += f"{crop_b}"
        return f"Policy analysis failed: Insufficient data (no recorded production/area) found for {missing_crop} in {region_y} over the last {n_years} years. Please select different crops or adjust the time period."
    corr_a, avg_yield_a, avg_rainfall_a = calculate_correlation(trend_a), trend_a['average_yield'].mean(), trend_a['average_rainfall'].mean()
    corr_b, avg_yield_b, avg_rainfall_b = calculate_correlation(trend_b), trend_b['average_yield'].mean(), trend_b['average_rainfall'].mean()
    arguments = []
    if abs(corr_a) < abs(corr_b):
        arg1 = f"**1. Enhanced Climate Resilience:** Crop **{crop_a}** exhibits a **weaker correlation ({corr_a:.2f})** between yield and rainfall than Crop **{crop_b}** ({corr_b:.2f}). This suggests that {crop_a} is inherently more resilient to rainfall variability (droughts or floods) in {region_y}, mitigating risk for farmers."
    else:
        arg1 = f"**1. Predictable Water Dependency:** While both crops show a similar level of dependency, promoting **{crop_a}** is strategic because its production trend is less volatile overall, leading to more predictable agricultural income for farmers."
    arguments.append(arg1)
    if avg_rainfall_a < avg_rainfall_b:
        arg2 = f"**2. Water Conservation:** The data shows that **{crop_a}** achieved its average yield (**{avg_yield_a:.2f}** units) with a lower average annual rainfall (**{avg_rainfall_a:.2f} mm**) over the last {n_years} years, whereas **{crop_b}** required **{avg_rainfall_b:.2f} mm**. This confirms **{crop_a}** is the less water-intensive choice for the region."
    else:
        yield_per_rainfall_a, yield_per_rainfall_b = avg_yield_a / avg_rainfall_a, avg_yield_b / avg_rainfall_b
        arg2 = f"**2. Superior Water Productivity:** **{crop_a}** demonstrates higher water productivity ({yield_per_rainfall_a:.4f} yield units per mm of rainfall) compared to **{crop_b}** ({yield_per_rainfall_b:.4f}), signifying a more efficient use of available water resources in {region_y}."
    arguments.append(arg2)
    if avg_yield_a > avg_yield_b:
        arg3 = f"**3. Higher Average Output:** Over the analysis period, **{crop_a}** demonstrated a higher average annual yield (**{avg_yield_a:.2f} units**) compared to **{crop_b}** (**{avg_yield_b:.2f} units**). Promoting {crop_a} directly increases overall agricultural output per unit of land in {region_y}."
    else:
        arg3 = f"**3. Mitigating Risk:** Although {crop_b} yields higher, the lower rainfall requirement and weaker climate correlation of **{crop_a}** mean its production is more stable, mitigating financial risk for small and marginal farmers during adverse weather years."
    arguments.append(arg3)
    response = f"--- Policy Recommendation for Promoting {crop_a} over {crop_b} in {region_y} (Based on Last {n_years} Years) ---\n\n"
    
    # Plotting for Q4
    st.markdown("#### 📉 Yield Trend Comparison:")
    yield_compare = trend_a[['crop_year', 'average_yield']].rename(columns={'average_yield': crop_a})
    yield_compare[crop_b] = trend_b['average_yield']
    st.line_chart(yield_compare.set_index('crop_year'), y=[crop_a, crop_b])
    st.caption(f"Annual Average Yield Trend ({crop_a} vs. {crop_b})")
    st.markdown("#### 🌧️ Rainfall Trend (Context):")
    rainfall_context = trend_a[['crop_year', 'average_rainfall']].set_index('crop_year')
    st.line_chart(rainfall_context, use_container_width=True)
    st.caption(f"Average Annual Rainfall in {region_y}")
    
    response += "The following are the three most compelling data-backed arguments to support the proposed policy:\n\n"
    response += "\n\n".join(arguments)
    response += "\n\n**Data Synthesis Source:** Integrated Master Dataset (Agri Prod & IMD Rainfall)."
    return response


# ---------------------------------------------------------------------------------------------------
# --- 4. STREAMLIT UI LAYOUT (MAIN APP LOGIC) ---
# ---------------------------------------------------------------------------------------------------

st.set_page_config(page_title="Project Samarth Q&A", layout="wide")
st.title("Agricultural & Climate Policy Q&A System")
st.subheader("Project Samarth Intelligent Data Synthesis")

# --- Interface for Question 1 ---
st.markdown("### 1. Rainfall and Top Crop Comparison")
st.markdown("---")

with st.container():
    col1, col2 = st.columns(2)
    
    # State and Time Inputs
    with col1:
        state_x_input = st.selectbox('State X (Max Rainfall)', options=ALL_STATES, index=ALL_STATES.index('Karnataka') if 'Karnataka' in ALL_STATES else 0, key='q1_x')
        state_y_input = st.selectbox('State Y (Compare Against)', options=[s for s in ALL_STATES if s != state_x_input], index=ALL_STATES.index('Maharashtra') if 'Maharashtra' in ALL_STATES else 0, key='q1_y')
        n_years_input = st.number_input('Analyze over N Years:', min_value=1, max_value=MAX_YEAR_SPAN, value=10, key='q1_n')

    # Crop Type and M Inputs
    with col2:
        crop_type_c_input = st.selectbox('Crop Type C:', options=ALL_CROP_TYPES, index=ALL_CROP_TYPES.index('Oilseed') if 'Oilseed' in ALL_CROP_TYPES else 0, key='q1_type')
        m_crops_input = st.number_input('Top M Crops:', min_value=1, max_value=10, value=3, key='q1_m')

# Button to run the analysis
if st.button('Answer Question 1: Compare Rainfall & Crops'):
    with st.spinner(f'Synthesizing data for {state_x_input} and {state_y_input}...'):
        final_answer = answer_question_1(master_df, state_x_input, state_y_input, n_years_input, crop_type_c_input, m_crops_input)
        st.markdown(final_answer)

# ---------------------------------------------------------------------------------------------------

# --- Interface for Question 2 ---
st.markdown('### 2. District-Level Max/Min Production Comparison')
st.markdown("---")

with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        state_x_q2_input = st.selectbox('State X (Max Producer)', options = ALL_STATES, key = 'q2_x', index=ALL_STATES.index('Uttar Pradesh'))
        state_y_q2_input = st.selectbox('State Y (Min Producer)', options=[s for s in ALL_STATES if s != state_x_q2_input], key='q2_y', index= ALL_STATES.index('Maharashtra'))

    with col2:
        crop_z_input = st.selectbox('Crop Z (Specific Crop Name):', options = ALL_CROPS, key='q2_crop', index=ALL_CROPS.index('Rice') if 'Rice' in ALL_CROPS else 0)

if st.button('Answer Question 2: Compare Max/Min District'):
    with st.spinner(f"Analyzing production data for {crop_z_input}..."):
        production_results = get_max_min_district_production(master_df, state_x = state_x_q2_input, state_y = state_y_q2_input, crop_z = crop_z_input)
        final_answer = answer_question_2(production_results, state_x_q2_input, state_y_q2_input, crop_z_input)
        st.markdown(final_answer)

# ---------------------------------------------------------------------------------------------------

# --- Interface for Question 3 ---
st.markdown('### 3. Yield Trend and Climate Correlation (Q3)')
st.markdown("---")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        state_y_q3_input = st.selectbox('State for Trend Analysis:', options=ALL_STATES, key='q3_state', index =ALL_STATES.index('Gujarat'))
        n_years_q3_input = st.number_input('Analyze over N Years (Q3):', min_value=1, max_value=MAX_YEAR_SPAN, value = 10, key = 'q3_years')
        
    with col2:
        crop_type_c_q3_input = st.selectbox('Crop Type for Correlation:', options = ALL_CROP_TYPES, key = 'q3_crop_type', index=ALL_CROP_TYPES.index('Oilseed'))

if st.button('Answer Question 3: Analyze Correlation'):
    with st.spinner(f'Calculating trend and correlation for {crop_type_c_q3_input} in {state_y_q3_input}...'):
        trend_data = get_yield_and_rainfall_trend(master_df, state_name=state_y_q3_input, crop_type=crop_type_c_q3_input, n_years = n_years_q3_input)
        
        if trend_data.empty:
            st.error(f"Analysis Failed: No data found for {crop_type_c_q3_input} in {state_y_q3_input} for the requested period.")
        else:
            correlation_value = calculate_correlation(trend_data)
            final_answer = answer_question_3(trend_data, correlation_value, state_y_q3_input, crop_type_c_q3_input)
            st.markdown(final_answer)

# ---------------------------------------------------------------------------------------------------

# --- Interface for Question 4 ---
st.markdown("### 4. Policy Analysis & Data-Backed Arguments (Q4)")
st.markdown("---")

with st.container():
    col1, col2 = st.columns(2)

    with col1:
        region_y_input = st.selectbox("Geographic Region Y:", options= ALL_STATES, key='q4_region', index=ALL_STATES.index('Uttar Pradesh'))
        n_years_q4_input = st.number_input('Analyze over N Years (Q4):',min_value=1, max_value =MAX_YEAR_SPAN, value=10, key='q4_years')

    with col2:
        crop_a_input = st.selectbox('Crop A (To Promote - e.g., Drought Resistant):', options = ALL_SINGLE_CROPS, key='q4_crop_a', index=ALL_SINGLE_CROPS.index('Maize') if 'Maize' in ALL_SINGLE_CROPS else 0)
        crop_b_input = st.selectbox('Crop B (To Replace - e.g., Water Intensive):', options = [c for c in ALL_SINGLE_CROPS if c != crop_a_input], key = 'q4_crop_b', index = ALL_SINGLE_CROPS.index('Rice') if 'Rice' in ALL_SINGLE_CROPS else 0)

if st.button('Answer Question 4: Generate Policy Arguments' ):
    with st.spinner(f'Synthesizing policy arguments for {crop_a_input} vs {crop_b_input} in {region_y_input}...'):
        final_answer = answer_question_4(master_df, region_y_input, crop_a_input, crop_b_input, n_years_q4_input)

        st.markdown(final_answer)

