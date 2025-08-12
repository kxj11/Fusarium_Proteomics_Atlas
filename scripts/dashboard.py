# === Fusarium Proteomics Full Dashboard ===
import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid, GridOptionsBuilder
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
import os

# === LOADER FUNCTION ===
@st.cache_data(show_spinner=False)
def load_table(name):
    DATA_DIR = Path(__file__).resolve().parent.parent / "cleaned"
    p_csv = DATA_DIR / f"{name}.csv"
    p_tsv_gz = DATA_DIR / f"{name}.tsv.gz"
    p_tsv = DATA_DIR / f"{name}.tsv"
    p_xlsx = DATA_DIR / f"{name}.xlsx"

    if p_csv.exists():
        return pd.read_csv(p_csv)
    if p_tsv_gz.exists():
        return pd.read_csv(p_tsv_gz, sep="\t", compression="gzip")
    if p_tsv.exists():
        return pd.read_csv(p_tsv, sep="\t")
    if p_xlsx.exists():
        return pd.read_excel(p_xlsx)
    raise FileNotFoundError(f"Could not find {name} in {DATA_DIR}")



# === PAGE CONFIG ===
st.set_page_config(page_title="Fusarium Proteomics Atlas", layout="wide")




# === PATH SETUP ===
base_dir = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(base_dir, "cleaned", "cleaned_data.csv")
mapping_path = os.path.join(base_dir, "cleaned", "mapping_table.csv")
class_map_path = os.path.join(base_dir, "cleaned", "protein_class_mapping.csv")
uniprot_file = "uniprot_id_to_name_mapping.tsv.gz"
uniprot_path = os.path.join(base_dir, "cleaned", uniprot_file)
image_path = os.path.join(base_dir, "images", "green.jpg")
compression_type = 'gzip' if uniprot_file.endswith('.gz') else None




# === LOAD DATA ===
df = pd.read_csv(data_path)
mapping_df = pd.read_csv(mapping_path)
class_df = pd.read_csv(class_map_path)
class_df.rename(columns={"UniProt ID": "T: Single Protein IDs"}, inplace=True)
uniprot_map = pd.read_csv(uniprot_path, sep='\t', compression=compression_type)
uniprot_map = uniprot_map[['From', 'Protein names']]
uniprot_map.rename(columns={'From': 'T: Single Protein IDs', 'Protein names': 'UniProt Protein Name'}, inplace=True)




# === CUSTOM THEME ===
st.markdown("""
<style>
  body, .main { background-color: #f7f5f0; color: #333; margin-top: -50px; }
  .block-container { padding-top: 1rem; }
  h1, h2, h3 { color: #4e7039; }
  .stTabs [data-baseweb="tab"] {
      background-color: #e8ecd8; border-radius: 0.5rem; margin-right: 1rem;
  }
  .stTabs [data-baseweb="tab-active"] {
      background-color: #d4d7c3; color: #1e4421;
  }
</style>
""", unsafe_allow_html=True)




# === SIDEBAR ===
with st.sidebar:
    st.image(image_path, width=150)
    st.markdown("## Filter Samples")
    groups = mapping_df["Group"].dropna().unique()
    treatments = mapping_df["Cultivar_Treatment"].dropna().unique()
    selected_groups = st.multiselect("Select Groups:", groups, default=groups)
    selected_treatments = st.multiselect("Select Treatments:", treatments, default=treatments)




# === FILTERING ===
filtered_map = mapping_df[
  mapping_df["Group"].isin(selected_groups) &
  mapping_df["Cultivar_Treatment"].isin(selected_treatments)
]
selected_columns = filtered_map["Original_Column"].tolist()
selected_labels = filtered_map["TMT_Label"].tolist()
rename_dict = dict(zip(selected_columns, selected_labels))
df_filtered = df.rename(columns=rename_dict)
df_selected = df_filtered[selected_labels + ["T: Single Protein IDs", "Protein names", "Gene names"]]
df_selected[selected_labels] = df_selected[selected_labels].apply(pd.to_numeric, errors='coerce')
df_selected = df_selected.merge(uniprot_map, on='T: Single Protein IDs', how='left')
df_selected = df_selected.merge(class_df, on='T: Single Protein IDs', how='left')




