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

🔗 [View Interactive Map](https://open-energy-transition.github.io/Awesome-Electric-Demand/) | [Map Source Code](https://github.com/Vamsipriya22/global-demand/tree/main)

---

## 2. 📊 National-Level Datasets

The repository currently provides electricity demand data for a range of countries across the following regions:

- Europe
- Asia
- Oceania
- North America
- South America
- Some subnational/regional datasets are also included where national data is unavailable.

To improve accessibility, a **static global map** is added, highlighting countries and regions with available data. This provides the users with a quick visual overview of coverage.


![Static Global Map](figures/available_countries.png "Countries and regions with available electricity demand data")



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

## 3. 🚀 Roadmap and Future Work

The following enhancements are currently under development:

- Expanding coverage to include demand data sources for more countries and sub-national regions.
- Providing a static global map that highlights countries and regions with available data. This will give users a quick visual overview of data coverage.
- Enhancing the Global Demand Data Map by:
  - Adding links to country-level demand data sources.
  - Improving visual presentation through clear color schemes for better differentiation between countries.

> Note: Tasks related to data processing, ETL pipelines, and cloud storage integration are maintained in the companion repository: [`electric-demand-data`](https://github.com/open-energy-transition/electric-demand-data)
---

## 4. 📜 Licensing and Usage
All data sources retain the licenses of their original providers. Users are advised to refer the specific licensing terms of each source before using or distributing the data.

> ⚖️ **Please ensure proper attribution when utilizing any data source from this repository.**

---

## 🤝 Contributions

Contributions and feedback are welcome!

- Contributions are welcome in the form of adding links to websites that provide hourly or sub-hourly electricity demand data, including information on data availability timelines and licensing conditions.
- Use [GitHub Issues](https://github.com/open-energy-transition/Awesome-Electric-Demand/issues) for bug reports, data requests, or suggestions.
- Submit [Pull Requests](https://github.com/open-energy-transition/Awesome-Electric-Demand/pulls) for adding new data sources or enhancing metadata.


---

📌 *Built with the goal of democratizing energy data access for a sustainable future.*
