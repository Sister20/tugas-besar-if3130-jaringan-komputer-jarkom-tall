FROM python:3.10
WORKDIR /app

COPY . /app

CMD ["python", "TictactoePlayer1.py"]