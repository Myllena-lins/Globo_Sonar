from core.database import Base, engine
import models.mxf_file

Base.metadata.create_all(bind=engine)

print("Banco criado!")
