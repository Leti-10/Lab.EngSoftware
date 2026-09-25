from datetime import datetime

from services import user_service

user_service_instance = user_service.UserService()
u = user_service_instance.create_user(
    user_service.User(
        id=1,
        username="john_doe",
        email="teste@teste.com",
        password="password123",
        created_at=datetime.now(),
    )
)
print(u)
