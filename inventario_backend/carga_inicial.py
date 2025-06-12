from app.main import SessionLocal, Categoria, Ubicacion, Responsable

db = SessionLocal()

# Datos de prueba
categorias = ["Taladros", "Fijaciones", "Cortadoras", "Lijadoras"]
ubicaciones = ["Bodega A", "Bodega B", "Obra Norte", "Obra Sur"]
responsables = ["Juan Pérez", "Ana Torres", "Carlos Díaz", "Laura Méndez"]

# Insertar categorías
for nombre in categorias:
    if not db.query(Categoria).filter_by(nombre=nombre).first():
        db.add(Categoria(nombre=nombre))

# Insertar ubicaciones
for nombre in ubicaciones:
    if not db.query(Ubicacion).filter_by(nombre=nombre).first():
        db.add(Ubicacion(nombre=nombre))

# Insertar responsables
for nombre in responsables:
    if not db.query(Responsable).filter_by(nombre_completo=nombre).first():
        db.add(Responsable(nombre_completo=nombre))

db.commit()
db.close()

print("✅ Datos iniciales insertados correctamente.")
