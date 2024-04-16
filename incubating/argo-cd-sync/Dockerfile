FROM    python:3.13.0a5-bookworm


# USER codefresh
RUN useradd -d /home/codefresh -m -s /usr/bin/bash codefresh
USER codefresh
WORKDIR /home/codefresh

ENV PYTHONPATH /home/codefresh/.local/lib/python3.13/site-packages/

COPY    --chown=codefresh requirements.txt requirements.txt
RUN     pip3 install --upgrade pip
RUN     pip3 install --user -r requirements.txt
COPY    queries queries/
COPY    argocd_sync.py run.py
CMD     [ "python3", "run.py"]
