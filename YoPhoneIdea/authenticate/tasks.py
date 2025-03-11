import redis
import threading
import time
from django.conf import settings
from .models import CustomUser

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)

def delete_unverified_users():
    while True:
        keys = redis_client.keys("pending_user:*")
        for key in keys:
            user_id = redis_client.get(key)
            if user_id:
                try:
                    user = CustomUser.objects.get(pk=user_id)
                    if not user.is_verified:
                        user.delete()
                        redis_client.delete(key)
                        print(f"Deleted unverified user: {user.username}")
                except CustomUser.DoesNotExist:
                    redis_client.delete(key)

        time.sleep(300)  # 5 րոպե սպասում է մինչ հաջորդ ստուգումը

# Start background task
thread = threading.Thread(target=delete_unverified_users, daemon=True)
thread.start()
