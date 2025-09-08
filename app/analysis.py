import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from matplotlib.figure import Figure

def analyze_jobs(csv_path):
    df = pd.read_csv(csv_path)

    df["skills"] = df["skills"].fillna("")
    all_skills = ", ".join(df["skills"]).split(",")
    skills_series = pd.Series(all_skills).str.strip().value_counts().head(10)
    
    # Create skills plot
    skills_fig = Figure(figsize=(10,5))
    ax = skills_fig.add_subplot(111)
    sns.barplot(x=skills_series.values, y=skills_series.index, ax=ax)
    ax.set_title("Top 10 Skills")
    skills_fig.tight_layout()

    # Create salary plot
    salary_fig = Figure(figsize=(8,5))
    ax = salary_fig.add_subplot(111)
    sns.histplot(df["salary"].dropna(), bins=10, ax=ax)
    ax.set_title("Salary Distribution")
    salary_fig.tight_layout()

    return {
        "jobs": df.head(10).to_dict(orient="records"),
        "skills_fig": skills_fig,
        "salary_fig": salary_fig
    }

def create_skills_plot(df):
    """Create a skills distribution plot from job data."""
    if df.empty or 'skills' not in df.columns:
        # Return empty plot if no data
        fig = Figure(figsize=(10, 5))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No skills data available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title("Skills Distribution")
        return fig
    
    # Process skills data
    df["skills"] = df["skills"].fillna("")
    all_skills = ", ".join(df["skills"]).split(",")
    skills_series = pd.Series(all_skills).str.strip()
    skills_series = skills_series[skills_series != ""]  # Remove empty strings
    skills_counts = skills_series.value_counts().head(10)
    
    # Create plot
    fig = Figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    
    if not skills_counts.empty:
        sns.barplot(x=skills_counts.values, y=skills_counts.index, ax=ax)
        ax.set_title("Top 10 Required Skills")
        ax.set_xlabel("Number of Jobs")
        ax.set_ylabel("Skills")
    else:
        ax.text(0.5, 0.5, 'No skills data available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title("Skills Distribution")
    
    fig.tight_layout()
    return fig

def create_salary_plot(df):
    """Create a salary distribution plot from job data."""
    if df.empty or 'salary' not in df.columns:
        # Return empty plot if no data
        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, 'No salary data available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title("Salary Distribution")
        return fig
    
    # Filter out zero and negative salaries
    salary_data = df["salary"].dropna()
    salary_data = salary_data[salary_data > 0]
    
    fig = Figure(figsize=(8, 5))
    ax = fig.add_subplot(111)
    
    if not salary_data.empty:
        sns.histplot(salary_data, bins=15, ax=ax)
        ax.set_title("Salary Distribution")
        ax.set_xlabel("Salary")
        ax.set_ylabel("Number of Jobs")
    else:
        ax.text(0.5, 0.5, 'No salary data available', ha='center', va='center', transform=ax.transAxes)
        ax.set_title("Salary Distribution")
    
    fig.tight_layout()
    return fig
