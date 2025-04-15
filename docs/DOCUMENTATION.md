# 🌍 Awesome Electric Demand

**Awesome Electric Demand** is a curated repository of global electricity demand datasets, designed to enhance the accessibility, harmonization, and usability of open energy data. This initiative supports the sustainable energy transition by providing high-quality, structured, and region-specific electricity demand data.

---

## 🎯 Repository Objectives

- Serve as a curated list of websites and platforms that provide hourly or sub-hourly electricity demand data from various national and regional sources.
- Include essential metadata for each data source such as:
  - Time range of data availability
  - Licensing and usage terms
- Facilitate discoverability and transparency for researchers, analysts, and policymakers by promoting open and verifiable access to electricity demand data.

This repository is limited to hosting links and metadata only.
To access the code for downloading, extracting, and processing the data, please refer to our companion repository: [`electric-demand-data`](https://github.com/open-energy-transition/electric-demand-data).



---

## 1. 🌐 Global Demand Data Map

An interactive visualization tool has been developed to provide a centralized view of electricity demand datasets across the globe:

- **Functionality**: Users can click on individual countries to access the corresponding electricity demand data or official data source.
- **Purpose**: Simplifies navigation and enhances discoverability of regional or national datasets.

🔗 [View Interactive Map](https://vamsipriya22.github.io/global-demand/) | [Map Source Code](https://github.com/Vamsipriya22/global-demand/tree/main)

---

## 2. 📊 National-Level Datasets

The repository currently provides electricity demand data for a range of countries across the following regions:

- Europe
- Asia
- Australia and New Zealand
- North America
- Some subnational/regional datasets are also included where national data is unavailable.

To improve accessibility, this section will be enhanced with a **static global map** highlighting countries and regions with available data. This will provide users with a quick visual overview of coverage.

🛠 *[Static overview map coming soon]*  

### 🔍 Key Attributes

- **Data Sources**: ENTSO-E, AEMO, EMI, PUCSL, Kaggle, CCEI, and others.
- **Coverage**: Time series data with varying temporal resolution and historical span. Regional data is also provided in addition to the national-level datasets wherever available.
- **Licensing terms**: Provided in `README.md` as the list of data sources in the repository.

- **Metadata Table**:
  - Country name
  - Data availability (timestamp range)
  - Direct link to source platforms

The format for the list of data sources in the repository is presented in `README.md` as:

## Continent
  - ### Country
    - #### Region
      Source | Years | License

📄 [Access the Metadata Table](https://github.com/open-energy-transition/Awesome-Electric-Demand/blob/main/demand_data_table.md)

---
## 3. 📁 Data Format and Standardization

To ensure consistency and interoperability across all datasets, the following standardization protocols have been implemented:

### 📂 File Structure

All cleaned and harmonized electricity demand datasets are stored in the `Data-files/` directory.
Each file represents data from a specific country and is available in both `.csv` and `.parquet` formats.

This centralized file structure facilitates easy access, comparison, and processing of demand data across countries.

### 🧾 Data Format

- Electricity demand values are expressed in **megawatts (MW)**
- Supported output formats: **CSV** and **Parquet**

---

## 4. 🚀 Roadmap and Future Work

The following enhancements are currently under development:

- Integration with cloud storage platforms for scalable access
- Implementation of automated ETL pipelines for continuous updates
- Expansion to include additional countries and regions

---

## 5. 📜 Licensing and Usage

All datasets retain the licenses of their original sources. Users are advised to refer to the source-specific licensing terms prior to reuse or distribution.

> ⚖️ **Please ensure proper attribution** when utilizing any dataset from this repository.

---

## 🤝 Contact and Contributions

Contributions, feedback, and collaborations are welcome!

- Use [GitHub Issues](https://github.com/open-energy-transition/Awesome-Electric-Demand/issues) for bug reports or data requests
- Submit [Pull Requests](https://github.com/open-energy-transition/Awesome-Electric-Demand/pulls) for enhancements

---

📌 *Built with the goal of democratizing energy data access for a sustainable future.*
