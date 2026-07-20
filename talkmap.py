# Leaflet cluster map of talk locations
#
# Run this from the _talks/ directory, which contains .md files of all your
# talks. This scrapes the location YAML field from each .md file, geolocates it
# with geopy/Nominatim, and uses the getorg library to output data, HTML, and
# Javascript for a standalone cluster map. This is functionally the same as the
# #talkmap Jupyter notebook.
#
# Career/training stages that aren't covered by any talk (e.g. where I
# trained or worked but never gave a talk there) live in _data/career.yml and
# are geocoded and pinned the same way.
import frontmatter
import glob
import yaml
import getorg
from geopy import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Institutions worked at get a yellow pin instead of the default blue one.
INSTITUTION_KEYWORDS = [
    "Université de Bordeaux",
    "University of Florida",
    "University of Illinois at Urbana-Champaign",
    "Swansea University",
    "Manchester Institute of Biotechnology",
    "Manchester Metropolitan University",
]

# Collect the Markdown files
g = glob.glob("_talks/*.md")

# Prepare to geolocate. Nominatim's usage policy caps requests at 1/second, so
# space requests out and retry on the 429s that a bare geocode() loop hits.
geocoder = Nominatim(user_agent="academicpages.github.io", timeout=10)
geocode = RateLimiter(geocoder.geocode, min_delay_seconds=1.5, max_retries=5, error_wait_seconds=5.0)
location_dict = {}

# Perform geolocation for talks
for file in sorted(g):
    # Read the file
    data = frontmatter.load(file)
    data = data.to_dict()

    # Press on if the location is not present
    if 'location' not in data:
        continue

    # Prepare the description
    title = data['title'].strip()
    venue = data['venue'].strip()
    location = data['location'].strip()
    year = data['date'].year
    description = f"{title}<br />{venue}; {location} ({year})"

    # Geocode the location and report the status
    try:
        location_dict[description] = geocode(location)
        print(description, location_dict[description])
    except Exception as ex:
        print(f"An unhandled exception occurred while processing input {location} with message {ex}")

# Perform geolocation for career/training stages not covered by a talk
with open("_data/career.yml") as f:
    career = yaml.safe_load(f)

for entry in career:
    title = entry['title'].strip()
    venue = entry['venue'].strip()
    location = entry['location'].strip()
    description = f"{title}<br />{venue}; {location} ({entry['start_year']}–{entry['end_year']})"

    try:
        location_dict[description] = geocode(location)
        print(description, location_dict[description])
    except Exception as ex:
        print(f"An unhandled exception occurred while processing input {location} with message {ex}")

# Save the map
m = getorg.orgmap.create_map_obj()
getorg.orgmap.output_html_cluster_map(location_dict, folder_name="talkmap", hashed_usernames=False)

# getorg's own map.html template doesn't know about institution highlighting,
# doesn't style the Leaflet attribution control to match this site's font,
# and its instructional <span> doesn't match this site's fonts either.
# Rewrite the generated map.html with our own fixed template instead of
# hand-patching getorg's output, so every regeneration (including CI)
# produces the same result regardless of what getorg's template looks like.
MAP_HTML = """
    <!DOCTYPE html>
    <html>
    <head>
    	<meta charset="utf-8" />
    	<title>Leaflet debug page</title>

    	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0-beta.2/leaflet.css" />
    	<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.0.0-beta.2/leaflet.js"></script>
    	<meta name="viewport" content="width=device-width, initial-scale=1.0">
    	<link rel="stylesheet" href="leaflet_dist/screen.css" />

    	<link rel="stylesheet" href="leaflet_dist/MarkerCluster.css" />
    	<link rel="stylesheet" href="leaflet_dist/MarkerCluster.Default.css" />
    	<script src="leaflet_dist/leaflet.markercluster-src.js"></script>
    	<script src="org-locations.js"></script>
    	<style>
    		body, .leaflet-container {
    			font-family: -apple-system, BlinkMacSystemFont, 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    		}
    	</style>

    </head>
    <body>

    	<div id="map"></div>
    	<script type="text/javascript">
    		var tiles = L.tileLayer('http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
              maxZoom: 18,
              attribution: 'Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012'
                    }),
    			latlng = L.latLng(30, 10);
    		var map = L.map('map', {center: latlng, zoom: 0.7, layers: [tiles]});
    		var markers = L.markerClusterGroup({
    			showCoverageOnHover: false,
    			// maxClusterRadius is normally a fixed pixel radius, which groups
    			// wildly different real-world distances depending on zoom level.
    			// Use a distance-based radius instead so only talks that are
    			// genuinely close together (~200m) ever cluster, at any zoom.
    			maxClusterRadius: function (zoom) {
    				var desiredMeters = 200;
    				var metersPerPixel = 156543.03392 / Math.pow(2, zoom);
    				return desiredMeters / metersPerPixel;
    			}
    			});

    		// Institutions worked at get a yellow pin instead of the default blue one.
    		var institutionKeywords = %(institution_keywords)s;
    		var institutionIcon = L.divIcon({
    			className: 'institution-marker',
    			html: '<svg width="25" height="41" viewBox="0 0 25 41" xmlns="http://www.w3.org/2000/svg">' +
    				'<path d="M12.5 0C5.6 0 0 5.6 0 12.5c0 9.4 12.5 28.5 12.5 28.5S25 21.9 25 12.5C25 5.6 19.4 0 12.5 0z" fill="#FFC107" stroke="#8a6d00" stroke-width="1"/>' +
    				'<circle cx="12.5" cy="12.5" r="5" fill="#ffffff"/></svg>',
    			iconSize: [25, 41],
    			iconAnchor: [12, 41],
    			popupAnchor: [1, -34]
    		});

    		for (var i = 0; i < addressPoints.length; i++) {
    			var a = addressPoints[i];
    			var title = a[0];
    			var isInstitution = institutionKeywords.some(function (keyword) {
    				return title.indexOf(keyword) !== -1;
    			});
    			var markerOptions = { title: title };
    			if (isInstitution) {
    				markerOptions.icon = institutionIcon;
    			}
    			var marker = L.marker(new L.LatLng(a[1], a[2]), markerOptions);
    			marker.bindPopup(title);
    			markers.addLayer(marker);
    		}
    		map.addLayer(markers);
    		map.zoomIn();
    	</script>
    </body>
    </html>
    """

keywords_js = "[\n" + ",\n".join(f"\t\t\t'{kw}'" for kw in INSTITUTION_KEYWORDS) + "\n\t\t]"
with open("talkmap/map.html", "w") as f:
    f.write(MAP_HTML % {"institution_keywords": keywords_js})
