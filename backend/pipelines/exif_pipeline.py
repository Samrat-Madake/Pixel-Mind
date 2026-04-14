from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import reverse_geocoder as rg
from pathlib import Path
from datetime import datetime

class EXIFPipeline:
    def extract(self, image_path: str) -> dict:
        """Extract EXIF metadata + offline reverse geocoding."""
        metadata = {
            "shot_date": None,
            "lat": None,
            "lon": None,
            "camera_make": None,
            "camera_model": None,
            "location": None
        }
        
        try:
            img = Image.open(image_path)
            exif = img._getexif()
            
            if not exif:
                return metadata
            
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                
                if decoded == "DateTimeOriginal":
                    metadata["shot_date"] = value
                elif decoded == "Make":
                    metadata["camera_make"] = str(value).strip()
                elif decoded == "Model":
                    metadata["camera_model"] = str(value).strip()
                elif decoded == "GPSInfo":
                    gps_data = {}
                    for t in value:
                        sub_tag = GPSTAGS.get(t, t)
                        gps_data[sub_tag] = value[t]
                    
                    lat_lon = self._get_lat_lon(gps_data)
                    if lat_lon:
                        metadata["lat"], metadata["lon"] = lat_lon
                        metadata["location"] = self._reverse_geocode(lat_lon[0], lat_lon[1])
        except Exception as e:
            print(f"EXIF Extraction Error for {image_path}: {e}")
            
        return metadata

    def _get_lat_lon(self, gps_info):
        """Convert GPS EXIF to decimal lat/lon."""
        def _to_degrees(value):
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)

        try:
            lat = _to_degrees(gps_info["GPSLatitude"])
            if gps_info["GPSLatitudeRef"] != "N":
                lat = -lat
            
            lon = _to_degrees(gps_info["GPSLongitude"])
            if gps_info["GPSLongitudeRef"] != "E":
                lon = -lon
                
            return lat, lon
        except:
            return None

    def _reverse_geocode(self, lat, lon):
        """Offline reverse geocoding using reverse_geocoder."""
        try:
            # rg.search returns a list of result dicts
            result = rg.search((lat, lon))[0]
            return f"{result['name']}, {result['admin1']}, {result['cc']}"
        except:
            return None

# Global instance
exif_pipeline = EXIFPipeline()
