"""
Notification background tasks for user communications, alerts, and reminders.
Handles email notifications, study reminders, and system alerts.
"""

import asyncio
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.tasks.celery_app import celery_app
from app.core.database import AsyncSessionLocal
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

@celery_app.task(bind=True, max_retries=3, default_retry_delay=300)
def send_daily_summaries(self):
    """Send daily study summaries to users"""
    try:
        return asyncio.run(_send_daily_summaries())
    except Exception as exc:
        logger.error(f"Daily summaries failed: {exc}")
        raise self.retry(exc=exc)

async def _send_daily_summaries():
    """Send daily study summaries to active users"""
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import text
            
            # Get users who want daily summaries and were active yesterday
            yesterday = date.today() - timedelta(days=1)
            
            query = text("""
                SELECT DISTINCT u.id, u.email, u.full_name,
                       dua.questions_attempted, dua.correct_answers, 
                       dua.study_time_minutes, dua.accuracy_rate
                FROM users u
                INNER JOIN user_preferences up ON u.id = up.user_id
                INNER JOIN daily_user_activities dua ON u.id = dua.user_id
                WHERE up.email_notifications = true
                AND u.is_active = true
                AND dua.date = :yesterday
                AND dua.questions_attempted > 0
            """)
            
            result = await db.execute(query, {"yesterday": yesterday})
            users = result.fetchall()
            
            sent_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    user_id, email, name, questions, correct, study_time, accuracy = user
                    
                    # Prepare summary data
                    summary_data = {
                        "name": name or "Student",
                        "date": yesterday.strftime("%B %d, %Y"),
                        "questions_attempted": questions,
                        "correct_answers": correct,
                        "study_time_minutes": study_time,
                        "accuracy_rate": round(accuracy, 1)
                    }
                    
                    # Send email
                    await _send_daily_summary_email(email, summary_data)
                    sent_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to send daily summary to {email}: {e}")
                    failed_count += 1
            
            logger.info(f"Daily summaries: {sent_count} sent, {failed_count} failed")
            
            return {
                "status": "completed",
                "sent_count": sent_count,
                "failed_count": failed_count,
                "date": yesterday.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending daily summaries: {e}")
            raise e

async def _send_daily_summary_email(email: str, summary_data: Dict[str, Any]):
    """Send daily summary email to a user"""
    subject = f"Your Daily Study Summary - {summary_data['date']}"
    
    # Create HTML email content
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">Daily Study Summary</h1>
                <p style="color: white; margin: 5px 0;">Keep up the great work, {summary_data['name']}!</p>
            </div>
            
            <div style="padding: 30px 20px;">
                <h2 style="color: #333;">Your Progress for {summary_data['date']}</h2>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0;">
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #667eea; margin: 0; font-size: 24px;">{summary_data['questions_attempted']}</h3>
                        <p style="margin: 5px 0; color: #666;">Questions Attempted</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #28a745; margin: 0; font-size: 24px;">{summary_data['correct_answers']}</h3>
                        <p style="margin: 5px 0; color: #666;">Correct Answers</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #ffc107; margin: 0; font-size: 24px;">{summary_data['accuracy_rate']}%</h3>
                        <p style="margin: 5px 0; color: #666;">Accuracy Rate</p>
                    </div>
                    
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center;">
                        <h3 style="color: #17a2b8; margin: 0; font-size: 24px;">{summary_data['study_time_minutes']}</h3>
                        <p style="margin: 5px 0; color: #666;">Minutes Studied</p>
                    </div>
                </div>
                
                <div style="background: #e9ecef; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">Tomorrow's Goal</h3>
                    <p style="color: #666; margin-bottom: 0;">
                        Continue your learning streak! Try to maintain or improve your accuracy rate.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/dashboard" 
                       style="background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        View Full Dashboard
                    </a>
                </div>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px;">
                <p>You're receiving this because you have daily summaries enabled.</p>
                <a href="{settings.FRONTEND_URL}/settings" style="color: #667eea;">Update preferences</a>
            </div>
        </body>
    </html>
    """
    
    await _send_email(email, subject, html_content)

@celery_app.task(bind=True, max_retries=3)
def send_study_reminders(self):
    """Send study reminders to users based on their preferences"""
    try:
        return asyncio.run(_send_study_reminders())
    except Exception as exc:
        logger.error(f"Study reminders failed: {exc}")
        raise self.retry(exc=exc)

async def _send_study_reminders():
    """Send study reminders to users"""
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import text
            
            # Get current time and day
            now = datetime.utcnow()
            current_time = now.strftime("%H:%M")
            
            # Find users who want reminders at this time
            query = text("""
                SELECT u.id, u.email, u.full_name, up.daily_question_goal
                FROM users u
                INNER JOIN user_preferences up ON u.id = up.user_id
                WHERE up.study_reminder_enabled = true
                AND up.study_reminder_time = :current_time
                AND u.is_active = true
                AND u.id NOT IN (
                    SELECT DISTINCT user_id 
                    FROM daily_user_activities 
                    WHERE date = CURRENT_DATE
                    AND questions_attempted >= up.daily_question_goal
                )
            """)
            
            result = await db.execute(query, {"current_time": current_time})
            users = result.fetchall()
            
            sent_count = 0
            for user in users:
                try:
                    user_id, email, name, goal = user
                    await _send_study_reminder_email(email, name or "Student", goal)
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send reminder to {email}: {e}")
            
            return {
                "status": "completed",
                "reminders_sent": sent_count,
                "time": current_time
            }
            
        except Exception as e:
            logger.error(f"Error sending study reminders: {e}")
            raise e

async def _send_study_reminder_email(email: str, name: str, daily_goal: int):
    """Send study reminder email"""
    subject = "Time for your daily study session! 📚"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: #667eea; padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">📚 Study Time!</h1>
            </div>
            
            <div style="padding: 30px 20px; text-align: center;">
                <h2 style="color: #333;">Hi {name}! Ready to learn?</h2>
                
                <p style="font-size: 18px; color: #666; margin: 20px 0;">
                    Your daily goal is <strong>{daily_goal} questions</strong>. 
                    Let's keep your learning streak going!
                </p>
                
                <a href="{settings.FRONTEND_URL}/practice" 
                   style="background: #28a745; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-size: 16px; margin: 20px 0;">
                    Start Practicing Now
                </a>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">💡 Study Tip</h3>
                    <p style="color: #666; margin-bottom: 0;">
                        Consistent daily practice is more effective than long, infrequent study sessions.
                    </p>
                </div>
            </div>
        </body>
    </html>
    """
    
    await _send_email(email, subject, html_content)

@celery_app.task(bind=True, max_retries=3)
def send_achievement_notification(self, user_id: int, achievement_type: str, achievement_data: Dict[str, Any]):
    """Send achievement notification to user"""
    try:
        return asyncio.run(_send_achievement_notification(user_id, achievement_type, achievement_data))
    except Exception as exc:
        logger.error(f"Achievement notification failed: {exc}")
        raise self.retry(exc=exc)

async def _send_achievement_notification(user_id: int, achievement_type: str, achievement_data: Dict[str, Any]):
    """Send achievement notification"""
    async with AsyncSessionLocal() as db:
        try:
            from sqlalchemy import text
            
            # Get user details
            user_query = text("""
                SELECT u.email, u.full_name, up.notifications_enabled
                FROM users u
                LEFT JOIN user_preferences up ON u.id = up.user_id
                WHERE u.id = :user_id AND u.is_active = true
            """)
            
            result = await db.execute(user_query, {"user_id": user_id})
            user = result.fetchone()
            
            if not user or not user[2]:  # notifications_enabled
                return {"status": "skipped", "reason": "Notifications disabled"}
            
            email, name, _ = user
            await _send_achievement_email(email, name or "Student", achievement_type, achievement_data)
            
            return {
                "status": "sent",
                "user_id": user_id,
                "achievement_type": achievement_type
            }
            
        except Exception as e:
            logger.error(f"Error sending achievement notification: {e}")
            raise e

async def _send_achievement_email(email: str, name: str, achievement_type: str, data: Dict[str, Any]):
    """Send achievement congratulations email"""
    
    # Achievement templates
    achievements = {
        "streak_milestone": {
            "title": "🔥 Study Streak Milestone!",
            "message": f"Congratulations! You've maintained a {data.get('days', 0)}-day study streak!"
        },
        "accuracy_milestone": {
            "title": "🎯 Accuracy Achievement!",
            "message": f"Amazing! You achieved {data.get('accuracy', 0)}% accuracy!"
        },
        "questions_milestone": {
            "title": "📈 Question Milestone!",
            "message": f"Incredible! You've answered {data.get('total_questions', 0)} questions!"
        }
    }
    
    achievement = achievements.get(achievement_type, {
        "title": "🏆 Achievement Unlocked!",
        "message": "Congratulations on your progress!"
    })
    
    subject = f"{achievement['title']} - {name}"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%); padding: 20px; text-align: center;">
                <h1 style="color: #333; margin: 0; font-size: 28px;">{achievement['title']}</h1>
            </div>
            
            <div style="padding: 30px 20px; text-align: center;">
                <h2 style="color: #333;">Way to go, {name}! 🎉</h2>
                
                <p style="font-size: 18px; color: #666; margin: 20px 0;">
                    {achievement['message']}
                </p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-top: 0;">Keep it up!</h3>
                    <p style="color: #666; margin-bottom: 0;">
                        Your dedication to learning is paying off. Continue practicing to reach even greater heights!
                    </p>
                </div>
                
                <a href="{settings.FRONTEND_URL}/dashboard" 
                   style="background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0;">
                    View Your Progress
                </a>
            </div>
        </body>
    </html>
    """
    
    await _send_email(email, subject, html_content)

async def _send_email(to_email: str, subject: str, html_content: str):
    """Send email using SMTP"""
    try:
        # Email configuration from settings
        smtp_server = getattr(settings, 'SMTP_SERVER', 'localhost')
        smtp_port = getattr(settings, 'SMTP_PORT', 587)
        smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        from_email = getattr(settings, 'FROM_EMAIL', 'noreply@papa.com')
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # Add HTML content
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_username and smtp_password:
                server.starttls()
                server.login(smtp_username, smtp_password)
            
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        raise e

# Export task functions
__all__ = [
    "send_daily_summaries",
    "send_study_reminders", 
    "send_achievement_notification"
]
