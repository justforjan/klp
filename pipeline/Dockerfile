FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

LABEL org.opencontainers.image.source=https://github.com/justforjan/klp

ENV DEBIAN_FRONTEND=noninteractive

# Generate de_DE.UTF-8 non-interactively: write locale entry, generate it, and set /etc/default/locale
RUN apt-get update && \
    apt-get install -y --no-install-recommends locales && \
    echo "de_DE.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen de_DE.UTF-8 && \
    # Set default locale file directly to avoid update-locale issues in some images
    printf 'LANG=de_DE.UTF-8\nLC_ALL=de_DE.UTF-8\n' > /etc/default/locale && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=de_DE.UTF-8
ENV LC_ALL=de_DE.UTF-8

CMD ["sh"]