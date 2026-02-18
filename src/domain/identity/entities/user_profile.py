from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any

from src.domain.shared.entity import Entity
from ..value_objects.user_id import UserId

@dataclass
class UserProfile(Entity):
    user_id: UserId
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Override id to use strong generic Entity ID or specific profile ID
    # For now utilizing the default Entity ID factory
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
        
    def update_info(self, first_name: Optional[str] = None, last_name: Optional[str] = None, bio: Optional[str] = None, avatar_url: Optional[str] = None) -> None:
        if first_name:
            self.first_name = first_name
        if last_name:
            self.last_name = last_name
        if bio is not None:
             self.bio = bio
        if avatar_url is not None:
            self.avatar_url = avatar_url
        self.updated_at = datetime.now()

    def update_preferences(self, preferences: Dict[str, Any]) -> None:
        self.preferences.update(preferences)
        self.updated_at = datetime.now()
