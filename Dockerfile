FROM python:3.11.3-slim-bullseye
WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install -r requirements.txt
COPY . /app
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]