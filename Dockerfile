ARG BUILD_FROM
# hadolint ignore=DL3006
FROM $BUILD_FROM

# Install requirements
# hadolint ignore=DL3018
RUN \
    apk add --no-cache \
        bash \
        python3 \
        py3-pip \
        gcc \
        musl-dev \
        python3-dev \
        libffi-dev

# Copy app directory
COPY app /app/
COPY run.sh /

RUN pip install --no-cache-dir -r /app/requirements.txt --break-system-packages \
    && chmod a+x /run.sh

CMD [ "/run.sh" ]
