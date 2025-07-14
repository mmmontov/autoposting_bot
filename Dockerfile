FROM python:3.11-slim

RUN mkdir /autoposting_bot

WORKDIR /autoposting_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python3", "main.py"]