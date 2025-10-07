FROM python:3.10-slim
USER root

# ロケールとタイムゾーンの設定
RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

# 必要なパッケージのインストール
RUN apt-get install -y git gcc wget curl 

# 作業ディレクトリの作成
RUN mkdir -p /discord-rembg-bot
COPY ./requirements.txt /discord-rembg-bot
WORKDIR /discord-rembg-bot

# Pythonパッケージのインストール
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt

# アプリケーションファイルのコピー
COPY . /discord-rembg-bot

# SSL設定の確認
RUN openssl ciphers 'ALL'

# Botの起動
CMD ["python", "main.py"]
