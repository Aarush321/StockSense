import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

class EmailService:
    def __init__(self):
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY', '')
        self.smtp_host = os.getenv('SMTP_HOST', '')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@stocksense.com')
        # Use frontend URL for email links (Netlify URL in production)
        self.app_url = os.getenv('FRONTEND_URL', os.getenv('APP_URL', 'http://localhost:5001'))
        
    def send_email(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email using SendGrid or SMTP"""
        # Try SendGrid first
        if self.sendgrid_api_key and 'your_' not in self.sendgrid_api_key:
            try:
                return self._send_via_sendgrid(to_email, subject, html_content, text_content)
            except Exception as e:
                print(f"SendGrid email error: {e}")
        
        # Fallback to SMTP
        if self.smtp_host and self.smtp_user and self.smtp_password:
            try:
                return self._send_via_smtp(to_email, subject, html_content, text_content)
            except Exception as e:
                print(f"SMTP email error: {e}")
        
        # If no email service configured, just log (for development)
        print(f"Email service not configured. Would send to {to_email}: {subject}")
        return False
    
    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email via SendGrid API"""
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=self.from_email,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            if text_content:
                message.plain_text_content = text_content
            
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            return response.status_code in [200, 201, 202]
        except Exception as e:
            print(f"SendGrid error: {e}")
            return False
    
    def _send_via_smtp(self, to_email: str, subject: str, html_content: str, text_content: str = None) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            print(f"SMTP error: {e}")
            return False
    
    def send_verification_email(self, to_email: str, verification_token: str) -> bool:
        """Send email verification email"""
        # Use frontend URL with verify-email route
        verification_url = f"{self.app_url}/verify-email?token={verification_token}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #1f2937;">Verify Your Email</h1>
                    <p>Thank you for signing up for StockSense!</p>
                    <p>Please click the button below to verify your email address:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{verification_url}" style="background-color: #1f2937; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Verify Email</a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #6b7280;">{verification_url}</p>
                    <p style="margin-top: 30px; font-size: 12px; color: #6b7280;">This link will expire in 24 hours.</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        Verify Your Email
        
        Thank you for signing up for StockSense!
        
        Please click the link below to verify your email address:
        {verification_url}
        
        This link will expire in 24 hours.
        """
        
        return self.send_email(to_email, "Verify Your StockSense Email", html_content, text_content)
    
    def send_password_reset_email(self, to_email: str, reset_token: str) -> bool:
        """Send password reset email"""
        reset_url = f"{self.app_url}/reset-password?token={reset_token}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #1f2937;">Reset Your Password</h1>
                    <p>You requested to reset your password for StockSense.</p>
                    <p>Click the button below to reset your password:</p>
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="background-color: #1f2937; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Password</a>
                    </div>
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all; color: #6b7280;">{reset_url}</p>
                    <p style="margin-top: 30px; font-size: 12px; color: #6b7280;">This link will expire in 1 hour. If you didn't request this, please ignore this email.</p>
                </div>
            </body>
        </html>
        """
        
        text_content = f"""
        Reset Your Password
        
        You requested to reset your password for StockSense.
        
        Click the link below to reset your password:
        {reset_url}
        
        This link will expire in 1 hour. If you didn't request this, please ignore this email.
        """
        
        return self.send_email(to_email, "Reset Your StockSense Password", html_content, text_content)

