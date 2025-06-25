import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="AI Career Insights Dashboard", layout="wide")

# Load data
df = pd.read_csv("jobs_ai_dashboard.csv")

st.title("🤖 AI Career Insights Dashboard")

# Sidebar Filters
st.sidebar.header("🎯 Filter Jobs")

job_titles = ["All"] + sorted(df["title"].unique())
selected_title = st.sidebar.selectbox("Select Job Title", job_titles)

locations = ["All"] + sorted(df["location"].unique())
selected_location = st.sidebar.selectbox("Select Location", locations)

# Extract all skills
all_skills = set()
for skills in df["skills_required"].dropna():
    for skill in skills.split(','):
        all_skills.add(skill.strip())

selected_skills = st.sidebar.multiselect("Filter by Skill(s):", sorted(all_skills))

min_salary = int(df["salary"].min())
max_salary = int(df["salary"].max())
salary_range = st.sidebar.slider("Select Salary Range", min_salary, max_salary, (min_salary, max_salary))

# Apply filters
filtered_df = df.copy()

if selected_title != "All":
    filtered_df = filtered_df[filtered_df["title"] == selected_title]

if selected_location != "All":
    filtered_df = filtered_df[filtered_df["location"] == selected_location]

filtered_df = filtered_df[filtered_df["salary"].between(salary_range[0], salary_range[1])]

if selected_skills:
    filtered_df = filtered_df[filtered_df["skills_required"].str.contains('|'.join(selected_skills), case=False, na=False)]

# Show Raw Data
if st.checkbox("🔍 Show Raw Data"):
    st.dataframe(df)

# Show Filtered Data
st.subheader("📋 Filtered Job Listings")
st.dataframe(
    filtered_df[["title", "company", "location", "salary", "skills_required"]],
    height=200)

# Download Filtered Data
st.download_button(
    label="📥 Download Filtered Jobs as CSV",
    data=filtered_df.to_csv(index=False),
    file_name='filtered_jobs.csv',
    mime='text/csv'
)

# Charts
st.subheader("📊 Visual Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**1. Salary Distribution**")
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.hist(filtered_df["salary"], bins=8, color="skyblue", edgecolor="black")
    ax.set_xlabel("Salary")
    ax.set_ylabel("Number of Jobs")
    st.pyplot(fig)

with col2:
    st.markdown("**2. Average Salary by Location**")
    avg_salary = filtered_df.groupby("location")["salary"].mean().sort_values()
    fig, ax = plt.subplots(figsize=(6, 4))
    avg_salary.plot(kind="barh", color="lightgreen", edgecolor="black", ax=ax)
    ax.set_xlabel("Average Salary")
    st.pyplot(fig)

col3, col4 = st.columns(2)

with col3:
    st.markdown("**3. Job Distribution by Title (Donut)**")
    title_counts = filtered_df["title"].value_counts()
    fig, ax = plt.subplots(figsize=(5, 5))
    wedges, texts, autotexts = ax.pie(title_counts, labels=title_counts.index, autopct="%1.1f%%",
                                      startangle=90, wedgeprops=dict(width=0.4))
    ax.set_title("Job Titles")
    st.pyplot(fig)

with col4:
    st.markdown("**4. Salary Range by City (Boxplot)**")
    if len(filtered_df["location"].unique()) > 1:
        fig, ax = plt.subplots(figsize=(6, 4))
        filtered_df.boxplot(column="salary", by="location", ax=ax)
        plt.xticks(rotation=90)
        ax.set_title("Salary by Location")
        plt.suptitle("")
        st.pyplot(fig)

# Heatmap – Skill vs Location
st.markdown("**5. Jobs by Skill and Location (Heatmap)**")
skill_df = df.copy()
skill_df["skills_required"] = skill_df["skills_required"].str.split(",")
exploded = skill_df.explode("skills_required")
exploded["skills_required"] = exploded["skills_required"].str.strip()

pivot = exploded.pivot_table(index="skills_required", columns="location", aggfunc="size", fill_value=0)

fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot, cmap="YlGnBu", annot=False, fmt="d", ax=ax)
ax.set_title("Jobs by Skill and Location")
st.pyplot(fig)
