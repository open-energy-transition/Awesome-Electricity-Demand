// Map of the countries with electricity demand data. Each country is
// coloured by its years of data, read from sources.json, and a click on
// it opens a popup with its data sources. The country shapes come from
// world.geo.json, whose features are identified by ISO 3166-1 alpha-3
// codes.

const COUNTRY_SHAPES =
  "https://raw.githubusercontent.com/johan/world.geo.json/34c96bba9c07d2ceb30696c599bb51a5b939b20f/countries.geo.json";

// Codes of the shapes that differ from the codes of the list.
const SHAPE_CODES = { "CS-KM": "XKX" };

const NO_DATA = "#e0e0e0";

function colour(country) {
  if (!country || country.years === 0) return NO_DATA;
  if (country.years < 5) return "#b2d8b2";
  if (country.years < 10) return "#67b367";
  if (country.years < 20) return "#267326";
  return "#0d400d";
}

function element(tag, text) {
  const node = document.createElement(tag);
  if (text) node.textContent = text;
  return node;
}

function link(text, url) {
  const node = element("a", text);
  node.href = url;
  node.target = "_blank";
  node.rel = "noopener";
  return node;
}

function popupContent(country) {
  const content = element("div");
  content.append(element("h4", country.name));
  if (country.series.length === 0) {
    content.append(element("p", "No data in the list yet."));
    return content;
  }
  const list = element("ul");
  for (const source of country.series) {
    const item = element("li");
    if (source.subdivision_name) {
      item.append(element("strong", `${source.subdivision_name}: `));
    }
    item.append(link(source.source_name, source.url));
    const end = source.end === source.start ? "" : `-${source.end}`;
    item.append(
      ` · ${source.start}${end} · ${source.resolution_minutes} min · `,
    );
    item.append(link(source.licence_name, source.licence_url));
    if (source.access === "on-request") item.append(" · access on request");
    if (source.note) item.append(` · ${source.note}`);
    if (source.demandcast) item.append(" · retrieved by DemandCast");
    list.append(item);
  }
  content.append(list);
  return content;
}

const map = new maplibregl.Map({
  container: "map",
  style: "https://demotiles.maplibre.org/style.json",
  center: [12, 44],
  zoom: 1.5,
  minZoom: 1.27,
  maxZoom: 6,
});

map.on("load", async () => {
  const [list, shapes] = await Promise.all([
    fetch("sources.json").then((response) => response.json()),
    fetch(COUNTRY_SHAPES).then((response) => response.json()),
  ]);
  for (const feature of shapes.features) {
    const code = SHAPE_CODES[feature.id] ?? feature.id;
    const country = list.countries[code];
    feature.properties.code = code;
    feature.properties.colour = colour(country);
  }

  map.addSource("countries", { type: "geojson", data: shapes });
  map.addLayer({
    id: "country-fills",
    type: "fill",
    source: "countries",
    paint: { "fill-color": ["get", "colour"], "fill-opacity": 1.0 },
  });
  map.addLayer({
    id: "country-borders",
    type: "line",
    source: "countries",
    paint: { "line-color": "#000", "line-width": 1 },
  });

  map.on("click", "country-fills", (event) => {
    const feature = event.features[0];
    const country = list.countries[feature.properties.code] ?? {
      name: feature.properties.name,
      series: [],
    };
    new maplibregl.Popup({ maxWidth: "420px" })
      .setLngLat(event.lngLat)
      .setDOMContent(popupContent(country))
      .addTo(map);
  });
  map.on("mouseenter", "country-fills", () => {
    map.getCanvas().style.cursor = "pointer";
  });
  map.on("mouseleave", "country-fills", () => {
    map.getCanvas().style.cursor = "";
  });
});
