from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

app = FastAPI()

# Создание базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Модель устройства
class Device(Base):
    __tablename__ = 'devices'

    name = Column(String, primary_key=True)
    category = Column(String)
    place = Column(String)
    version = Column(String)  # Версия программного обеспечения


# Создание таблицы
Base.metadata.create_all(bind=engine)


# Функция зависимости для получения сессии базы данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Эндпоинт для поиска устройств
@app.get("/search")
def search_items(q: str = None, category: str = None, place: str = None, version: str = None,
                 db: Session = Depends(get_db)):
    query = db.query(Device)

    # Фильтрация по параметрам запроса
    if q:
        query = query.filter(Device.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(Device.category == category)
    if place:
        query = query.filter(Device.place == place)
    if version:
        query = query.filter(Device.version == version)

    result = query.all()

    categorized_result = {"computers": [], "router": [], "printer": [], "item": []}
    for device in result:
        if device.category == "computers":
            categorized_result["computers"].append(
                {"name": device.name, "place": device.place, "version": device.version})
        elif device.category == "router":
            categorized_result["router"].append({"name": device.name, "place": device.place, "version": device.version})
        elif device.category == "printer":
            categorized_result["printer"].append(
                {"name": device.name, "place": device.place, "version": device.version})
        else:
            categorized_result["item"].append(
                {"name": device.name, "category": device.category, "place": device.place, "version": device.version})

    return categorized_result


# Эндпоинт для добавления нового устройства
@app.post("/add_device")
def add_device(name: str, category: str, place: str, version: str, db: Session = Depends(get_db)):
    # Проверяем, существует ли устройство с таким же именем
    if db.query(Device).filter(Device.name == name).first():
        raise HTTPException(status_code=400, detail="Device with this name already exists")

    # Создаем новое устройство и добавляем его в базу данных
    new_device = Device(name=name, category=category, place=place, version=version)
    db.add(new_device)
    db.commit()
    return {"message": "Device added successfully"}