sample_to_group = dict(zip(filtered_map["TMT_Label"], filtered_map["Group"]))
sample_to_treatment = dict(zip(filtered_map["TMT_Label"], filtered_map["Cultivar_Treatment"]))




# === HEADER ===
st.markdown("""
<h1 style='text-align:center; color:#4e7039;'>Fusarium Head Blight Proteomics Atlas</h1>
<p style='text-align:center;'>Explore expression trends across wheat varieties, treatments, and timepoints.</p>
<hr>
""", unsafe_allow_html=True)




# === TABS ===
tabs = st.tabs(["Home", "Protein Explorer", "Full Data Table", "Heatmap Explorer", "Help & Info", "Upload Your Own Data"])




# === HOME TAB ===
with tabs[0]:
  st.subheader("Background")
  st.markdown("""
**Fusarium Head Blight (FHB)** is a serious fungal disease affecting wheat crops globally, with direct impacts on food security and agricultural sustainability.
This project, the **Fusarium Proteomics Atlas**, provides an interactive platform to explore proteomic trends across multiple wheat varieties, infection statuses, and timepoints.




Fusarium infection research often spans multiple studies, technologies (DDA and TMT), and time periods. To support this research, our database compiles processed proteomics dataset from a major study by Buchanan et al.(2025) (https://www.sciencedirect.com/science/article/pii/S1535947625000866), covering infected and uninfected wheat across years, timepoints, and cultivars.




Rather than focusing on minute details, this atlas is designed to help researchers, plant pathologists, and breeders explore large-scale patterns and trends in protein expression related to Fusarium infection.




---




### Why this Matters:
Researchers often struggle to access harmonized, user-friendly tools to examine proteomic trends across multiple experiments.
This platform bridges that gap by enabling:




- Accessible, interactive data exploration
- Focus on big-picture trends across years, cultivars, and treatments
- Hypothesis generation for downstream research
- Support for both technical and non-technical users




---




### How to Use This Database:
- **Protein Explorer**: Search and visualize protein intensity across treatments and cultivars.
- **Full Data Table**: Browse, search, and download datasets.
- **Help & Info**: Learn more about datasets and project background.




---




**Project Lead**: Kunjal Akolkar
**Advisors**: Dr. Jennifer Geddes-McAlister, Dr. Lewis Lukens
**Built with**: Streamlit + Plotly + AgGrid + Seaborn
""")




# === PROTEIN EXPLORER ===
with tabs[1]:
  st.subheader("Protein Explorer")
  df_selected['Dropdown Label'] = df_selected['UniProt Protein Name'].fillna('Unknown') + " (" + df_selected['T: Single Protein IDs'] + ")"
  dropdown_options = df_selected[['T: Single Protein IDs', 'Dropdown Label']].drop_duplicates()




  selected_protein_label = st.selectbox("Select a protein:", dropdown_options['Dropdown Label'].sort_values())
  selected_protein = dropdown_options[dropdown_options['Dropdown Label'] == selected_protein_label]['T: Single Protein IDs'].values[0]




  protein_data = df_selected[df_selected['T: Single Protein IDs'] == selected_protein]
  melted = protein_data.melt(id_vars=["T: Single Protein IDs"], value_vars=selected_labels,
                             var_name="Sample", value_name="Intensity")
  melted["Group"] = melted["Sample"].map(sample_to_group)
  melted["Treatment"] = melted["Sample"].map(sample_to_treatment)




  fig = px.box(melted, x="Group", y="Intensity", color="Treatment", points="all",
               title=f"Intensity for {selected_protein}", labels={"Intensity": "Log2 Intensity"})
  st.plotly_chart(fig, use_container_width=True)




  st.dataframe(melted.groupby("Group")["Intensity"].describe())




