from typing import List, Dict
import random
from uuid import UUID


class RecommendationEngine:
    """
    Simple collaborative filtering + content-based recommendation engine
    """
    
    def __init__(self):
        self.algorithm = "hybrid"
    
    def generate_recommendations(
        self,
        user_preferences: dict,
        watch_history: List,
        available_content: List[dict],
        limit: int = 20
    ) -> List[dict]:
        """
        Generate personalized recommendations based on user preferences and history
        """
        scored_content = []
        
        for content in available_content:
            score = self._calculate_content_score(
                content,
                user_preferences,
                watch_history
            )
            
            if score > 0:
                scored_content.append({
                    **content,
                    "match_score": score,
                    "reason": self._generate_reason(content, user_preferences)
                })
        
        # Sort by score and return top N
        scored_content.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_content[:limit]
    
    def _calculate_content_score(
        self,
        content: dict,
        user_preferences: dict,
        watch_history: List
    ) -> float:
        """
        Calculate a match score for content based on user preferences
        """
        score = 0.0
        
        # Genre matching (40% weight)
        preferred_genres = user_preferences.get("preferred_genres", [])
        disliked_genres = user_preferences.get("disliked_genres", [])
        content_genres = content.get("genre", [])
        
        if any(genre in preferred_genres for genre in content_genres):
            score += 0.4
        
        if any(genre in disliked_genres for genre in content_genres):
            score -= 0.3
        
        # Director matching (20% weight)
        favorite_directors = user_preferences.get("favorite_directors", [])
        if content.get("director") in favorite_directors:
            score += 0.2
        
        # Rating boost (20% weight)
        rating = content.get("rating", 0)
        if rating >= 8.0:
            score += 0.2
        elif rating >= 7.0:
            score += 0.1
        
        # Language matching (10% weight)
        preferred_languages = user_preferences.get("preferred_languages", [])
        if content.get("language") in preferred_languages:
            score += 0.1
        
        # Watch history weights (10% weight)
        watch_weights = user_preferences.get("watch_history_weights", {})
        content_genre = content.get("genre", [""])[0] if content.get("genre") else ""
        if content_genre in watch_weights:
            score += watch_weights[content_genre] * 0.1
        
        # Penalize already watched content
        watched_content_ids = [h.content_id for h in watch_history]
        if content.get("id") in watched_content_ids:
            score -= 0.5
        
        return max(0, score)
    
    def _generate_reason(self, content: dict, user_preferences: dict) -> str:
        """
        Generate a human-readable reason for the recommendation
        """
        reasons = []
        
        preferred_genres = user_preferences.get("preferred_genres", [])
        content_genres = content.get("genre", [])
        
        if any(genre in preferred_genres for genre in content_genres):
            matching_genres = set(content_genres) & set(preferred_genres)
            reasons.append(f"Because you like {', '.join(matching_genres)}")
        
        favorite_directors = user_preferences.get("favorite_directors", [])
        if content.get("director") in favorite_directors:
            reasons.append(f"Directed by {content.get('director')}")
        
        rating = content.get("rating", 0)
        if rating >= 8.0:
            reasons.append(f"Highly rated ({rating}/10)")
        
        return reasons[0] if reasons else "Popular choice"


recommendation_engine = RecommendationEngine()
