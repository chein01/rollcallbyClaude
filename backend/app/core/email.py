from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.core.config import settings

# Cấu hình email
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME or "dummy",
    MAIL_PASSWORD=settings.MAIL_PASSWORD or "dummy",
    MAIL_FROM=settings.MAIL_FROM or "dummy@example.com",
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER or "smtp.example.com",
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)


async def send_reset_password_email(email: EmailStr, reset_token: str):
    """
    Gửi email khôi phục mật khẩu.
    
    Args:
        email: Email người nhận
        reset_token: Token khôi phục mật khẩu
    """
    # Kiểm tra xem có cấu hình email không
    if not all([settings.MAIL_USERNAME, settings.MAIL_PASSWORD, settings.MAIL_FROM, settings.MAIL_SERVER]):
        print(f"Email configuration is not complete. Skipping sending email to {email}")
        return
        
    # Tạo URL khôi phục mật khẩu
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    
    # Nội dung email
    html = f"""
        <p>Xin chào,</p>
        <p>Bạn đã yêu cầu khôi phục mật khẩu cho tài khoản của mình.</p>
        <p>Vui lòng nhấp vào liên kết bên dưới để đặt lại mật khẩu:</p>
        <p><a href="{reset_url}">Đặt lại mật khẩu</a></p>
        <p>Liên kết này sẽ hết hạn sau 1 giờ.</p>
        <p>Nếu bạn không yêu cầu khôi phục mật khẩu, vui lòng bỏ qua email này.</p>
        <p>Trân trọng,<br>Đội ngũ Roll Call by AI</p>
    """
    
    message = MessageSchema(
        subject="Khôi phục mật khẩu - Roll Call by AI",
        recipients=[email],
        body=html,
        subtype="html"
    )
    
    # Gửi email
    fastmail = FastMail(conf)
    await fastmail.send_message(message) 