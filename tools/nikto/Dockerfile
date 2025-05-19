FROM perl:latest

RUN apt-get update && \
    apt-get install -y git && \
    git clone https://github.com/sullo/nikto.git /opt/nikto

WORKDIR /opt/nikto
ENTRYPOINT ["perl", "nikto.pl"]

