class MXFRepository:

    def save_file_record(self, db, file_name: str, path: str):
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO files (file_name, path, status)
            VALUES (?, ?, ?)
        """, (file_name, path, "pending"))
        db.commit()

    def update_status(self, db, file_name: str, status: str):
        cursor = db.cursor()
        cursor.execute("""
            UPDATE files SET status = ?
            WHERE file_name = ?
        """, (status, file_name))
        db.commit()
