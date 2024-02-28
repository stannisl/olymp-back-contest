from config import POSTGRES_CONN, DEBUG, POSTGRES_USERNAME, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import sessionmaker


def start_engine() -> Engine:
    try:
        engine = create_engine(f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")
    except Exception as e:
        raise ConnectionError("Не удалось подлкючиться к Базе Данных.", e)
    return engine


def start_session():
    try:
        engine = start_engine()
        session = sessionmaker(bind=engine)
    except Exception as e:
        raise ConnectionError("Не удалось создать сессию.")
    return session


if __name__ == "__main__":
    session = start_session()
    engine = start_engine()
    # with engine.connect() as connection:
    #         result = connection.execute(text(f"SELECT name FROM countries WHERE region = '{request.args.get('region').capitalize()}'")).all()
    #         print(f"[*]                            {[i[0] for i in result]}")