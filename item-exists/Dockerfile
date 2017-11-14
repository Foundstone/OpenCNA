FROM python:2.7.14

WORKDIR /csv_processing
COPY src/requirements.txt .
RUN pip install -r ./requirements.txt

COPY src .
COPY models ../models

ENTRYPOINT ["python", "-W", "ignore", "item_existance_checker.py"]