# === FULL DATA TABLE ===
with tabs[2]:
  st.subheader("Full Data Table")
  gb = GridOptionsBuilder.from_dataframe(df_selected)
  for col in selected_labels:  # Format numeric TMT intensity columns
      gb.configure_column(col, type=["numericColumn", "numberColumnFilter", "customNumericFormat"], precision=2)
  gb.configure_default_column(filter=True, sortable=True, resizable=True)
  gb.configure_column("UniProt Protein Name", header_name="Protein Name", filter='agTextColumnFilter')
  gb.configure_column("Gene names", header_name="Gene Names", filter='agTextColumnFilter')
  gb.configure_pagination(enabled=True)
  gridOptions = gb.build()
  AgGrid(df_selected, gridOptions=gridOptions, height=500, fit_columns_on_grid_load=True)




  csv = df_selected.to_csv(index=False).encode('utf-8')
  st.download_button("Download Filtered Data", data=csv, file_name='filtered_data.csv', mime='text/csv')




# === HEATMAP EXPLORER ===
# === HEATMAP EXPLORER ===
with tabs[3]:
    st.subheader("Heatmap Explorer")

    # Dictionary for all class definitions (edit to match your mapping file)
    CLASS_DEFS = {
        "Housekeeping": "Core maintenance proteins (e.g., ribosomal, basic metabolism) that tend to be relatively stable.",
        "Kinase": "Signaling enzymes that phosphorylate targets; coordinate stress and defense pathways.",
        "Mycotoxin-related": "Proteins implicated in mycotoxin (e.g., DON) detox/response or pathways affecting toxin handling.",
        "Stress-response": "General stress/defense machinery (e.g., heat-shock proteins, PR proteins, chaperones).",
        "Transporter": "Membrane transport proteins moving ions/metabolites/toxins; can modulate stress tolerance.",
        "Other": "Proteins not confidently assigned based on current annotations."
    }

    heatmap_mode = st.selectbox("Select Heatmap Mode", ["Protein Class", "Custom Proteins"])

    if heatmap_mode == "Protein Class":
        selected_class = st.selectbox(
            "Choose a Protein Class:",
            sorted(df_selected["Protein Class"].dropna().unique())
        )
        class_subset = df_selected[df_selected["Protein Class"] == selected_class]
        melted_class = class_subset.melt(
            id_vars=["UniProt Protein Name"],
            value_vars=selected_labels,
            var_name="Sample",
            value_name="Intensity"
        )
        melted_class["Group"] = melted_class["Sample"].map(sample_to_group)
        heatmap_df = melted_class.groupby(["UniProt Protein Name", "Group"])["Intensity"].mean().reset_index()
        heatmap_matrix = heatmap_df.pivot(index="UniProt Protein Name", columns="Group", values="Intensity")

        use_fixed_scale = st.checkbox("Use fixed scale (±0.2) for better contrast", value=True)

        fig_class, ax = plt.subplots(figsize=(12, 10))
        if use_fixed_scale:
            sns.heatmap(
                heatmap_matrix,
                cmap="coolwarm",
                center=0,
                vmin=-0.2, vmax=0.2,
                linewidths=0.5,
                cbar_kws={'label': 'Log2 Intensity'}
            )
        else:
            sns.heatmap(
                heatmap_matrix,
                cmap="coolwarm",
                center=0,
                linewidths=0.5,
                cbar_kws={'label': 'Log2 Intensity'}
            )
        ax.set_title(f"Class Heatmap: {selected_class}")
        ax.set_xlabel("Group")
        ax.set_ylabel("Protein Name")
        plt.xticks(rotation=45)
        st.pyplot(fig_class)

    elif heatmap_mode == "Custom Proteins":
        all_proteins = df_selected[['T: Single Protein IDs', 'UniProt Protein Name']].drop_duplicates()
        all_proteins['Label'] = all_proteins['UniProt Protein Name'].fillna('Unknown') + " (" + all_proteins['T: Single Protein IDs'] + ")"
        selected_proteins = st.multiselect(
            "Select proteins to compare:",
            options=all_proteins['Label'].sort_values()
        )
        if selected_proteins:
            selected_ids = all_proteins[all_proteins['Label'].isin(selected_proteins)]['T: Single Protein IDs'].tolist()
            custom_subset = df_selected[df_selected['T: Single Protein IDs'].isin(selected_ids)]
            melted_custom = custom_subset.melt(
                id_vars=["UniProt Protein Name"],
                value_vars=selected_labels,
                var_name="Sample",
                value_name="Intensity"
            )
            melted_custom["Group"] = melted_custom["Sample"].map(sample_to_group)
            heatmap_df = melted_custom.groupby(["UniProt Protein Name", "Group"])["Intensity"].mean().reset_index()
            heatmap_matrix = heatmap_df.pivot(index="UniProt Protein Name", columns="Group", values="Intensity")

            fig_custom, ax = plt.subplots(figsize=(12, 8))
            sns.heatmap(
                heatmap_matrix,
                cmap="coolwarm",
                center=0,
                linewidths=0.5,
                cbar_kws={'label': 'Log2 Intensity'}
            )
            ax.set_title("Custom Protein Heatmap")
            ax.set_xlabel("Group")
            ax.set_ylabel("Protein Name")
            plt.xticks(rotation=45)
            st.pyplot(fig_custom)

    # --- Always show all class definitions below heatmap ---
    st.markdown("### Protein classes in this dashboard")
    for cls, desc in CLASS_DEFS.items():
        st.markdown(f"- **{cls}** — {desc}")

    st.caption(
        "How class names were assigned: `T: Single Protein IDs` were mapped to UniProt names/keywords and GO terms, "
        "reviewed against Fusarium/DON literature, and lightly curated for ambiguous cases. "
        "These labels are stored in `protein_class_mapping.csv` and surfaced as **Protein Class** in the app."
    )



