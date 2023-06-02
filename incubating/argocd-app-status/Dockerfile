FROM    python:3.11.3-slim-buster
WORKDIR /app
COPY    requirements.txt requirements.txt
RUN     pip3 install -r requirements.txt
COPY    queries queries/
COPY    argocd_app_status.py argocd_app_status.py
CMD     [ "python3", "argocd_app_status.py"]
