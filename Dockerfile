FROM python:3.12-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /Animal_Shelter
COPY requirements.txt .
RUN pip install --no-cache -r /Animal_Shelter/requirements.txt
COPY app.py .
CMD ["python", "-m", "app.py"]