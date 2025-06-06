import os
import pandas as pd
import streamlit as st

# Risk scoring criteria
scores = {
    'objective': {
        'Capital Preservation': 5,
        'Retirement Planning': 10,
        'Wealth Management': 12,
        'Capital Appreciation': 20,
        'Capital Appreciation/Wealth Creation': 20,
        'Other': 8
    },
    'age': {
        '18 to 30 years': 20,
        '31 to 40 years': 15,
        '41 to 50 years': 10,
        '51 to 60 years': 5,
        'Above 60 years': 3
    },
    'income': {
        'Under INR 10 Lacs': 5,
        'INR 10 Lacs to INR 1 Crore': 10,
        'INR 1 Crore to INR 5 Crore': 15,
        'Above INR 5 Crore': 20,
        'Retired': 3
    },
    'dependents': {
        'No dependants': 10,
        '1 dependant': 7,
        '1 dependant (earning)': 8,
        '2 to 3 dependants': 5,
        'More than 3 dependants': 2
    },
    'investable_percent': {
        '0% to 25%': 5,
        '25% to 50%': 10,
        'Above 50%': 15,
        'I currently have no income but adequate assets': 10,
        'Neither': 0
    },
    'liabilities': {
        'Less than 25% of income': 10,
        '25% to 50% of income': 7,
        'More than 50% of income': 3,
        'I have enough surplus income': 10,
        'I have no liabilities': 15
    },
    'expected_return': {
        '6% per annum': 2,
        '10% per annum': 5,
        '12% per annum': 10,
        '15% per annum': 15,
        'More than 15% per annum': 20
    },
    'risk_agree': {
        'Strongly disagree': 2,
        'Disagree': 5,
        'Agree': 10,
        'Strongly agree': 15
    },
    'emergency_fund': {
        'No fund': 2,
        'Less than 6 months': 5,
        '6 to 12 months': 10,
        'More than 12 months': 15
    },
    'major_allocation': {
        'Savings/FD': 2,
        'Bonds': 5,
        'Mutual Funds': 10,
        'Equity/Derivatives': 15,
        'Real Estate': 8
    },
    'horizon': {
        'Less than 1 year': 2,
        '1 to 3 years': 5,
        '3 to 5 years': 10,
        'More than 5 years': 15
    },
    'drawdown_tolerance': {
        'Less than 5%': 2,
        '5% to 10%': 5,
        '10% to 20%': 10,
        '20% to 30%': 15,
        'More than 30%': 20
    },
    'advisor_visibility': {
        'Less than 25%': 3,
        '25% to 75%': 5,
        '75-100% (Full view of my financial assets)': 10
    },
    'insurance_agree': {
        'Strongly disagree': 0,
        'Disagree': 3,
        'Agree': 7,
        'Strongly agree': 10
    },
    'lifestyle_expenditure': {
        'Up to INR 1 Lacs per month': 8,
        'INR 1 - 2 Lacs per month': 6,
        'INR 2 - 3 Lacs per month': 4,
        'Over INR 3 Lacs': 2
    }
}

column_mapping = {
    'objective': 'What is your primary investment objective?',
    'age': 'What is your current age? ',
    'income': 'What is your annual take home income?',
    'dependents': 'How many people depend on you financially?',
    'investable_percent': 'What percentage of your monthly income can be invested?',
    'liabilities': 'What percentage of your take home income goes into repaying your liabilities?',
    'expected_return': 'What is your expected rate of return from your investments',
    'risk_agree': 'In order to achieve high returns I am willing to choose high risk investments.',
    'emergency_fund': 'How many months of expenses can your emergency funds cover?',
    'major_allocation': 'In your financial assets, currently the maximum surplus is parked into',
    'horizon': 'When do you expect to liquidate your investment? ',
    'drawdown_tolerance': 'I would start to worry about my investments under advice of HPPWA, if my portfolio value falls',
    'advisor_visibility': 'Does the Investment Adviser (HPPWA) have complete or partial view of your financial assets?',
    'insurance_agree': 'I have adequate family health insurance',
    'lifestyle_expenditure': 'What would be your family\'s lifestyle monthly expenditure?'
}

def normalize_response(value):
    if isinstance(value, str):
        return value.strip()
    return value

def calculate_risk_appetite(response, name):
    score_breakdown = {}
    total_possible = 233

    for key in scores:
        raw_answer = response.get(key, '').strip()
        if not raw_answer:
            return None, None, None
        score_value = scores[key].get(raw_answer, 0)
        score_breakdown[key] = score_value

    total_score = sum(score_breakdown.values())
    normalized = (total_score / total_possible) * 100

    if normalized <= 20:
        category = 'Very Conservative'
    elif normalized <= 35:
        category = 'Conservative'
    elif normalized <= 50:
        category = 'Moderate'
    elif normalized <= 65:
        category = 'Moderate to High'
    elif normalized <= 80:
        category = 'High'
    else:
        category = 'Very High'

    return round(normalized, 1), category, score_breakdown

def process_file(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(uploaded_file)
    elif ext in ['.xls', '.xlsx']:
        df = pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file format.")
        return None

    for col in column_mapping.values():
        df[col] = df[col].fillna("").apply(normalize_response)

    names, scores_list, categories, breakdowns = [], [], [], []

    for _, row in df.iterrows():
        name = row.get('Full Name', 'Unknown')
        response = {key: row.get(col, '') for key, col in column_mapping.items()}
        score, category, breakdown = calculate_risk_appetite(response, name)
        if score is not None:
            names.append(name)
            scores_list.append(score)
            categories.append(category)
            breakdowns.append(breakdown)

    result_df = pd.DataFrame({
        'Name': names,
        'Risk Score': scores_list,
        'Risk Appetite': categories
    })

    for key in scores:
        result_df[f'{key} Score'] = [b.get(key, 0) for b in breakdowns]

    return result_df

# --------- Streamlit UI ---------

st.set_page_config(page_title="Client Risk Profiler", layout="wide")
st.title("🧮 Client Risk Profiling Tool")

uploaded_file = st.file_uploader("Upload Excel or CSV file", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    st.success("✅ File uploaded successfully. Processing...")

    result_df = process_file(uploaded_file)

    if result_df is not None:
        st.dataframe(result_df.head(10))

        # Convert to Excel for download
        from io import BytesIO
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, index=False, sheet_name='Risk_Profile')
        processed_data = output.getvalue()

        st.download_button(
            label="📥 Download Risk Profile Excel",
            data=processed_data,
            file_name='Risk_Profile_Output.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )