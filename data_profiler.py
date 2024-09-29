import streamlit as st
import subprocess
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

# Install xlsxwriter if not installed
try:
    import xlsxwriter
except ModuleNotFoundError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "xlsxwriter"])
    import xlsxwriter

# Mock authentication (replace with a proper authentication mechanism)
USERS = {'user1': 'password1', 'user2': 'password2'}


# Function to handle sign-in
def authenticate(username, password):
    if USERS.get(username) == password:
        return True
    else:
        return False


# Function to load data
def load_data(file):
    try:
        datafile = pd.read_csv(file)
        return datafile
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


# Function to clean data
def clean_data(datafile):
    # Handle missing values
    datafile = datafile.dropna()

    # Convert data types if necessary
    for column in datafile.columns:
        if datafile[column].dtype == 'object':
            try:
                datafile[column] = pd.to_numeric(datafile[column])
            except ValueError:
                continue
    return datafile


# Function to display data overview
def data_overview(datafile):
    st.write("Data Overview")
    st.write("Number of Records:", datafile.shape[0])
    st.write("Number of Variables:", datafile.shape[1])
    st.write(datafile.head())
    st.write("Data Types:")
    st.write(datafile.dtypes)


# Function to perform missing values analysis
def missing_values_analysis(datafile):
    st.write("Missing Values Analysis")
    missing_values = datafile.isnull().sum()
    st.write(missing_values)
    return missing_values


# Function to display summary statistics
def summary_statistics(datafile):
    st.write("### Summary Statistics")
    summary_stats = datafile.describe()
    st.write(summary_stats)
    plt.figure(figsize=(10, 6))
    sns.heatmap(summary_stats, annot=True, fmt='g', cmap='viridis')
    st.pyplot(plt)

# Function to display data types
def data_types_analysis(datafile):
    st.write("### Data Types")
    st.write(datafile.dtypes)

# Function to calculate basic statistics
def calculate_basic_statistics(datafile):
    st.write("### Basic Statistics")
    numeric_data = datafile.select_dtypes(include=['float64', 'int64'])
    stats = numeric_data.describe().T
    stats['median'] = numeric_data.median()
    st.write(stats)
    plt.figure(figsize=(10, 6))
    sns.heatmap(stats, annot=True, fmt='g', cmap='viridis')
    st.pyplot(plt)


# Function to plot histograms
def plot_histograms(datafile):
    st.write("Data Distribution")
    for column in datafile.select_dtypes(include=['float64', 'int64']).columns:
        st.write(f"Distribution of {column}")
        plt.figure(figsize=(10, 6))
        sns.histplot(datafile[column].dropna(), kde=True)
        st.pyplot(plt)


# Function to plot scatter plot
def plot_scatter(datafile):
    st.write("Scatter Plot")
    numerical_columns = datafile.select_dtypes(
        include=['float64', 'int64']).columns
    x_axis = st.selectbox("Select X-axis variable", numerical_columns)
    y_axis = st.selectbox("Select Y-axis variable", numerical_columns)

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=datafile[x_axis], y=datafile[y_axis])
    st.pyplot(plt)


# Function to plot box plots
def plot_boxplots(datafile):
    st.write("Box Plots")
    for column in datafile.select_dtypes(include=['float64', 'int64']).columns:
        st.write(f"Box Plot of {column}")
        plt.figure(figsize=(10, 6))
        sns.boxplot(y=datafile[column].dropna())
        st.pyplot(plt)


# Function to plot pie charts
def plot_piecharts(datafile):
    st.write("Pie Charts")
    categorical_columns = datafile.select_dtypes(include=['object']).columns
    for column in categorical_columns:
        st.write(f"Pie Chart of {column}")
        value_counts = datafile[column].value_counts()
        if len(value_counts) > 10:
            other_count = value_counts[10:].sum()
            value_counts = pd.concat([value_counts[:10], pd.Series({'Other': other_count})])
        plt.figure(figsize=(12, 8))
        wedges, texts, autotexts = plt.pie(
            value_counts, 
            autopct='%1.1f%%', 
            startangle=90, 
            pctdistance=0.85, 
            explode=[0.05]*len(value_counts), 
            labels=None
        )
        plt.gca().set_aspect('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.legend(wedges, value_counts.index, loc='center left', bbox_to_anchor=(1, 0.5), title=column)
        plt.ylabel('')  # Hide the y-label
        plt.title(f"Pie Chart of {column}", fontsize=12)
        st.pyplot(plt)


# Function to plot heatmaps
def plot_heatmaps(datafile):
    st.write("Missing Values Heatmap")
    plt.figure(figsize=(10, 6))
    sns.heatmap(datafile.isnull(), cbar=False)
    st.pyplot(plt)

    st.write("Correlation Heatmap")
    numerical_data = datafile.select_dtypes(include=['float64', 'int64'])
    if not numerical_data.empty:
        correlation_matrix = numerical_data.corr()
        plt.figure(figsize=(10, 6))
        sns.heatmap(correlation_matrix,
                    annot=True,
                    cmap='coolwarm',
                    vmin=-1,
                    vmax=1)
        st.pyplot(plt)
    else:
        st.write("No numerical data available to plot correlation heatmap.")


# Function to generate and download the report
def generate_report(datafile):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        datafile.to_excel(writer, index=False, sheet_name='Data')

    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    download_link = f'<a href="data:application/octet-stream;base64,{b64}" download="report.xlsx">Download Report</a>'
    st.markdown(download_link, unsafe_allow_html=True)


# Main function to run the app
def main():
    st.title("Data Profiling Tool")

    # Sign-in and log-in functionality
    st.sidebar.title("User Authentication")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Username", type="password")
    if st.sidebar.button("Sign In"):
        if authenticate(username, password):
            st.sidebar.success("Logged In as {}".format(username))
        else:
            st.sidebar.error("Invalid credentials")

    if 'username' not in st.session_state:
        st.session_state.username = None

    if st.session_state.username is None:
        st.session_state.username = username if authenticate(
            username, password) else None

    if st.session_state.username:
        st.sidebar.title("Upload Your Dataset")
        uploaded_file = st.sidebar.file_uploader("Choose a file", type=['csv'])

        if uploaded_file is not None:
            datafile = load_data(uploaded_file)
            if datafile is not None:
                datafile = clean_data(datafile)
                data_overview(datafile)
                missing_values_analysis(datafile)
                summary_statistics(datafile)
                data_types_analysis(datafile)
                calculate_basic_statistics(datafile)
                plot_histograms(datafile)
                plot_scatter(datafile)
                plot_boxplots(datafile)
                plot_piecharts(datafile)
                plot_heatmaps(datafile)
                generate_report(datafile)


if __name__ == "__main__":
    main()
