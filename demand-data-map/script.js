// Create the Map
const map = new maplibregl.Map({
  container: "map",
  style: "https://demotiles.maplibre.org/style.json", // Default MapLibre style
  center: [12, 44], // [Longitude, Latitude]
  zoom: 1.5,
  pitch: 0,
  bearing: 0,
  antialias: true,
});

// Sample demand data with country colors and links
const countryData = {
  Albania: {
    color: "#B2D8B2",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YAL-KESH-----5!CTY|10YAL-KESH-----5&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Austria: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YAT-APG------L!CTY|10YAT-APG------L&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Belgium: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YBE----------2!CTY|10YBE----------2&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  "Bosnia and Herzegovina": {
    color: "#67B367",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YBA-JPCC-----D!CTY|10YBA-JPCC-----D&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Bulgaria: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YCA-BULGARIA-R!CTY|10YCA-BULGARIA-R&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Croatia: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YHR-HEP------M!CTY|10YHR-HEP------M&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Cyprus: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YCY-1001A0003J!CTY|10YCY-1001A0003J&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  "Czech Republic": {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YCZ-CEPS-----N!CTY|10YCZ-CEPS-----N&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Denmark: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A65H!CTY|10Y1001A1001A65H&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Estonia: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A39I!CTY|10Y1001A1001A39I&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Finland: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YFI-1--------U!CTY|10YFI-1--------U&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  France: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YFR-RTE------C!CTY|10YFR-RTE------C&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Georgia: {
    color: "#B2D8B2",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001B012!CTY|10Y1001A1001B012&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Germany: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A83F!CTY|10Y1001A1001A83F&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Greece: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YGR-HTSO-----Y!CTY|10YGR-HTSO-----Y&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Hungary: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YHU-MAVIR----U!CTY|10YHU-MAVIR----U&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Ireland: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YIE-1001A00010!CTY|10YIE-1001A00010&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Italy: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YIT-GRTN-----B!CTY|10YIT-GRTN-----B&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Kosovo: {
    color: "#B2D8B2",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10Y1001C--00100H!CTY|10Y1001C--00100H&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Latvia: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YLV-1001A00074!CTY|10YLV-1001A00074&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Lithuania: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YLT-1001A0008Q!CTY|10YLT-1001A0008Q&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Luxembourg: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YLU-CEGEDEL-NQ!CTY|10YLU-CEGEDEL-NQ&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Moldova: {
    color: "#67B367",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A990!CTY|10Y1001A1001A990&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Montenegro: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YCS-CG-TSO---S!CTY|10YCS-CG-TSO---S&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Netherlands: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YNL----------L!CTY|10YNL----------L&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Macedonia: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YMK-MEPSO----8!CTY|10YMK-MEPSO----8&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Norway: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YNO-0--------C!CTY|10YNO-0--------C&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Poland: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YPL-AREA-----S!CTY|10YPL-AREA-----S&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Portugal: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YPT-REN------W!CTY|10YPT-REN------W&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Romania: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YRO-TEL------P!CTY|10YRO-TEL------P&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  "Republic of Serbia": {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YCS-SERBIATSOV!CTY|10YCS-SERBIATSOV&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Slovakia: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YSK-SEPS-----K!CTY|10YSK-SEPS-----K&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Slovenia: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=13.03.2025+00:00|CET|DAY&biddingZone.values=CTY|10YSI-ELES-----O!CTY|10YSI-ELES-----O&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Spain: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YES-REE------0!CTY|10YES-REE------0&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Sweden: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YSE-1--------K!CTY|10YSE-1--------K&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Switzerland: {
    color: "#267326",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10YCH-SWISSGRIDZ!CTY|10YCH-SWISSGRIDZ&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Ukraine: {
    color: "#67B367",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=01.01.2022+00:00|CET|DAY&biddingZone.values=CTY|10Y1001C--00003F!CTY|10Y1001C--00003F&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  "United Kingdom": {
    color: "#67B367",
    link: "https://transparency.entsoe.eu/load-domain/r2/totalLoadR2/show?name=&defaultValue=false&viewType=TABLE&areaType=CTY&atch=false&dateTime.dateTime=14.03.2024+00:00|CET|DAY&biddingZone.values=CTY|10Y1001A1001A92E!CTY|10Y1001A1001A92E&dateTime.timezone=CET_CEST&dateTime.timezone_input=CET+(UTC+1)+/+CEST+(UTC+2) ",
  },
  Australia: {
    color: "#0D400D",
    link: "https://www.aemo.com.au/energy-systems/electricity/national-electricity-market-nem/data-nem/aggregated-data",
  },
  "New Zealand": {
    color: "#0D400D",
    link: "https://www.emi.ea.govt.nz/Wholesale/Reports/W_GD_C",
  },
  Algeria: {
    color: "#67B367",
    link: "https://data.mendeley.com/datasets/z5x2d3mhw7/1",
  },
  Nigeria: {
    color: "#B2D8B2",
    link: "https://data.mendeley.com/datasets/pxvdm26rn7/2",
  },
  "South Africa": {
    color: "#67B367",
    link: "https://www.eskom.co.za/dataportal/data-request-form/",
  },
  Japan: {
    color: "#67B367",
    link: "https://www.tepco.co.jp/en/forecast/html/download-e.html",
  },
  "Sri Lanka": {
    color: "#B2D8B2",
    link: "https://gendata.pucsl.gov.lk/generation-profile",
  },
  Turkey: {
    color: "#B2D8B2",
    link: "https://seffaflik.epias.com.tr/electricity/electricity-consumption/ex-post-consumption/real-time-consumption",
  },
  Canada: {
    color: "#B2D8B2",
    link: "https://energy-information.canada.ca/en/resources/high-frequency-electricity-data",
  },
  Argentina: { color: "#B2D8B2", link: "https://cammesaweb.cammesa.com/" },
  Brazil: {
    color: "#0D400D",
    link: "https://dados.ons.org.br/dataset/curva-carga",
  },
  Chile: {
    color: "#0D400D",
    link: "https://www.coordinador.cl/operacion/graficos/operacion-real/demanda-real/",
  },
  Peru: {
    color: "#0D400D",
    link: "https://www.coes.org.pe/Portal/portalinformacion/demanda",
  },
};

// Load country boundaries from GeoJSON
map.on("load", function () {
  fetch(
    "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
  )
    .then((response) => response.json())
    .then((data) => {
      map.addSource("countries", {
        type: "geojson",
        data: data,
      });

      map.addLayer({
        id: "country-fills",
        type: "fill",
        source: "countries",
        layout: {},
        paint: {
          "fill-color": [
            "match",
            ["get", "name"],
            ...Object.entries(countryData).flatMap(([name, info]) => [
              name,
              info.color,
            ]),
            "#AAAAAA", // Default color for unlisted countries
          ],
          "fill-opacity": 1.0,
        },
      });

      // Add country borders
      map.addLayer({
        id: "country-borders",
        type: "line",
        source: "countries",
        layout: {},
        paint: {
          "line-color": "#000",
          "line-width": 1,
        },
      });

      // Click Event for Countries
      map.on("click", "country-fills", function (e) {
        const countryName = e.features[0].properties.name;
        const countryInfo = countryData[countryName];

        if (countryInfo) {
          window.open(countryInfo.link, "_blank"); // Open demand data link
        } else {
          alert("No demand data available for " + countryName);
        }
      });

      // Change cursor on hover
      map.on("mouseenter", "country-fills", function () {
        map.getCanvas().style.cursor = "pointer";
      });

      map.on("mouseleave", "country-fills", function () {
        map.getCanvas().style.cursor = "";
      });
    });
});
