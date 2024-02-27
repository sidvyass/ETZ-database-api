import logging
from connection import get_connection
import time

logger = logging.getLogger().getChild("MAIL")

def send_mail(subject, body, recipient):
    """Sends an email using the database inbuilt function. Done using SQL query"""
    t_sql_command = f"""
    EXEC msdb.dbo.sp_send_dbmail @profile_name = "MIE Notifications",
                        @recipients = "{recipient}",
                        @subject = "{subject}",
                        @body = "{body}";
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(t_sql_command)

        logger.info(f"Email command executed. Recipient -> {recipient}. SENT STATUS PENDING")

        time.sleep(5)  # we check the status after 5 seconds
        query = "SELECT IDENT_CURRENT('msdb.dbo.sysmail_allitems')"
        cursor.execute(query)
        pk = cursor.fetchone()[0]
        sent_status_query = "SELECT sent_status FROM msdb.dbo.sysmail_allitems WHERE mailitem_id = ?"
        cursor.execute(sent_status_query, pk)
        
        status = cursor.fetchone()[0] 
        if status == "sent":
            logger.info(f"Eamil Sent. SENT STATUS CONFIRMED")
        elif status == "failed":
            logger.error(f"Email failed. recipient: {recipient}")
        else:
            logger.critical("Unknown error. Message not delivered")
