from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Enum, Text, create_engine, desc
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from pydantic import BaseModel
import enum
import datetime

# Configuración de base de datos
DATABASE_URL = "sqlite:///./inventario.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums para tipos de movimiento
class TipoMovimiento(str, enum.Enum):
    prestamo = "prestamo"
    devolucion = "devolucion"
    mantenimiento = "mantenimiento"
    traslado = "traslado"

# Modelos SQLAlchemy
class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True)

class Ubicacion(Base):
    __tablename__ = "ubicaciones"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)

class Responsable(Base):
    __tablename__ = "responsables"
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String)

class Herramienta(Base):
    __tablename__ = "herramientas"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    descripcion = Column(Text)
    categoria_id = Column(Integer, ForeignKey("categorias.id"))
    marca = Column(String)
    modelo = Column(String)
    estado = Column(String)
    ubicacion_id = Column(Integer, ForeignKey("ubicaciones.id"))
    responsable_id = Column(Integer, ForeignKey("responsables.id"))
    fecha_ingreso = Column(Date, default=datetime.date.today)
    codigo_interno = Column(String)

class Movimiento(Base):
    __tablename__ = "movimientos"
    id = Column(Integer, primary_key=True, index=True)
    herramienta_id = Column(Integer, ForeignKey("herramientas.id"))
    responsable_id = Column(Integer, ForeignKey("responsables.id"))
    tipo = Column(Enum(TipoMovimiento))
    fecha = Column(Date, default=datetime.date.today)
    ubicacion_origen_id = Column(Integer, ForeignKey("ubicaciones.id"))
    ubicacion_destino_id = Column(Integer, ForeignKey("ubicaciones.id"))
    observaciones = Column(Text)

# Crear tablas
Base.metadata.create_all(bind=engine)

# Schemas Pydantic
class HerramientaCreate(BaseModel):
    nombre: str
    descripcion: str = ""
    categoria_id: int
    marca: str
    modelo: str
    estado: str
    ubicacion_id: int
    responsable_id: int
    codigo_interno: str

class HerramientaUpdate(HerramientaCreate):
    pass

class HerramientaOut(HerramientaCreate):
    id: int
    class Config:
        from_attributes = True

class CategoriaOut(BaseModel):
    id: int
    nombre: str
    class Config:
        from_attributes = True

class UbicacionOut(BaseModel):
    id: int
    nombre: str
    class Config:
        from_attributes = True

class ResponsableOut(BaseModel):
    id: int
    nombre_completo: str
    class Config:
        from_attributes = True

class MovimientoCreate(BaseModel):
    herramienta_id: int
    responsable_id: int
    tipo: TipoMovimiento
    fecha: datetime.date
    ubicacion_origen_id: int
    ubicacion_destino_id: int
    observaciones: str = ""

class MovimientoOut(MovimientoCreate):
    id: int
    class Config:
        from_attributes = True

class HerramientaResumen(BaseModel):
    id: int
    nombre: str
    descripcion: str
    estado: str
    ubicacion_actual: str
    responsable_actual: str
    ultimo_movimiento: MovimientoOut | None

# FastAPI app
app = FastAPI()

# Dependencia para obtener sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Crear herramienta
@app.post("/herramientas/", response_model=HerramientaOut)
def crear_herramienta(herramienta: HerramientaCreate, db: Session = Depends(get_db)):
    db_herramienta = Herramienta(**herramienta.dict())
    db.add(db_herramienta)
    db.commit()
    db.refresh(db_herramienta)
    return db_herramienta

# Listar todas las herramientas
@app.get("/herramientas/", response_model=list[HerramientaOut])
def listar_herramientas(db: Session = Depends(get_db)):
    return db.query(Herramienta).all()

# Obtener una herramienta por ID
@app.get("/herramientas/{herramienta_id}", response_model=HerramientaOut)
def obtener_herramienta(herramienta_id: int, db: Session = Depends(get_db)):
    herramienta = db.query(Herramienta).filter(Herramienta.id == herramienta_id).first()
    if not herramienta:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")
    return herramienta

# Actualizar una herramienta por ID
@app.put("/herramientas/{herramienta_id}", response_model=HerramientaOut)
def actualizar_herramienta(herramienta_id: int, herramienta_actualizada: HerramientaUpdate, db: Session = Depends(get_db)):
    herramienta = db.query(Herramienta).filter(Herramienta.id == herramienta_id).first()
    if not herramienta:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")
    for key, value in herramienta_actualizada.dict().items():
        setattr(herramienta, key, value)
    db.commit()
    db.refresh(herramienta)
    return herramienta

