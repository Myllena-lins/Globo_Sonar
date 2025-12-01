class EDLRepository:

    def save_edl_record(self, db, process_id: str, edl_name: str, path: str,
                        frame_rate: float, drop_frame: bool,
                        total_events: int, validation_status: str,
                        validation_errors: list):
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO edls (process_id, edl_name, path, frame_rate, drop_frame,
                              total_events, validation_status, validation_errors, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (process_id, edl_name, path, frame_rate, int(drop_frame),
              total_events, validation_status, ",".join(validation_errors)))
        db.commit()
        return cursor.lastrowid

    def update_status(self, db, edl_id: int, validation_status: str, validation_errors: list = None):
        cursor = db.cursor()
        if validation_errors is None:
            cursor.execute("""
                UPDATE edls SET validation_status = ?
                WHERE id = ?
            """, (validation_status, edl_id))
        else:
            cursor.execute("""
                UPDATE edls SET validation_status = ?, validation_errors = ?
                WHERE id = ?
            """, (validation_status, ",".join(validation_errors), edl_id))
        db.commit()

    def get_edl(self, db, edl_id: int):
        cursor = db.cursor()
        cursor.execute("SELECT id, process_id, edl_name, path, frame_rate, drop_frame, total_events, validation_status, validation_errors, created_at FROM edls WHERE id = ?", (edl_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return {
            "id": row[0],
            "process_id": row[1],
            "edl_name": row[2],
            "file_path": row[3],
            "frame_rate": row[4],
            "drop_frame": bool(row[5]),
            "total_events": row[6],
            "validation_status": row[7],
            "validation_errors": (row[8].split(",") if row[8] else []),
            "created_at": row[9],
        }