# === HELP & INFO ===
with tabs[4]:
 st.subheader("Help & Info")
 st.markdown("""
### About This Dashboard








The **Fusarium Proteomics Atlas** is an interactive tool for exploring proteomic trends in wheat under Fusarium stress.








---



### 🔍 Tab Overview

#### 🏠 Home  
Provides background on the project, its biological significance, and overall goals. It introduces users to the wheat–Fusarium system and how proteomics data is used to explore disease response. The dataset is taken from the published study by Buchanan et al.(2025) (https://www.sciencedirect.com/science/article/pii/S1535947625000866).

#### 🧫 Protein Explorer  
Use the dropdown to select any **individual protein**. You’ll see:
- A **boxplot** of log2-transformed intensity values across all sample groups
- Visualization of trends across cultivars and timepoints
- Useful for observing differential expression in response to Fusarium

#### 📊 Full Data Table  
Explore all protein-level intensity values in a searchable, sortable table:
- Filter by gene/protein name
- View all metadata and sample intensities
- Export the table as `.csv` with the download button at the bottom

#### 🌡️ Heatmap Explorer  
View intensity heatmaps across selected protein sets:
- **Protein Class Mode**: Select a protein class (e.g., defense response), and view global expression trends
- **Custom Protein Mode**: Manually select multiple proteins to compare
- **Single Protein Heatmap**: Highlight how one protein behaves across all sample groups

Great for spotting clusters of higher/lower-abundant proteins.






---






### Legend (How to Read Sample Codes)








| Code | Meaning |
|------|---------|
| **H / L / M** | High-DON (1.0 mg/ml 15-ADON) / Low-DON (0.1 mg/ml 15-ADON) / Mock (control) cultivar type |
| **N / S** | Norwell (FHB-susceptible cultivar) / Sumai#3 (FHB-resistant cultivar) |
| **24 / 120** | Hours post inoculation |








**Examples:**
- `HN24`: High-DON, Norwell, 24 hours post-inoculation
- `MS120`: Mock cultivar, Sumai, 120 hours post-inoculation








---








### FAQs








**Q:** What is Log2 Intensity?
**A:** Protein abundance values have been log2-transformed to reduce skew and enhance visualization.








**Q:** Can I download the data?
**A:** Yes! Go to the **Full Data Table** tab and use the download button at the bottom.








**Q:** Who can use this tool?
**A:** This tool is built for both bioinformatics experts and researchers without programming skills.








---








**Lead:** Kunjal Akolkar
**Advisors:** Dr. Jennifer Geddes-McAlister & Dr. Lewis Lukens
**Built with:** Streamlit + Plotly + Seaborn + AgGrid
""")






