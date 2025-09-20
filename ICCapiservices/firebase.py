import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from django.conf import settings

# Initialize Firebase using environment variables
firebase_credentials = {
    "type": settings.FIREBASE_TYPE,
    "project_id": settings.FIREBASE_PROJECT_ID,
    "private_key_id": settings.FIREBASE_PRIVATE_KEY_ID,
    "private_key": settings.FIREBASE_PRIVATE_KEY,
    "client_email": settings.FIREBASE_CLIENT_EMAIL,
    "client_id": settings.FIREBASE_CLIENT_ID,
    "auth_uri": settings.FIREBASE_AUTH_URI,
    "token_uri": settings.FIREBASE_TOKEN_URI,
    "auth_provider_x509_cert_url": settings.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
    "client_x509_cert_url": settings.FIREBASE_CLIENT_X509_CERT_URL,
    "universe_domain": settings.FIREBASE_UNIVERSE_DOMAIN
}

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(firebase_credentials)
        firebase_admin.initialize_app(cred)
        print("Firebase initialized successfully!")
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        # For development, you might want to skip Firebase initialization
        pass


def build_fcm_message(token: str, title: str, message: str, link: str | None = None):
    webpush_config = None
    if link:
        webpush_config = messaging.WebpushConfig(
            fcm_options=messaging.WebpushFCMOptions(
                link=link
            )
        )

    return messaging.Message(
        token=token,
        notification=messaging.Notification(
            title=title,
            body=message,
        ),
        webpush=webpush_config
    )

# send a notification to a specific device
def send_single_notification(token, title, body, link=None):
    message = build_fcm_message(token, title, body, link)
    response = messaging.send(message)
    return response

# send multiple notifications to a list of device tokens
def send_batch_notification(tokens, title, body, link=None):
    messages = [build_fcm_message(token, title, body, link) for token in tokens]
    response = messaging.send_each(messages)
    return response