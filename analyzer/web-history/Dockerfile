FROM python:2.7.14

WORKDIR /web-history
COPY src/requirements.txt .
RUN pip install -r ./requirements.txt

COPY src .

ENTRYPOINT ["python", "-W", "ignore", "web_history.py"]
