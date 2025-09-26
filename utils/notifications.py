import requests
import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from users.models import User
from django.contrib.auth import get_user_model
from pywebpush import webpush, WebPushException
from orders.models import Order
from users.models import User, MedicProfile
import time




# Firebase app faqat bir marta initialize qilinadi
if not firebase_admin._apps:
    cred = credentials.Certificate(settings.FIREBASE_CREDENTIAL)
    firebase_admin.initialize_app(cred)


FCM_VAPID_PRIVATE_KEY = "SIZNING_PRIVATE_KEY"
FCM_VAPID_CLAIMS = {
    "sub": "mailto:youremail@example.com"
}

def send_push(user: User, title: str, body: str, data: dict = None):
    """
    Web-push yuborish (Firebase Cloud Messaging)
    """
    if not hasattr(user, "push_token") or not user.push_token:
        raise ValueError("User push token not found")

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        data=data or {},
        token=user.push_token,
    )
    response = messaging.send(message)
    return response

def send_webpush(subscription_info, message):
    try:
        webpush(
            subscription_info=subscription_info,
            data=message,
            vapid_private_key=FCM_VAPID_PRIVATE_KEY,
            vapid_claims=FCM_VAPID_CLAIMS,
        )
        return True
    except WebPushException as ex:
        print("WebPush error:", ex)
        return False

def send_sms(phone: str, text: str):
    """
    phone: +998XXXXXXXXX
    text: SMS matni
    """
    url = "https://sms-api.example/send"  # lokal provayder API
    payload = {"to": phone, "message": text}
    resp = requests.post(url, json=payload)
    return resp.status_code == 200

def notify_medics_new_order(order: Order):
    """
    Buyurtma yaratildi: hudud va xizmat turi bo‘yicha mediklarga push + fallback SMS yuborish
    """
    # Hudud va xizmat turi bo‘yicha mediklarni filterlash
    medics_qs = MedicProfile.objects.filter(status="approved", areas__icontains=order.client.address)
    medics_qs = [m for m in medics_qs if order.address in m.areas]

    # Push yuborish
    push_failed_medics = []
    for medic in medics_qs:
        try:
            send_push(
                medic.user,
                title="Yangi buyurtma",
                body=f"Yangi buyurtma #{order.id} sizning hududingizda",
                data={"order_id": str(order.id)}
            )
        except Exception:
            push_failed_medics.append(medic)

    # Fallback SMS (faqat 2–3 medik)
    max_sms = 2
    sms_count = 0
    for medic in push_failed_medics[:3]:
        phone = medic.user.phone
        if phone and sms_count < max_sms:
            text = f"Yangi buyurtma #{order.id} sizning hududingizda. Iltimos qabul qiling."
            send_sms(phone, text)
            sms_count += 1
            time.sleep(1)  # API flood limit uchun kichik kutish

    return True

def send_push_notification(push_token: str, title: str, body: str, data: dict = None):
    """
    push_token: FCM yoki web-push token
    title: push sarlavhasi
    body: push matni
    data: qo‘shimcha ma’lumot (dict)
    """
    try:
        payload = {
            "title": title,
            "body": body,
            "data": data or {}
        }
        # Misol: FCM HTTP API
        resp = requests.post(
            "https://fcm.googleapis.com/fcm/send",
            headers={
                "Authorization": f"key={settings.FCM_SERVER_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "to": push_token,
                "notification": {
                    "title": title,
                    "body": body,
                },
                "data": data or {}
            }
        )
        return resp.status_code == 200
    except Exception as e:
        print("Push notification error:", e)
        return False

def send_sms(phone: str, text: str):
    """
    phone: +998XXXXXXXXX
    text: SMS matni
    """
    try:
        url = "https://sms-api.example/send"  # o‘z provider API
        payload = {"to": phone, "message": text}
        resp = requests.post(url, json=payload)
        return resp.status_code == 200
    except Exception as e:
        print("SMS sending error:", e)
        return False

def notify_medics_new_order(order: Order):
    """
    order: Order instance
    Hudud bo‘yicha mediklarni push + SMS yuboradi
    """
    # TODO: hudud bo‘yicha filter
    medics = MedicProfile.objects.filter(status="approved")  # soddalashtirilgan
    for medic in medics:
        user = medic.user
        # Push
        if user.push_token:
            send_push_notification(
                push_token=user.push_token,
                title="Yangi buyurtma",
                body=f"Yangi buyurtma #{order.id} sizning hududingizda",
                data={"order_id": str(order.id)}
            )
        # SMS fallback (agar push token yo‘q bo‘lsa)
        elif user.phone:
            send_sms(user.phone, f"Yangi buyurtma #{order.id} sizning hududingizda")