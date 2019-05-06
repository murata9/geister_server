FROM ubuntu:18.04

RUN apt-get update \
     && apt-get install -y python3 python3-pip \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt /usr/src/app/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /usr/src/app/requirements.txt

# 備考:docker composeの場合はマウントする
COPY server /usr/src/app

EXPOSE 5000

# 環境変数の設定
# 備考:docker composeの場合はそちらで設定する
ARG secret_key
ARG database_name
ARG database_host
ARG database_user
ARG database_pass
ARG database_port

ENV GEISTER_SECRET_KEY=${secret_key}
ENV GEISTER_DATABASE_NAME=${database_name}
ENV GEISTER_DATABASE_HOST=${database_host}
ENV GEISTER_DATABASE_USER=${database_user}
ENV GEISTER_DATABASE_PASS=${database_pass}
ENV GEISTER_DATABASE_PORT=${database_port}

CMD ["python3", "/usr/src/app/run.py"]
