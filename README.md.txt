# Fusarium Proteomics Atlas

An interactive dashboard for exploring processed proteomics data from the Fusarium head blight project.

## Features
- **Protein Explorer** – Search and visualize protein expression across experimental conditions.
- **Heatmap Explorer** – Compare expression patterns for protein classes or custom protein lists.
- **Full Data Table** – Interactive AgGrid table with filtering and sorting.
- **Help & Info Tab** – Project description, sample code legend, and file upload requirements.

## Tech Stack
- **Python** with [Streamlit](https://streamlit.io/) for the web application.
- **Pandas** for data handling and preprocessing.
- **Plotly** and **Seaborn** for visualizations.
- **AgGrid** for interactive data tables.

## Project Structure
Fusarium_Project/
├─ cleaned/ # Processed datasets for the dashboard
├─ images/ # Images used in the dashboard
├─ scripts/ # dashboard.py and utility scripts
├─ requirements.txt # Python dependencies
├─ runtime.txt # Python version for deployment
├─ .gitignore # Files and folders to ignore in Git
└─ README.md # Project documentation



## Running Locally
1. **Clone the repository**:
   ```bash
   git clone https://github.com/kxj11/Fusarium_Proteomics_Atlas.git
   cd Fusarium_Proteomics_Atlas

2. Install dependencies:

pip install -r requirements.txt

3. Launch the app:
streamlit run scripts/dashboard.py

Deployment
This app can be deployed on:

Streamlit Community Cloud

Hugging Face Spaces

Deploy on Streamlit Cloud:

Connect your GitHub account.

Select this repository (Fusarium_Proteomics_Atlas).

Set Main file path to:

scripts/dashboard.py

4. Click Deploy.