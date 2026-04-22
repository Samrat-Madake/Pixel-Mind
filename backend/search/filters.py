from backend.db.db import get_db_connection

class SQLiteFilters:
    @staticmethod
    def apply(filters: dict) -> list[int]:
        """
        Applies SQL filters and returns a list of image_ids that match.
        Supported filters: date_from, date_to, camera_make, camera_model, location
        """
        if not filters:
            return None
            
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT image_id FROM metadata WHERE 1=1"
        params = []
        
        if "date_from" in filters and filters["date_from"]:
            query += " AND shot_date >= ?"
            params.append(filters["date_from"])
            
        if "date_to" in filters and filters["date_to"]:
            query += " AND shot_date <= ?"
            params.append(filters["date_to"])
            
        if "camera_make" in filters and filters["camera_make"]:
            query += " AND camera_make LIKE ?"
            params.append(f"%{filters['camera_make']}%")
            
        if "camera_model" in filters and filters["camera_model"]:
            query += " AND camera_model LIKE ?"
            params.append(f"%{filters['camera_model']}%")
            
        if "location" in filters and filters["location"]:
            query += " AND location LIKE ?"
            params.append(f"%{filters['location']}%")
            
        cursor.execute(query, params)
        results = [row["image_id"] for row in cursor.fetchall()]
        conn.close()
        
        return results
