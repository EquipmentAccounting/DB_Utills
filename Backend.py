from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, String, Integer, Date, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
from typing import Optional

app = FastAPI()

Base = declarative_base()

# Создание базы данных
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Place(Base):
    __tablename__ = 'places'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, unique=True)
    # Другие поля места, если есть

    devices = relationship("Device", back_populates="place")


class Device(Base):
    __tablename__ = 'devices'

    name = Column(String)
    category = Column(String)
    place_id = Column(Integer, ForeignKey('places.id'))  # Внешний ключ на таблицу мест
    version = Column(String)
    id = Column(Integer, primary_key=True)
    releaseDate = Column(Date)
    softwareStartDate = Column(Date)
    softwareEndDate = Column(Date)
    manufacturer = Column(String)
    xCord = Column(Float)
    yCoord = Column(Float)
    waveRadius = Column(Float)

    place = relationship("Place", back_populates="devices")


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
def search_items(q: Optional[str] = None, category: Optional[str] = None, place: Optional[str] = None,
                 version: Optional[str] = None, id: Optional[int] = None, releaseDate: Optional[date] = None,
                 softwareStartDate: Optional[date] = None, softwareEndDate: Optional[date] = None,
                 manufacturer: Optional[str] = None, xCord: Optional[float] = None,
                 yCoord: Optional[float] = None, waveRadius: Optional[float] = None, db: Session = Depends(get_db)):

    query = db.query(Device)

    # Фильтрация по параметрам запроса
    if q:
        query = query.filter(Device.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(Device.category == category)
    if place:
        query = query.filter(Device.place.has(name=place))
    if version:
        query = query.filter(Device.version == version)
    if id:
        query = query.filter(Device.id == id)
    if releaseDate:
        query = query.filter(Device.releaseDate == releaseDate)
    if softwareStartDate:
        query = query.filter(Device.softwareStartDate == softwareStartDate)
    if softwareEndDate:
        query = query.filter(Device.softwareEndDate == softwareEndDate)
    if manufacturer:
        query = query.filter(Device.manufacturer == manufacturer)
    if xCord:
        query = query.filter(Device.xCord == xCord)
    if yCoord:
        query = query.filter(Device.yCoord == yCoord)
    if waveRadius:
        query = query.filter(Device.waveRadius == waveRadius)

    result = query.all()

    categorized_result = {"computers": [], "router": [], "printer": [], "item": []}
    for device in result:
        device_info = {
            "name": device.name,
            "category": device.category,
            "place_id": device.place_id if device.place else None,
            "version": device.version,
            "id": device.id,
            "releaseDate": str(device.releaseDate),
            "softwareStartDate": str(device.softwareStartDate),
            "softwareEndDate": str(device.softwareEndDate),
            "manufacturer": device.manufacturer,
            "xCord": device.xCord,
            "yCoord": device.yCoord,
            "waveRadius": device.waveRadius
        }
        if device.category == "computers":
            categorized_result["computers"].append(device_info)
        elif device.category == "router":
            categorized_result["router"].append(device_info)
        elif device.category == "printer":
            categorized_result["printer"].append(device_info)
        else:
            categorized_result["item"].append(device_info)

    return categorized_result


# Эндпоинт для добавления нового устройства
@app.post("/add_device")
def add_device(name: str, category: str, place_id: int, version: str, id: int, releaseDate: date,
                softwareStartDate: date, softwareEndDate: date, manufacturer: str,
                xCord: float, yCoord: float, waveRadius: float, db: Session = Depends(get_db)):

    # Проверяем, существует ли устройство с таким же именем
    if db.query(Device).filter(Device.name == name).first():
        raise HTTPException(status_code=400, detail="Device with this name already exists")

    # Создаем новое устройство и добавляем его в базу данных
    new_device = Device(name=name, category=category, place_id=place_id, version=version,
                        id=id, releaseDate=releaseDate, softwareStartDate=softwareStartDate,
                        softwareEndDate=softwareEndDate, manufacturer=manufacturer,
                        xCord=xCord, yCoord=yCoord, waveRadius=waveRadius)
    db.add(new_device)
    db.commit()
    return {"message": "Device added successfully"}
