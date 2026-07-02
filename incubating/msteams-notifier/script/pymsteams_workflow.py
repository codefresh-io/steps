#!/usr/bin/env python
"""Vendored Power Automate Workflow connector for MS Teams.

The published ``pymsteams-workflow`` package installs its code under the module
name ``pymsteams``, which collides with the regular ``pymsteams`` package (both
own ``pymsteams/__init__.py``). Since this notifier needs BOTH the legacy
webhook client (``pymsteams``) and the Workflow client at the same time, the
Workflow client is vendored here under a distinct module name so the two can
coexist.

It builds a Microsoft Adaptive Card and POSTs it to a Power Automate Workflow
"When a Teams webhook request is received" trigger URL.
"""

import json
from urllib.parse import urlparse, parse_qs

import requests


class TeamsWebhookException(Exception):
    """Custom exception for a failed workflow call."""
    pass


class cardsection:
    """Accumulates section content and renders it as Adaptive Card blocks."""

    def __init__(self):
        self.activity_subtitle = None
        self.activity_image = None
        self.activity_text = None
        self.facts = []

    def activitySubtitle(self, subtitle):
        self.activity_subtitle = subtitle
        return self

    def activityImage(self, image_url):
        self.activity_image = image_url
        return self

    def activityText(self, text):
        self.activity_text = text
        return self

    def addFact(self, name, value):
        self.facts.append({"title": str(name), "value": str(value)})
        return self

    def as_blocks(self):
        blocks = []

        if self.activity_image or self.activity_subtitle:
            columns = []
            if self.activity_image:
                columns.append({
                    "type": "Column",
                    "width": "auto",
                    "items": [{
                        "type": "Image",
                        "url": self.activity_image,
                        "size": "Small",
                    }],
                })
            if self.activity_subtitle:
                columns.append({
                    "type": "Column",
                    "width": "stretch",
                    "verticalContentAlignment": "Center",
                    "items": [{
                        "type": "TextBlock",
                        "text": self.activity_subtitle,
                        "weight": "Bolder",
                        "wrap": True,
                    }],
                })
            blocks.append({"type": "ColumnSet", "columns": columns})

        if self.activity_text:
            blocks.append({
                "type": "TextBlock",
                "text": self.activity_text,
                "wrap": True,
            })

        if self.facts:
            blocks.append({"type": "FactSet", "facts": self.facts})

        return blocks


class connectorcard:
    def __init__(self, url):
        # Tolerate surrounding whitespace and quotes that commonly leak in from
        # mis-quoted CI environment variables (e.g. MSTEAMS_WORKFLOW_URL="...").
        url = (url or "").strip().strip('"').strip("'").strip()
        if not url:
            raise TeamsWebhookException(
                "Workflow URL is empty. Set the MSTEAMS_WORKFLOW_URL environment "
                "variable to the Power Automate trigger URL (without surrounding quotes)."
            )

        # Parse the URL to extract the base URL and query parameters.
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            raise TeamsWebhookException(
                f"Invalid workflow URL {url!r}: expected an https:// URL. Check that "
                "MSTEAMS_WORKFLOW_URL is set correctly and is not wrapped in quotes."
            )

        self.hookurl = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        query_params = parse_qs(parsed_url.query)

        self.params = {
            'api-version': query_params.get('api-version', ['2016-06-01'])[0],
            'sp': query_params.get('sp', ['/triggers/manual/run'])[0],
            'sv': query_params.get('sv', ['1.0'])[0],
            'sig': query_params.get('sig', [''])[0],
        }

        self.payload = {
            "type": "message",
            "attachments": [
                {
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "contentUrl": None,
                    "content": {
                        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                        "type": "AdaptiveCard",
                        "version": "1.4",
                        "body": [],
                        "msteams": {"width": "full"},
                    },
                }
            ],
        }
        self.proxies = None
        self.http_timeout = 60
        self.verify = True
        self.last_http_response = None

    def _body(self):
        return self.payload["attachments"][0]["content"]["body"]

    def title(self, mtitle):
        self._body().insert(0, {
            "type": "TextBlock",
            "text": mtitle,
            "style": "heading",
            "weight": "Bolder",
            "size": "Large",
            "wrap": True,
            "id": "title",
        })
        return self

    def text(self, mtext):
        self._body().append({
            "type": "TextBlock",
            "text": mtext,
            "wrap": True,
            "id": "body",
        })
        return self

    def addLinkButton(self, button_text, button_url):
        actions = self.payload["attachments"][0]["content"].setdefault("actions", [])
        actions.append({
            "type": "Action.OpenUrl",
            "title": button_text,
            "url": button_url,
        })
        return self

    def addSection(self, section):
        self._body().extend(section.as_blocks())
        return self

    def printme(self):
        print(json.dumps(self.payload, indent=4))

    def send(self):
        headers = {
            'User-Agent': 'MSTeams',
            'Content-Type': 'application/json',
        }
        try:
            r = requests.post(
                self.hookurl,
                params=self.params,
                data=json.dumps(self.payload),
                headers=headers,
                proxies=self.proxies,
                timeout=self.http_timeout,
                verify=self.verify,
            )
            self.last_http_response = r
            if r.status_code in (requests.codes.ok, requests.codes.accepted):
                return True
            raise TeamsWebhookException(r.text)
        except requests.exceptions.RequestException as e:
            raise TeamsWebhookException(str(e))