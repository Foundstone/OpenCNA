FROM python:2.7.14

COPY requirements.txt .
RUN pip install -r ./requirements.txt

WORKDIR /parsers
COPY src .

ENTRYPOINT ["python", "normalize.py"]
