"""
Initialization Service - Handles app startup tasks
"""

from sqlmodel import select

from models import Channel

from .base import BaseService


class InitializationService(BaseService):
    """Service for handling application initialization tasks."""

    def ensure_default_channels(self):
        """Ensure default channels exist in database."""
        try:
            for name in ["Airbnb", "Offline"]:
                exists = self.session.exec(
                    select(Channel).where(Channel.channel_name == name)
                ).first()

                if not exists:
                    channel = Channel(channel_name=name)
                    self.session.add(channel)

            self.session.commit()

            return self.success_response(
                {
                    "message": "Default channels ensured",
                    "channels": ["Airbnb", "Offline"],
                }
            )

        except Exception as e:
            self.session.rollback()
            return self.error_response(f"Failed to ensure channels: {str(e)}")

    def get_total_properties(self):
        """Get total property count."""
        try:
            from sqlmodel import func

            from models import Property

            count = self.session.exec(select(func.count(Property.id))).one()

            return self.success_response({"total_properties": count})

        except Exception as e:
            return self.error_response(f"Failed to get property count: {str(e)}")
