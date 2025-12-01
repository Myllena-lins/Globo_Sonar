from sqlalchemy.orm import Session

from app.model.mxf import MXFFile

class MXFRepository:
    def save_file_record(self, db: Session, file_name: str, path: str) -> MXFFile:
        mxf = MXFFile(file_name=file_name, path=path, status="pending")
        db.add(mxf)
        db.commit()
        db.refresh(mxf)
        return mxf

    def update_status(self, db: Session, file_id: int, status: str) -> MXFFile:
        mxf = db.query(MXFFile).filter(MXFFile.id == file_id).first()
        if not mxf:
            return None
        mxf.status = status
        db.commit()
        db.refresh(mxf)
        return mxf
