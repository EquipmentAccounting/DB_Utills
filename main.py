import asyncio
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession
from models.device import device
from models.place import place
from models.db_session import global_init, session_db
from models.user import User


async def main():
    await global_init()
#     await test()
# @session_db
# async def test(session: AsyncSession):
#     user = User(telegram_id=15, username="Kolya", first_name="Kolya", age=11, city="Moskva", count_tests=23)
#     await user.save(session=session)
#     use = await User.get_user(telegram_id=15, session=session)
#     user_name = use.username
#     print(user_name)
    async with session_db() as session:
        await test(session)


@session_db
async def test(session):
    test_device = device(
        name="Test Device",
        category="Test Category",
        place_id=1,
        version="1.0",
        releaseDate=datetime.now().date(),
        softwareStartDate=datetime.now().date(),
        softwareEndDate=datetime.now().date(),
        manufacturer="Test Manufacturer",
        xCord=0.0,
        yCoord=0.0,
        waveRadius=1.0
    )
    test_place = place(name="Test Place")

    # Сначала сохраните место, чтобы у него был id
    await test_place.save(session=session)

    # Затем присвойте id места устройству
    test_device.place_id = test_place.id

    # Сохраните устройство
    await test_device.save(session=session)

    # Подтвердите изменения
    await session.commit()

    print("Test completed successfully.")


if __name__ == "__main__":
    asyncio.run(main())
