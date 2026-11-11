# Awesome Electricity Demand

A curated collection of links to hourly or sub-hourly electricity demand data, designed to improve the accessibility and discoverability of datasets for energy system modelers and planners, while enhancing global open data coverage to support a sustainable energy transition.

<!-- summary:start: generated from data/ by scripts/build.py, do not edit -->
The list has **244 time series** from **48 data sources** for **68 countries** and their subdivisions in:

- [Africa](#africa) (3 countries)
- [Asia](#asia) (14 countries)
- [Europe](#europe) (38 countries)
- [North America](#north-america) (5 countries)
- [South America](#south-america) (6 countries)
- [Oceania](#oceania) (2 countries)
<!-- summary:end -->

Each data source is listed with essential metadata, such as the time range and resolution of the available data, as well as licensing and usage terms.

- [Interactive map](https://open-energy-transition.github.io/Awesome-Electricity-Demand/) with links to the data sources.
- The whole list as [CSV](https://open-energy-transition.github.io/Awesome-Electricity-Demand/sources.csv) or [JSON](https://open-energy-transition.github.io/Awesome-Electricity-Demand/sources.json).

Python code for downloading, extracting, and processing the available data can be found in our companion repository: [DemandCast](https://github.com/open-energy-transition/demandcast).

### Data Overview

The map shows each country and subdivision of the list, coloured by its years of data from all sources.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://open-energy-transition.github.io/Awesome-Electricity-Demand/figures/map_dark.png">
  <img src="https://open-energy-transition.github.io/Awesome-Electricity-Demand/figures/map_light.png" alt="World map of the countries and subdivisions with demand data, coloured by their years of data" width="100%">
</picture>

The years of data of each continent, by time resolution:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://open-energy-transition.github.io/Awesome-Electricity-Demand/figures/years_by_continent_dark.png">
  <img src="https://open-energy-transition.github.io/Awesome-Electricity-Demand/figures/years_by_continent_light.png" alt="Horizontal bars of the years of demand data of each continent, stacked by time resolution" width="100%">
</picture>

The share of the countries of each continent with data, and of their population and land area:

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://open-energy-transition.github.io/Awesome-Electricity-Demand/figures/coverage_by_continent_dark.png">
  <img src="https://open-energy-transition.github.io/Awesome-Electricity-Demand/figures/coverage_by_continent_light.png" alt="Dot plot of the share of countries, people and land of each continent with demand data" width="100%">
</picture>

The figures are rebuilt from the list every time it changes, and every month.

## Contributions

Contributions are welcome in the form of new links to websites that provide hourly or sub-hourly electricity demand data, including information on data availability timelines and licensing conditions.

- Use [GitHub Issues](https://github.com/open-energy-transition/Awesome-Electricity-Demand/issues) for data requests or suggestions.
- Submit [Pull Requests](https://github.com/open-energy-transition/Awesome-Electricity-Demand/pulls) for adding new data sources or enhancing metadata.

The list below is generated from the files in [`data/`](data/): do not edit it directly, but add or change the data source in `data/sources/<source>.yaml`. See [CONTRIBUTING.md](CONTRIBUTING.md) for how.

## List of data sources

<!-- sources:start: generated from data/ by scripts/build.py, do not edit -->
<sub>🟢 open · 🟡 non-commercial · 🔴 restricted [terms](CONTRIBUTING.md#terms-of-use) · 🔒 access on request · ✅ retrieved by [DemandCast](https://github.com/open-energy-transition/demandcast)</sub>

### Africa

<details open><summary>3 countries · 3 time series</summary>

| Country | Area | Source | Years | Resolution | Terms | DemandCast |
| --- | --- | --- | --- | --- | --- | :-: |
| **Algeria** | National | [Sonelgaz](https://data.mendeley.com/datasets/z5x2d3mhw7/1) | 2008-2020 | hourly | 🟢 [CC BY 4.0](https://data.mendeley.com/datasets/z5x2d3mhw7/1) | ✅ |
| **Nigeria** | National | [Mendeley](https://data.mendeley.com/datasets/pxvdm26rn7/2)<br><sub>Reconstructed demand without power outages</sub> | 2016 | hourly | 🟢 [CC BY 4.0](https://data.mendeley.com/datasets/pxvdm26rn7/2) | ✅ |
| **South Africa** | National | [ESKOM](https://www.eskom.co.za/dataportal/data-request-form/) | 2021-present | hourly | 🟡 [Non-commercial use](https://www.eskom.co.za/wp-content/uploads/2021/10/WEBSITE-TERMS-AND-CONDITIONS_Sep2021.pdf) 🔒 | ✅ |

</details>

### Asia

<details open><summary>14 countries · 90 time series</summary>

| Country | Area | Source | Years | Resolution | Terms | DemandCast |
| --- | --- | --- | --- | --- | --- | :-: |
| **Bangladesh** | National | [PGCB](https://erp.powergrid.gov.bd/w/report/eyJpdiI6IldsU2ZQTGkvbkRnQU9FMjZ5UHhmeGc9PSIsInZhbHVlIjoiQzhONVl5ZGxRY3E3T3ZVNCtLZGt1Zz09IiwibWFjIjoiN2JiNTI5MzNhOWIxZDVjY2NkMmFlZWU4ZDU1N2I4OWZlYjNlZWM1ZGU4NzRiNWU4ZjQ3ZDc1ODRlMTk3MDc0YyIsInRhZyI6IiJ9/show_report) | 2014-present | 30 min | 🔴 [Personal use](https://web.archive.org/web/20260713163535/https://pgcb.gov.bd/pages/static-pages/%E0%A6%AC%E0%A7%8D%E0%A6%AF%E0%A6%AC%E0%A6%B9%E0%A6%BE%E0%A6%B0%E0%A7%87%E0%A6%B0-%E0%A6%B6%E0%A6%B0%E0%A7%8D%E0%A6%A4%E0%A6%BE%E0%A6%AC%E0%A6%B2%E0%A7%80-qe03sl-697704dab42ad83461b56617) | ✅ |
| **China** | National | [Zenodo](https://zenodo.org/records/8322210)<br><sub>Modelled from the highest and lowest load of each day</sub> | 2018 | hourly | 🟢 [CC BY 4.0](https://zenodo.org/records/8322210) |  |
|  | <details><summary>31 subdivisions</summary>Anhui, Beijing, Chongqing, Fujian, Gansu, Guangdong, Guangxi, Guizhou, Hainan, Hebei, Heilongjiang, Henan, Hubei, Hunan, Inner Mongolia, Jiangsu, Jiangxi, Jilin, Liaoning, Ningxia, Qinghai, Shaanxi, Shandong, Shanghai, Shanxi, Sichuan, Tianjin, Tibet, Xinjiang, Yunnan, Zhejiang</details> | [Zenodo](https://zenodo.org/records/8322210)<br><sub>Modelled from the highest and lowest load of each day</sub> | 2018 | hourly | 🟢 [CC BY 4.0](https://zenodo.org/records/8322210) | ✅ |
| **India** | National | [NITI](https://iced.niti.gov.in/energy/electricity/distribution/national-level-consumption/load-curve) | 2017-2024 | 30 min | 🔴 [Use with authorisation](https://www.niti.gov.in/website-policy) |  |
|  | <details><summary>32 subdivisions</summary>Andhra Pradesh, Arunachal Pradesh, Assam, Bihar, Chandigarh, Chhattisgarh, Dadra and Nagar Haveli and Daman and Diu, Delhi, Goa, Gujarat, Haryana, Himachal Pradesh, Jammu and Kashmir and Ladakh, Jharkhand and West Bengal, Karnataka, Kerala, Madhya Pradesh, Maharashtra, Manipur, Meghalaya, Mizoram, Nagaland, Odisha, Puducherry, Punjab, Rajasthan, Sikkim, Tamil Nadu, Telangana, Tripura, Uttar Pradesh, Uttarakhand</details> | [NITI](https://iced.niti.gov.in/energy/electricity/distribution/national-level-consumption/load-curve) | 2017-2026 | hourly | 🔴 [Use with authorisation](https://www.niti.gov.in/website-policy) | ✅ |
| **Japan** | <details><summary>10 subdivisions</summary>Chūbu, Chūgoku, Hokkaidō, Hokuriku, Kansai, Kantō, Kyūshū, Okinawa, Shikoku, Tōhoku</details> | [OCCTO](https://occtonet3.occto.or.jp/public/dfw/RP11/OCCTO/SD/LOGIN_login) | 2016-present | hourly | 🟢 [Any use with attribution](https://www.occto.or.jp/chosakuken.html) | ✅ |
|  | Kansai | [KANSAI](https://www.kansai-td.co.jp/english/home/denkiyoho/area-performance/past.html#:~:text=Financial%20) | 2016-present | hourly | 🔴 [Personal use](https://www.kansai-td.co.jp/english/siteinfo/) | ✅ |
|  | Kantō | [TEPCO](https://www.tepco.co.jp/en/forecast/html/download-e.html) | 2016-2021 | hourly | 🔴 [Personal use](https://www4.tepco.co.jp/en/pg/legal/index-e.html) | ✅ |
|  | Kantō | [TEPCO](https://www.tepco.co.jp/en/forecast/html/download-e.html) | 2022-present | 5 min | 🔴 [Personal use](https://www4.tepco.co.jp/en/pg/legal/index-e.html) | ✅ |
| **Malaysia** | National | [GSO](https://www.gso.org.my/SystemData/SystemDemand.aspx)<br><sub>Peninsular Malaysia only, without Sabah and Sarawak</sub> | 2016-present | 10 min | 🔴 [Use with authorisation](https://www.gso.org.my/TermsConditions.aspx) |  |
| **Nepal** | National | [Open Data Nepal](https://opendatanepal.com/dataset/electricity-load-profile-of-nepal-in-2073-nepal-electricity-authority) | 2017-2018 | hourly | 🟢 [CC BY 4.0](https://opendatanepal.com/dataset/electricity-load-profile-of-nepal-in-2073-nepal-electricity-authority) | ✅ |
| **Pakistan** | National | [NTDC](https://zenodo.org/records/24023127)<br><sub>Copy on Zenodo of the dataset removed from Kaggle in 2026</sub> | 2015-2020 | hourly | 🟢 [CC0 1.0](https://zenodo.org/records/24023127) | ✅ |
|  | National | [ISMO](https://www.ismo.gov.pk/library/hourly-system-demand)<br><sub>Without K-Electric, which supplies Karachi</sub> | 2024-2025 | hourly | 🔴 [Personal use](https://www.ismo.gov.pk/terms-and-conditions) | ✅ |
| **Philippines** | National | [NGCP](https://www.ngcp.ph/operations#operations) | 2013-2025 | hourly | 🔴 [Use with authorisation](https://ngcp.ph) | ✅ |
| **Singapore** | National | [EMA](https://www.ema.gov.sg/resources/statistics/half-hourly-system-demand-data) | 2014-present | 30 min | 🟢 [Any use with attribution](https://www.ema.gov.sg/terms-of-use) | ✅ |
| **South Korea** | National | [KROGD](https://www.data.go.kr/data/15065266/fileData.do) | 2013-2025 | hourly | 🟢 [Any use](https://www.data.go.kr/data/15065266/fileData.do) | ✅ |
| **Sri Lanka** | National | [PUCSL](https://gendata.pucsl.gov.lk/generation-profile)<br><sub>Generation, proxy for demand</sub> | 2023-present | 15 min | 🔴 [Use with authorisation](https://www.pucsl.gov.lk/) | ✅ |
| **Taiwan** | National | [Zenodo](https://zenodo.org/records/7537890) | 2017-2022 | 10 min | 🟢 [CC BY 4.0](https://zenodo.org/records/7537890) | ✅ |
| **Thailand** | National | [Zenodo](https://doi.org/10.5281/zenodo.17109911) | 2023-2024 | hourly | 🟢 [CC BY 4.0](https://zenodo.org/records/17109911) | ✅ |
| **Turkey** | National | [EPIAS](https://kayit.epias.com.tr/epias-transparency-platform-registration-form) | 2016-present | hourly | 🟢 [Any use with attribution](https://seffaflik.epias.com.tr/about/about) 🔒 | ✅ |

</details>

### Europe

<details open><summary>38 countries · 48 time series</summary>

| Country | Area | Source | Years | Resolution | Terms | DemandCast |
| --- | --- | --- | --- | --- | --- | :-: |
| **Albania** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-2016 | 15 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
|  | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2021-present | 15 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Austria** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | 15 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Belgium** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2014-present | 15 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Bosnia and Herzegovina** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2017-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Bulgaria** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Croatia** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Cyprus** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2016-2022 | 30 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
|  | National | [TSOC](https://tsoc.org.cy/electrical-system/archive-total-daily-system-generation-on-the-transmission-system/)<br><sub>Generation, proxy for demand</sub> | 2018-present | 15 min | 🔴 [Use with authorisation](https://tsoc.org.cy/) | ✅ |
|  | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2024-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Czech Republic** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Denmark** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
|  | National | [Energi Data Service](https://www.energidataservice.dk/search/consumption)<br><sub>By grid area, region and consumer category, industry, and household heating</sub> | 2021-present | hourly | 🟢 [CC BY 4.0](https://www.energidataservice.dk/terms-and-conditions) |  |
|  | <details><summary>2 subdivisions</summary>Eastern Denmark, Western Denmark</details> | [Energi Data Service](https://www.energidataservice.dk/tso-electricity/ProductionConsumptionSettlement)<br><sub>Gross consumption with grid losses, from settlement data</sub> | 2005-present | hourly | 🟢 [CC BY 4.0](https://www.energidataservice.dk/terms-and-conditions) |  |
|  | <details><summary>2 subdivisions</summary>Eastern Denmark, Western Denmark</details> | [Energi Data Service](https://www.energidataservice.dk/tso-electricity/GenerationProdTypeExchange)<br><sub>Gross consumption, near real time</sub> | 2015-present | hourly | 🟢 [CC BY 4.0](https://www.energidataservice.dk/terms-and-conditions) |  |
| **Estonia** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Finland** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **France** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Georgia** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2022-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Germany** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | 15 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Greece** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Hungary** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | 15 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Ireland** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | 30 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Italy** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Kosovo** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2021-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Latvia** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Lithuania** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Luxembourg** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | 15 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Moldova** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2020-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Montenegro** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Netherlands** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2014-present | 15 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **North Macedonia** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Norway** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Poland** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Portugal** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Romania** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Serbia** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Slovakia** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Slovenia** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Spain** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Sweden** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Switzerland** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2014-present | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **Ukraine** | National | [ENTSO-E](https://transparency.entsoe.eu/) | 2017-2022 | hourly | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
| **United Kingdom** | Great Britain | [NESO](https://www.neso.energy/data-portal/historic-demand-data) | 2001-present | 30 min | 🟢 [Any use with attribution](https://www.neso.energy/data-portal/neso-open-licence) | ✅ |
|  | Great Britain | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-2021 | 30 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |
|  | Northern Ireland | [ENTSO-E](https://transparency.entsoe.eu/) | 2015-2025 | 30 min | 🔴 [Use with authorisation](https://transparencyplatform.zendesk.com/hc/en-us/articles/40921911218961-Legal-Terms-and-Conditions) | ✅ |

</details>

### North America

<details open><summary>5 countries · 57 time series</summary>

| Country | Area | Source | Years | Resolution | Terms | DemandCast |
| --- | --- | --- | --- | --- | --- | :-: |
| **Canada** | Alberta | [AESO](https://www.aeso.ca/market/market-and-system-reporting/data-requests/hourly-generation-metered-volumes-and-pool-price-and-ail-data-2001-to-july-2025/)<br><sub>Alberta Internal Load (AIL), with the load behind the fence of industrial sites</sub> | 2001-2025 | hourly | 🟡 [Non-commercial use with attribution](https://www.aeso.ca/legal) | ✅ |
|  | Alberta | [AESO](https://www.aeso.ca/market/market-and-system-reporting/data-requests/hourly-load-by-area-and-region) | 2011-2024 | hourly | 🟡 [Non-commercial use with attribution](https://www.aeso.ca/legal) | ✅ |
|  | Alberta | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2023-present | 5 min | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | British Columbia | [BCHYDRO](https://www.bchydro.com/energy-in-bc/operations/transmission/transmission-system/balancing-authority-load-data/historical-transmission-data.html) | 2001-present | hourly | 🔴 [Use with authorisation](https://www.bchydro.com/siteinfo/legal.html) | ✅ |
|  | British Columbia | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2001-2024 | hourly | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) |  |
|  | New Brunswick | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2016-2021 | hourly | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | New Brunswick | [NBPOWER](https://tso.nbpower.com/Public/en/system_information_archive.aspx) | 2018-present | hourly | 🔴 [Use with authorisation](https://www.nbpower.com/en/terms-of-use) | ✅ |
|  | New Brunswick | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2021-present | 5 min | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | Newfoundland and Labrador | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2022-present | 5 min | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | Nova Scotia | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2022-2023 | 5 min | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | Nova Scotia | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2024-present | 10 min | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | Ontario | [IESO](https://www.ieso.ca/Power-Data/Data-Directory) | 1994-present | hourly | 🔴 [Any use with attribution, no redistribution](https://www.ieso.ca/Terms-of-Use) | ✅ |
|  | Ontario | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2002-present | hourly | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | Prince Edward Island | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2012-present | 15 min | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | Quebec | [HYDROQUEBEC](https://donnees.hydroquebec.com/explore/dataset/historique-demande-electricite-quebec/information/) | 2019-2025 | hourly | 🟡 [CC BY-NC 4.0](https://donnees.hydroquebec.com/explore/dataset/historique-demande-electricite-quebec/information/) | ✅ |
|  | Quebec | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2021-present | 15 min | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
|  | Yukon | [CCEI](https://energy-information.canada.ca/en/resources/high-frequency-electricity-data)<br><sub>Collected from the provincial or territorial utility, whose terms also apply</sub> | 2024-present | 5 min | 🟡 [Non-commercial use with attribution](https://www.canada.ca/en/transparency/terms.html) | ✅ |
| **Costa Rica** | National | [GrupoICE](https://apps.grupoice.com/CenceWeb) | 2012-present | 15 min | 🟢 [CC BY-SA 4.0](https://web.archive.org/web/20250207024012/https://www.grupoice.com/wps/portal/ICE/Transparencia/datos-abiertos) | ✅ |
| **Mexico** | <details><summary>9 subdivisions</summary>Baja California, Baja California Sur, Central, Noreste, Noroeste, Norte, Occidental, Oriental, Peninsular</details> | [CENACE](https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx) | 2016-present | hourly | 🔴 [Personal use](https://www.gob.mx/terminos) | ✅ |
| **Panama** | National | [Mendeley](https://data.mendeley.com/datasets/tcmmj4t6f4/1) | 2016-2020 | hourly | 🟢 [CC BY 4.0](https://data.mendeley.com/datasets/tcmmj4t6f4/1) | ✅ |
| **United States** | <details><summary>13 subdivisions</summary>California, Carolinas, Central, Florida, Mid-Atlantic, Midwest, New England, New York, Northwest, Southeast, Southwest, Tennessee, Texas</details> | [EIA (Ruggles et al.)](https://github.com/truggles/EIA_Cleaned_Hourly_Electricity_Demand_Data) | 2015-2020 | hourly | 🟢 [CC BY 4.0](https://github.com/truggles/EIA_Cleaned_Hourly_Electricity_Demand_Data) |  |
|  | California | [CAISO](https://www.caiso.com/library/historical-ems-hourly-load) | 2019-present | hourly | 🟢 [Any use with attribution](https://www.caiso.com/privacy-terms-of-use) | ✅ |
|  | <details><summary>13 subdivisions</summary>California, Carolinas, Central, Florida, Mid-Atlantic, Midwest, New England, New York, Northwest, Southeast, Southwest, Tennessee, Texas</details> | [EIA](https://www.eia.gov/electricity/gridmonitor/) | 2020-present | hourly | 🟢 [Any use](https://www.eia.gov/about/copyrights_reuse.php) | ✅ |
|  | New England | [ISO-NE](https://webservices.iso-ne.com/docs/v1.1/) | 2019-present | hourly | 🔴 [Personal use](https://www.iso-ne.com/legal-privacy) 🔒 | ✅ |
|  | Texas | [ERCOT](https://www.ercot.com/gridinfo/load/load_hist)<br><sub>By weather zone from 2002, by control area before; no data for 2001</sub> | 1995-present | hourly | 🟢 [Any use](https://www.ercot.com/help/terms) |  |

</details>

### South America

<details open><summary>6 countries · 33 time series</summary>

| Country | Area | Source | Years | Resolution | Terms | DemandCast |
| --- | --- | --- | --- | --- | --- | :-: |
| **Argentina** | National | [Cammesa](https://cammesaweb.cammesa.com/) | 2024-present | hourly | 🔴 [Use with authorisation](https://cammesaweb.cammesa.com/politicas-de-acceso/) |  |
|  | <details><summary>22 subdivisions</summary>Buenos Aires and Ciudad Autónoma de Buenos Aires, Catamarca, Chaco, Chubut, Corrientes, Córdoba, Entre Ríos, Formosa, Jujuy, La Pampa, La Rioja, Mendoza, Misiones, Neuquén, Río Negro, Salta, San Juan, San Luis, Santa Cruz, Santa Fe, Santiago del Estero, Tucumán</details> | [Cammesa](https://cammesaweb.cammesa.com/)<br><sub>The API keeps only about the last 7 to 8 months</sub> | 2026-present | 5 min | 🔴 [Use with authorisation](https://cammesaweb.cammesa.com/politicas-de-acceso/) | ✅ |
| **Brazil** | National | [ONS](https://dados.ons.org.br/dataset/curva-carga) | 2000-present | hourly | 🟢 [CC BY](https://dados.ons.org.br/dataset/curva-carga) |  |
|  | <details><summary>4 subdivisions</summary>North, North-East, South, South-East</details> | [ONS](https://dados.ons.org.br/dataset/curva-carga) | 2000-present | hourly | 🟢 [CC BY](https://dados.ons.org.br/dataset/curva-carga) | ✅ |
| **Chile** | National | [CEN](https://www.coordinador.cl/operacion/graficos/operacion-real/demanda-real/)<br><sub>Until 2015, the central system (SIC) only, about 30% less. The API of the page has no data after 13 May 2026</sub> | 1999-2026 | hourly | 🟡 [Personal or academic use with attribution](https://www.coordinador.cl/terminos-y-condiciones/) | ✅ |
|  | National | [CEN (Qlik app)](https://qap-prd.coordinador.cl/ext/extensions/mashup_demanda_real/mashup_demanda_real.html)<br><sub>Only the last three months or so, each month published from the 20th of the next</sub> | 2026-present | hourly | 🟡 [Personal or academic use with attribution](https://www.coordinador.cl/terminos-y-condiciones/) |  |
| **Colombia** | National | [XM](https://www.energiadecolombia.com/consulta) | 2000-present | hourly | 🔴 [Use with authorisation](https://www.xm.com.co/legales/terminos-legales-del-sitio-web) | ✅ |
| **Peru** | National | [COES](https://www.coes.org.pe/Portal/portalinformacion/demanda)<br><sub>Until 1999, hourly values about 20% lower</sub> | 1997-present | 30 min | 🔴 [Personal use](https://www.coes.org.pe/Portal/Organizacion/TerminosyCondiciones) | ✅ |
| **Uruguay** | National | [ADME](https://adme.com.uy/controlpanel.php) | 2019-present | hourly | 🟢 [Any use with attribution](https://www.gub.uy/agencia-gobierno-electronico-sociedad-informacion-conocimiento/sites/agencia-gobierno-electronico-sociedad-informacion-conocimiento/files/documentos/publicaciones/licencia_de_datos_abiertos_0.pdf) | ✅ |

</details>

### Oceania

<details open><summary>2 countries · 13 time series</summary>

| Country | Area | Source | Years | Resolution | Terms | DemandCast |
| --- | --- | --- | --- | --- | --- | :-: |
| **Australia** | <details><summary>4 subdivisions</summary>New South Wales, Queensland, South Australia, Victoria</details> | [AEMO](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/aggregated-data) | 1998-2021 | 30 min | 🟢 [Any use with attribution](https://aemo.com.au/privacy-and-legal-notices/copyright-permissions) | ✅ |
|  | <details><summary>5 subdivisions</summary>New South Wales, Queensland, South Australia, Tasmania, Victoria</details> | [AEMO](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/aggregated-data) | 2021-present | 5 min | 🟢 [Any use with attribution](https://aemo.com.au/privacy-and-legal-notices/copyright-permissions) | ✅ |
|  | Tasmania | [AEMO](https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/aggregated-data) | 2005-2021 | 30 min | 🟢 [Any use with attribution](https://aemo.com.au/privacy-and-legal-notices/copyright-permissions) | ✅ |
|  | Western Australia | [AEMO](https://data.wa.aemo.com.au/datafiles/operational-demand/) | 2006-2023 | 30 min | 🟢 [Any use with attribution](https://aemo.com.au/privacy-and-legal-notices/copyright-permissions) | ✅ |
|  | Western Australia | [AEMO](https://data.wa.aemo.com.au/public/market-data/wemde/operationalDemandWithdrawal/dailyFiles/) | 2023-present | 5 min | 🟢 [Any use with attribution](https://aemo.com.au/privacy-and-legal-notices/copyright-permissions) | ✅ |
| **New Zealand** | National | [EMI](https://www.emi.ea.govt.nz/Wholesale/Reports/W_GD_C) | 2005-present | 30 min | 🟢 [CC BY 4.0](https://www.emi.ea.govt.nz/LegalInformation) | ✅ |

</details>
<!-- sources:end -->
