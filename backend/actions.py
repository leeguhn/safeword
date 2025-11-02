"""
Actions to trigger when safe word is detected.
"""
import os
from datetime import datetime
from typing import Dict, List, Optional
from audio_utils import start_recording_to_file, encrypt_file

# TODO: Uncomment and configure when ready to use
# from twilio.rest import Client
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email.mime.text import MIMEText
# from email import encoders


class ActionManager:
    """Manages actions triggered by safe word detection."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize action manager with configuration.
        
        Args:
            config: Configuration dict with keys:
                - record_duration: seconds to record (default 30)
                - encrypt_recordings: whether to encrypt (default True)
                - recordings_dir: where to save recordings
                - contacts: list of contact dicts with 'phone' and/or 'email'
                - grace_period: seconds before triggering (default 0)
        """
        self.config = config or {}
        self.recordings_dir = self.config.get('recordings_dir', 'data/recordings')
        self.record_duration = self.config.get('record_duration', 30)
        self.encrypt_recordings = self.config.get('encrypt_recordings', True)
        self.contacts = self.config.get('contacts', [])
        self.grace_period = self.config.get('grace_period', 0)
        
        # Create recordings directory
        os.makedirs(self.recordings_dir, exist_ok=True)
        
        # Track recent triggers to avoid spam
        self.last_trigger_time: Optional[float] = None
        self.min_trigger_interval = 60  # seconds
    
    def trigger_actions(self) -> Dict[str, any]:
        """
        Execute all configured actions when safe word is detected.
        
        Returns:
            Dict with results of each action
        """
        import time
        
        # Check if we're in cooldown period
        if self.last_trigger_time:
            elapsed = time.time() - self.last_trigger_time
            if elapsed < self.min_trigger_interval:
                return {
                    'triggered': False,
                    'reason': f'Cooldown active ({int(self.min_trigger_interval - elapsed)}s remaining)'
                }
        
        print("\n" + "="*50)
        print("SAFE WORD DETECTED - TRIGGERING ACTIONS")
        print("="*50 + "\n")
        
        self.last_trigger_time = time.time()
        
        results = {
            'triggered': True,
            'timestamp': datetime.now().isoformat(),
            'actions': {}
        }
        
        # Action 1: Record audio
        recording_result = self._record_audio()
        results['actions']['recording'] = recording_result
        
        # Action 2: Encrypt recording if enabled and recording succeeded
        if self.encrypt_recordings and recording_result.get('success'):
            encryption_result = self._encrypt_recording(recording_result['path'])
            results['actions']['encryption'] = encryption_result
        
        # Action 3: Send alerts (SMS/Email) - placeholder
        if self.contacts:
            alert_results = self._send_alerts(recording_result.get('path'))
            results['actions']['alerts'] = alert_results
        
        # Action 4: Log event
        self._log_event(results)
        
        return results
    
    def _record_audio(self) -> Dict[str, any]:
        """Record audio clip when alert is triggered."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'alert_{timestamp}.wav'
        filepath = os.path.join(self.recordings_dir, filename)
        
        print(f"Recording {self.record_duration}s audio clip...")
        result = start_recording_to_file(self.record_duration, filepath)
        
        if result['success']:
            print(f"✓ Recording saved: {filepath}")
        else:
            print(f"✗ Recording failed: {result.get('error')}")
        
        return result
    
    def _encrypt_recording(self, file_path: str) -> Dict[str, any]:
        """Encrypt a recording file."""
        encryption_key = os.getenv('ENCRYPTION_KEY', 'default-key-change-me')
        
        print(f"Encrypting recording...")
        result = encrypt_file(file_path, encryption_key)
        
        if result['success']:
            print(f"✓ Recording encrypted: {result['encrypted_path']}")
        else:
            print(f"✗ Encryption failed: {result.get('error')}")
        
        return result
    
    def _send_alerts(self, recording_path: Optional[str] = None) -> List[Dict[str, any]]:
        """
        Send alerts to configured contacts.
        
        TODO: Implement SMS via Twilio and Email via SMTP.
        This is a placeholder implementation.
        """
        results = []
        
        for contact in self.contacts:
            if 'phone' in contact:
                # SMS via Twilio (placeholder)
                sms_result = self._send_sms(
                    contact['phone'],
                    "ALERT: Safe word detected!",
                    recording_path
                )
                results.append({
                    'type': 'sms',
                    'recipient': contact['phone'],
                    'result': sms_result
                })
            
            if 'email' in contact:
                # Email via SMTP (placeholder)
                email_result = self._send_email(
                    contact['email'],
                    "ALERT: Safe word detected!",
                    recording_path
                )
                results.append({
                    'type': 'email',
                    'recipient': contact['email'],
                    'result': email_result
                })
        
        return results
    
    def _send_sms(self, phone: str, message: str, attachment_path: Optional[str] = None) -> Dict[str, any]:
        """
        Send SMS via Twilio.
        
        TODO: Implement when Twilio credentials are configured.
        """
        print(f"TODO: Send SMS to {phone}: {message}")
        
        # Placeholder implementation
        return {
            'success': False,
            'error': 'SMS sending not yet implemented. Configure Twilio credentials in .env'
        }
        
        # Uncomment when ready:
        # try:
        #     account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        #     auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        #     from_number = os.getenv('TWILIO_FROM_NUMBER')
        #     
        #     client = Client(account_sid, auth_token)
        #     
        #     message = client.messages.create(
        #         body=message,
        #         from_=from_number,
        #         to=phone
        #     )
        #     
        #     return {'success': True, 'message_sid': message.sid}
        # except Exception as e:
        #     return {'success': False, 'error': str(e)}
    
    def _send_email(self, email: str, subject: str, attachment_path: Optional[str] = None) -> Dict[str, any]:
        """
        Send email via SMTP.
        
        TODO: Implement when SMTP credentials are configured.
        """
        print(f"TODO: Send email to {email}: {subject}")
        
        # Placeholder implementation
        return {
            'success': False,
            'error': 'Email sending not yet implemented. Configure SMTP credentials in .env'
        }
        
        # Uncomment when ready:
        # try:
        #     smtp_server = os.getenv('SMTP_SERVER')
        #     smtp_port = int(os.getenv('SMTP_PORT', 587))
        #     smtp_username = os.getenv('SMTP_USERNAME')
        #     smtp_password = os.getenv('SMTP_PASSWORD')
        #     
        #     msg = MIMEMultipart()
        #     msg['From'] = smtp_username
        #     msg['To'] = email
        #     msg['Subject'] = subject
        #     
        #     body = "Safe word was detected. Alert triggered."
        #     msg.attach(MIMEText(body, 'plain'))
        #     
        #     # Attach recording if provided
        #     if attachment_path and os.path.exists(attachment_path):
        #         with open(attachment_path, 'rb') as f:
        #             part = MIMEBase('application', 'octet-stream')
        #             part.set_payload(f.read())
        #             encoders.encode_base64(part)
        #             part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_path)}')
        #             msg.attach(part)
        #     
        #     server = smtplib.SMTP(smtp_server, smtp_port)
        #     server.starttls()
        #     server.login(smtp_username, smtp_password)
        #     server.send_message(msg)
        #     server.quit()
        #     
        #     return {'success': True}
        # except Exception as e:
        #     return {'success': False, 'error': str(e)}
    
    def _log_event(self, results: Dict) -> None:
        """Log detection event to file."""
        log_file = os.path.join(self.recordings_dir, 'events.log')
        
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Timestamp: {results['timestamp']}\n")
            f.write(f"Triggered: {results['triggered']}\n")
            
            for action, result in results.get('actions', {}).items():
                f.write(f"{action}: {result}\n")
            
            f.write(f"{'='*50}\n")
        
        print(f"✓ Event logged to {log_file}")


# Global action manager instance
action_manager = ActionManager()
