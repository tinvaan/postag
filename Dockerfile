ARG LAMBDA_DIR="/app/postag"


FROM ubuntu:latest AS base
RUN apt-get update && \
    apt-get install -y gcc make python3-pip python3-venv

ARG LAMBDA_DIR
RUN mkdir -p ${LAMBDA_DIR}
RUN pip3 install --target ${LAMBDA_DIR} awslambdaric


FROM ubuntu:latest AS source
RUN apt-get update && \
    apt-get install -y gcc make python3-pip python3-venv
RUN pip3 install pipx && pipx install poetry==1.2.0

ARG LAMBDA_DIR
COPY . ${LAMBDA_DIR}
WORKDIR ${LAMBDA_DIR}

ENV PATH="/root/.local/bin:$PATH"
RUN poetry install --no-root

COPY --from=base ${LAMBDA_DIR} ${LAMBDA_DIR}
RUN poetry run pip3 install --upgrade --target ${LAMBDA_DIR} .

ENTRYPOINT [ "python3", "-m", "awslambdaric" ]
CMD [ "postag.func.run" ]
