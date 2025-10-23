FROM ubuntu:22.04
LABEL maintainer="Primus Labs"
WORKDIR /zkvm-server
ENV EXECUTION_FLAG=DOCKER

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    ln -sf python3 /usr/bin/python && \
    apt-get clean
    
COPY ./bin/zktls /zkvm-server/bin/
COPY ./https_server.py /zkvm-server/
RUN chmod +x /zkvm-server/bin/zktls /zkvm-server/https_server.py

EXPOSE 38080
CMD ["python", "https_server.py"]
