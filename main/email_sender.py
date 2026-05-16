import os
import base64
import json
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

logger = logging.getLogger(__name__)


def get_gmail_service():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")
    TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    elif os.environ.get("GMAIL_TOKEN_JSON"):
        creds = Credentials.from_authorized_user_info(
            json.loads(os.environ["GMAIL_TOKEN_JSON"]), SCOPES
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
    elif not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS_PATH):
            raise FileNotFoundError(
                f"credentials.json not found at {CREDENTIALS_PATH}. "
                "Download an OAuth 2.0 client ID from Google Cloud Console and place it in main/."
            )
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=8080)
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
        logger.info("OAuth complete. Copy token JSON to GMAIL_TOKEN_JSON secret:\n%s", creds.to_json())

    return build("gmail", "v1", credentials=creds)


def build_html(articles: list[dict]) -> str:
    date_str = datetime.now().strftime("%Y-%m-%d")
    count = len(articles)

    article_blocks = ""
    for i, a in enumerate(articles, 1):
        article_blocks += f"""
        <div style="margin-bottom:32px; padding-bottom:24px; border-bottom:1px solid #eee;">
            <p style="color:#888; font-size:12px; margin:0 0 4px;">
                {i}. {a.get('source', '')} &nbsp;·&nbsp;
                <a href="{a['url']}">Origin link</a>
            </p>
            <h2 style="margin:0 0 8px; font-size:18px;">{a['title']}</h2>
            <p style="margin:0; line-height:1.7; color:#333;">{a['summary']}</p>
        </div>
        """

    return f"""
    <html><body style="font-family:sans-serif; max-width:680px; margin:auto; padding:24px; color:#222;">
        <div style="background:#0f172a; color:white; padding:20px 24px; border-radius:8px; margin-bottom:28px;">
            <h1 style="margin:0; font-size:22px;">📰 Newilver Daily</h1>
            <p style="margin:6px 0 0; color:#94a3b8;">{date_str} &nbsp;·&nbsp; {count} Articles</p>
        </div>
        {article_blocks}
        <p style="color:#aaa; font-size:12px; text-align:center; margin-top:32px;">
            Newilver · Scheduled  · Daily 23:00 UTC
        </p>
    </body></html>
    """


def send_email(articles: list[dict], recipient: str):
    service = get_gmail_service()
    date_str = datetime.now().strftime("%Y-%m-%d")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[Newilver] {date_str} IT News"
    msg["From"] = recipient
    msg["To"] = recipient
    msg.attach(MIMEText(build_html(articles), "html"))

    encoded = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": encoded}).execute()

    logger.info("Email sent: %s", date_str)

if __name__ == "__main__":
    get_gmail_service()