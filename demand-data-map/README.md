This folder contains a map made with [MapLibre](https://maplibre.org/), hosted with GitHub Pages [here](https://open-energy-transition.github.io/Awesome-Electricity-Demand/). Click on a country to see its data sources.

The map reads `sources.json`, which `scripts/build.py site` generates from the data files next to these files. To see it locally, build the site and serve it:

```bash
uv run scripts/build.py site _site
python -m http.server --directory _site
```
