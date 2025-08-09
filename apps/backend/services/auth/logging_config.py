import logging
import json
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = record.created
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

def setup_logging():
    """
    Sets up structured JSON logging for the application.
    """
    # Configure the root logger to catch all logs
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Standard stream handler for general logs (non-JSON for easy local dev reading)
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(stream_formatter)

    # Avoid adding handlers if they already exist
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(stream_handler)

    # Configure the audit logger for structured JSON logs
    audit_logger = logging.getLogger('audit')
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False # Prevent audit logs from going to the root logger's handlers

    # JSON handler for audit logs
    json_handler = logging.StreamHandler()
    # Format: {"timestamp": "...", "level": "INFO", "message": "...", "extra_key": "value"}
    formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(message)s')
    json_handler.setFormatter(formatter)

    if not any(isinstance(h, logging.StreamHandler) for h in audit_logger.handlers):
        audit_logger.addHandler(json_handler)
