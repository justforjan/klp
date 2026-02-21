FROM node:25-alpine3.22 AS css

WORKDIR /workdir

COPY package.json package-lock.json ./
RUN npm ci

COPY ./static ./static
COPY ./templates ./templates

RUN npx @tailwindcss/cli -i ./static/src/input.css -o ./static/css/output.css

FROM ghcr.io/astral-sh/uv:python3.12-alpine3.23

WORKDIR /klp

COPY uv.lock pyproject.toml ./
RUN uv sync --no-dev

COPY --from=css /workdir/static/css/output.css ./static/css/output.css

COPY . .

ENV PYTHONUNBUFFERED=1
#ENV PYTHONFAULTHANDLER=1

CMD ["uv", "run", "main.py"]
