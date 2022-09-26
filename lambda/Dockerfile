FROM public.ecr.aws/lambda/python:3.9

RUN yum -y update && yum groupinstall -y "Development Tools"
RUN yum -y install cmake3 && ln -s /usr/bin/cmake3 /usr/bin/cmake

WORKDIR ${LAMBDA_TASK_ROOT}
RUN git clone --recursive https://github.com/bingmann/cobs.git

WORKDIR ${LAMBDA_TASK_ROOT}/cobs
RUN python setup.py install

WORKDIR ${LAMBDA_TASK_ROOT}
COPY requirements.txt .
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY src/* ${LAMBDA_TASK_ROOT}/
COPY config/ ${LAMBDA_TASK_ROOT}/config

CMD [ "app.lambda_handler" ]
