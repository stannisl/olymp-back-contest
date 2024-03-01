from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()

# def start_engine() -> Engine:
#     try:
#         engine = create_engine(f"postgresql://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}")
#     except Exception as e:
#         raise ConnectionError("Не удалось подлкючиться к Базе Данных.", e)
#     return engine


# def start_session():
#     try:
#         engine = start_engine()
#         session = sessionmaker(bind=engine)
#     except Exception as e:
#         raise ConnectionError("Не удалось создать сессию.")
#     return session
