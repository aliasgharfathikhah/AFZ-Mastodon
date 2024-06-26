FROM python:3.12


ENV PYTHONUNBUFFERED 1
ENV TZ Asia/Tehran


WORKDIR /usr/src/app


RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


COPY . .


CMD [ "python", "afz.py" ]
