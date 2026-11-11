FROM python:3.14-slim-trixie

ENV LANG=C.UTF-8

RUN pip install --no-cache-dir jira==3.10.5 certifi==2026.10.23

COPY script/. /

ENTRYPOINT ["python", "/jira_issue_manager.py"]
CMD [""]
