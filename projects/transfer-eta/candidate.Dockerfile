FROM m.daocloud.io/docker.io/library/python:3.13-slim@sha256:70729b46c69b4f1e97c4822c1af3df53a1476cf5ddc6c087c0c10bc3a5678c2f
WORKDIR /work
COPY . .
RUN sed -i -e 's|deb.debian.org/debian-security|mirrors.tuna.tsinghua.edu.cn/debian-security|g' -e 's|deb.debian.org/debian|mirrors.tuna.tsinghua.edu.cn/debian|g' /etc/apt/sources.list.d/debian.sources
RUN apt-get -o Acquire::ForceIPv4=true -o Acquire::Retries=3 update && apt-get install -y --no-install-recommends build-essential strace && rm -rf /var/lib/apt/lists/*
RUN make transfer-eta
CMD ["./transfer-eta","100"]
