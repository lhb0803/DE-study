
    
FROM python:3.8-buster

WORKDIR /app

ADD . /app

RUN apt-get update && apt-get install -y libgomp1

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["python", "lgbm_api.py"]    
