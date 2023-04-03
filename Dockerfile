FROM python:3.6-slim-buster AS build

WORKDIR /app
COPY assets ./assets
COPY src ./src
COPY app.py requirements.txt ./

RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.6-slim-buster

COPY --from=build /root/.local /root/.local
COPY --from=build /app .

ENV PATH=/root/.local/bin:$PATH

CMD ["python", "app.py"]