# === UPLOAD YOUR OWN DATA ===
# === UPLOAD YOUR OWN DATA ===
with tabs[5]:
    st.subheader("Upload Your Own Data")
    st.markdown("Upload a CSV file to explore your own proteomics data.")

    # --- Downloadable sample template (so users see the required format) ---
    st.markdown("#### Download a sample template")
    sample_df = pd.DataFrame(
        [
            {
                "T: Single Protein IDs": "Q9Z0V6",
                "Gene names": "GST1",
                "Protein names": "Glutathione S-transferase 1",
                "Sample1": 12.34,
                "Sample2": 12.10,
                "Sample3": 11.95,
            },
            {
                "T: Single Protein IDs": "P12345",
                "Gene names": "PR1",
                "Protein names": "Pathogenesis-related protein 1",
                "Sample1": 10.85,
                "Sample2": 11.20,
                "Sample3": 10.60,
            },
            {
                "T: Single Protein IDs": "A0A3B6B5K8",
                "Gene names": "AOX1",
                "Protein names": "Ubiquinol oxidase (alternative oxidase)",
                "Sample1": 13.05,
                "Sample2": 13.40,
                "Sample3": 13.10,
            },
        ]
    )
    sample_csv = sample_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Sample Data Template (CSV)",
        data=sample_csv,
        file_name="sample_upload_template.csv",
        mime="text/csv",
        help="Use this as a guide for column names and log2 intensity values.",
    )
    with st.expander("Preview of the sample template"):
        st.dataframe(sample_df, use_container_width=True)

    st.markdown("""
    ### Data Format Requirements (for Upload)

    Your `.csv` must include:
    - **`T: Single Protein IDs`** — e.g., UniProt IDs (P12345)
    - **`Gene names`** — gene symbols (e.g., GST1)
    - **`Protein names`** — descriptive names (e.g., Glutathione S-transferase 1)

    All **other columns** should be sample names (e.g., `Sample1`, `Sample2`, or your labels like `HN24`, `MS120`) with **log2 intensity values**.
    Each row = one protein across all samples.
    """)

    # --- Uploader ---
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file:
        user_df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        st.dataframe(user_df.head(), use_container_width=True)

        # Column validation
        required_columns = ["T: Single Protein IDs", "Gene names", "Protein names"]
        missing = [col for col in required_columns if col not in user_df.columns]
        if missing:
            st.error(f"Missing required columns: {', '.join(missing)}")
        else:
            st.success("File format looks good!")

            # Build dropdown for quick visualization
            user_df["Dropdown Label"] = user_df["Protein names"].fillna('Unknown') + " (" + user_df["T: Single Protein IDs"] + ")"
            dropdown_options = user_df[["T: Single Protein IDs", "Dropdown Label"]].drop_duplicates()

            selected_protein_label = st.selectbox(
                "Select a protein to visualize:",
                dropdown_options["Dropdown Label"].sort_values()
            )
            selected_protein = dropdown_options[
                dropdown_options["Dropdown Label"] == selected_protein_label
            ]["T: Single Protein IDs"].values[0]

            # Identify intensity columns as "everything else"
            intensity_cols = [c for c in user_df.columns if c not in required_columns + ["Dropdown Label"]]
            if not intensity_cols:
                st.warning("No intensity columns detected. Make sure you included sample columns (e.g., Sample1, Sample2...).")
            else:
                melted_user = user_df[user_df["T: Single Protein IDs"] == selected_protein].melt(
                    id_vars=["T: Single Protein IDs"], value_vars=intensity_cols,
                    var_name="Sample", value_name="Intensity"
                )

                fig = px.box(
                    melted_user, x="Sample", y="Intensity", points="all",
                    title=f"Intensity Distribution for {selected_protein}",
                    labels={"Intensity": "Log2 Intensity"}
                )
                st.plotly_chart(fig, use_container_width=True)
