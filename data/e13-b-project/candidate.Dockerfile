FROM python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY Makefile config.h extra.h helper.c main.c ./
RUN sed -i -e "s|https\?://deb.debian.org/debian-security|https://mirrors.tuna.tsinghua.edu.cn/debian-security|g" -e "s|https\?://deb.debian.org/debian|https://mirrors.tuna.tsinghua.edu.cn/debian|g" /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get install -y --no-install-recommends build-essential strace && rm -rf /var/lib/apt/lists/*
RUN make app
CMD ["./app"]
