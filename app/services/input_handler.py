from app.models.schemas import IncomingMessage


class InputHandler:

    @staticmethod
    def process(form_data) -> IncomingMessage:
        body = form_data.get("Body")
        media_url = form_data.get("MediaUrl0")
        sender = form_data.get("From")

        if media_url:
            message_type = "audio"
        else:
            message_type = "text"

        return IncomingMessage(
            sender=sender,
            message_type=message_type,
            text=body if message_type == "text" else None,
            media_url=media_url if message_type == "audio" else None
        )

    # app/services/input_handler.py
    