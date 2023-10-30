FROM    python:3.12-slim-bookworm
WORKDIR /app
COPY    requirements.txt requirements.txt
RUN     pip3 install -r requirements.txt
COPY    queries queries/
COPY    argocd_sync.py run.py
CMD     [ "python3", "run.py"]
