FROM python:2.7


ENV SHELL /bin/bash

RUN pip install boto3 pytz && echo "/" > /usr/local/lib/python2.7/site-packages/cf.pth

COPY cfecs-update /usr/local/bin/
COPY cfecs/ cfecs/

#ENTRYPOINT ["/cfecs-update"]
CMD ["bash"]