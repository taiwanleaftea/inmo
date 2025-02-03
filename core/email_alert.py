import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

def send_alert(new_count, listings_html, email_config):
    """Send HTML email with new listings"""
    try:
        msg = MIMEMultipart()
        msg['Subject'] = f"🚨 {new_count} New Rental Listing{'s' if new_count > 1 else ''} Found!"
        msg['From'] = email_config['sender']
        msg['To'] = email_config['receiver']

        body = f"""
        <h2>{new_count} New Listings Found</h2>
        {listings_html}
        <p><em>Automated alert from Rental Scraper</em></p>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
            server.starttls()
            server.login(email_config['sender'], email_config['password'])
            server.send_message(msg)
            
        logging.info("Email alert sent successfully")
        
    except Exception as e:
        logging.error(f"Email failed: {str(e)}")