

# Project Samarth Q\&A Prototype: Climate & Agriculture Synthesis

## 🚀 Mission Objective

This project, built for the Project Samarth Challenge, is an **Intelligent Q\&A System prototype** designed to overcome the challenge of data fragmentation across Indian government portals (Data.gov.in).

The primary goal is to **synthesize cross-domain insights** from disparate Ministry of Agriculture and IMD Climate datasets to provide coherent, data-backed answers for policy advising.

## 🛠️ Technology & Architecture

The application is built on a modular Python architecture designed for stability and scalability.

| Component | Technology | Rationale |
| :--- | :--- | :--- |
| **Interface** | **Streamlit** | Enables rapid development of an interactive web application entirely in Python, fulfilling the prototype requirement without complex front-end code. |
| **Data Engine** | **Python, Pandas, NumPy** | Used for high-speed data cleaning, complex filtration, grouping, and statistical analysis (correlation). |
| **Architecture** | **Single Page** | The logic is cleanly separated into helper functions (app.py) and organized UI page, ensuring high maintainability and testability. |

## 🧠 System Intelligence & Data Strategy

The core value of the system lies in its ability to unify and reason across conflicting data schemas.

### 1\. Data Integration (Phase 1)

  * **Foundation:** Data was sourced, cleaned, and merged based on three common keys: **State Name, District Name, and Crop Year.**
  * **Geographic Standardization:** IMD's complex regional subdivisions (e.g., 'West Uttar Pradesh') were **consolidated and mapped** to the single, consistent State names used in the Agricultural data (e.g., 'Uttar Pradesh').
  * **Categorical Cleaning:** Crop names were standardized (e.g., mapping synonyms like 'Paddy' to 'Rice') and categorized into **Crop Types** (e.g., Cereal, Pulse, Oilseed) to enable multi-criteria analysis (Q1, Q3).

### 2\. Analytical Logic (Phase 2)

The system uses specific functions to answer complex, multi-part questions:

| Question | Analytical Method Used | Key Output |
| :--- | :--- | :--- |
| **Q1 (Rainfall/Crops)** | Simple Aggregation & Filtering | Compares scalar values (Avg Rainfall) with categorical lists (Top $M$ Crops). |
| **Q2 (District Min/Max)** | Granular Filtration (`idxmax`/`idxmin`) | Identifies the highest and lowest production districts in different states for a single crop. |
| **Q3/Q4 (Correlation/Policy)** | **Yield Calculation & Pearson Correlation** | Quantifies the relationship (correlation coefficient) between **Crop Yield** (production/area) and **Annual Rainfall** to determine climate impact. |

## 🖼️ How to Run the Prototype Locally

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Krish5986/Project_Samarth_Q_and_A
    cd Project_Samarth_Q_and_A
    ```
2.  **Create Environment & Install Dependencies:**
      * *Note: This assumes you have Python 3.10+ installed.*
    <!-- end list -->
    ```bash
    python -m venv myenv
    .\myenv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Launch the Application:**
    ```bash
    streamlit run app.py
    ```

The application will open in your web browser, ready to run all four policy queries interactively.

-----

*Thank you for reviewing the solution to the Project Samarth Challenge.*

-----