# Eliminar una herramienta por ID
@app.delete("/herramientas/{herramienta_id}")
def eliminar_herramienta(herramienta_id: int, db: Session = Depends(get_db)):
    herramienta = db.query(Herramienta).filter(Herramienta.id == herramienta_id).first()
    if not herramienta:
        raise HTTPException(status_code=404, detail="Herramienta no encontrada")
    db.delete(herramienta)
    db.commit()
    return {"mensaje": "Herramienta eliminada correctamente"}

# Endpoints para categorías
@app.get("/categorias/", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(Categoria).all()

# Endpoints para ubicaciones
@app.get("/ubicaciones/", response_model=list[UbicacionOut])
def listar_ubicaciones(db: Session = Depends(get_db)):
    return db.query(Ubicacion).all()

# Endpoints para responsables
@app.get("/responsables/", response_model=list[ResponsableOut])
def listar_responsables(db: Session = Depends(get_db)):
    return db.query(Responsable).all()

# Endpoints para movimientos
@app.post("/movimientos/", response_model=MovimientoOut)
def registrar_movimiento(movimiento: MovimientoCreate, db: Session = Depends(get_db)):
    db_movimiento = Movimiento(**movimiento.dict())
    db.add(db_movimiento)

    herramienta = db.query(Herramienta).filter(Herramienta.id == movimiento.herramienta_id).first()
    if herramienta:
        herramienta.ubicacion_id = movimiento.ubicacion_destino_id
        herramienta.responsable_id = movimiento.responsable_id
        db.commit()
        db.refresh(herramienta)

    db.commit()
    db.refresh(db_movimiento)
    return db_movimiento

@app.get("/movimientos/", response_model=list[MovimientoOut])
def listar_movimientos(db: Session = Depends(get_db)):
    return db.query(Movimiento).all()

# Endpoint de resumen por herramienta
@app.get("/resumen/", response_model=list[HerramientaResumen])
def resumen_herramientas(db: Session = Depends(get_db)):
    herramientas = db.query(Herramienta).all()
    resumen = []
    for h in herramientas:
        ultimo = db.query(Movimiento).filter(Movimiento.herramienta_id == h.id).order_by(desc(Movimiento.fecha)).first()
        resumen.append(HerramientaResumen(
            id=h.id,
            nombre=h.nombre,
            descripcion=h.descripcion,
            estado=h.estado,
            ubicacion_actual=db.query(Ubicacion).filter(Ubicacion.id == h.ubicacion_id).first().nombre,
            responsable_actual=db.query(Responsable).filter(Responsable.id == h.responsable_id).first().nombre_completo,
            ultimo_movimiento=ultimo
        ))
    return resumen

import csv
from fastapi.responses import StreamingResponse
from io import StringIO

@app.get("/resumen/csv")
def exportar_resumen_csv(db: Session = Depends(get_db)):
    herramientas = db.query(Herramienta).all()
    
    # Crear un buffer en memoria para escribir CSV
    buffer = StringIO()
    writer = csv.writer(buffer)
    
    # Escribir encabezados
    writer.writerow(["ID", "Nombre", "Descripción", "Estado", "Ubicación Actual", "Responsable Actual", "Último Movimiento Tipo", "Último Movimiento Fecha", "Último Movimiento Observaciones"])
    
    for h in herramientas:
        ubicacion = db.query(Ubicacion).filter(Ubicacion.id == h.ubicacion_id).first()
        responsable = db.query(Responsable).filter(Responsable.id == h.responsable_id).first()
        ultimo_mov = db.query(Movimiento).filter(Movimiento.herramienta_id == h.id).order_by(desc(Movimiento.fecha)).first()
        
        writer.writerow([
            h.id,
            h.nombre,
            h.descripcion,
            h.estado,
            ubicacion.nombre if ubicacion else "",
            responsable.nombre_completo if responsable else "",
            ultimo_mov.tipo.value if ultimo_mov else "",
            ultimo_mov.fecha.isoformat() if ultimo_mov else "",
            ultimo_mov.observaciones if ultimo_mov else "",
        ])
    
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=resumen_herramientas.csv"})
