FROM python:3.12.1-alpine3.19

WORKDIR /

COPY entrypoint.sh /entrypoint.sh


WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV SERVER_PORT=8080
ENV JWT_SECRET_KEY=VV@$B%Avdswa1B!$5
ENV FLASK_APP=app.py

#local test only
ENV SERVER_ADDRESS=0.0.0.0
ENV SERVER_PORT=8080
ENV POSTGRES_CONN=postgres://postgres:postgres@localhost:5432/pulse
ENV POSTGRES_USERNAME=postgres
ENV POSTGRES_PASSWORD=postgres
ENV POSTGRES_HOST=localhost
ENV POSTGRES_DATABASE=pulse
ENV POSTGRES_PORT=5432

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["sh", "entrypoint.sh" ]

# CMD ["sh", "-c", "exec python3 -m flask db upgrade", "exec python3 -m flask run --host=0.0.0.0 --port=$SERVER_PORT"]