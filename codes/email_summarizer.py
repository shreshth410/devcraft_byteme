"""
Email and Notice Summarizer for Campus Copilot
Summarizes long emails, notices, and announcements
"""

import logging
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailSummarizer:
    """Summarize emails, notices, and announcements"""
    
    def __init__(self):
        """Initialize email summarizer"""
        self.max_summary_length = 200  # Maximum words in summary
        self.key_sections = [
            "important", "deadline", "action required", "urgent",
            "reminder", "announcement", "notice", "update"
        ]
        
    def summarize_email(self, email_content: str, sender: str = "", 
                       subject: str = "") -> Dict[str, Any]:
        """Summarize an email
        
        Args:
            email_content: Full email content
            sender: Email sender (optional)
            subject: Email subject (optional)
            
        Returns:
            Dictionary containing summary and metadata
        """
        try:
            # Clean and preprocess the email content
            cleaned_content = self._clean_email_content(email_content)
            
            # Extract key information
            key_info = self._extract_key_information(cleaned_content)
            
            # Generate summary
            summary = self._generate_summary(cleaned_content)
            
            # Extract action items
            action_items = self._extract_action_items(cleaned_content)
            
            # Extract dates and deadlines
            dates = self._extract_dates(cleaned_content)
            
            # Determine priority level
            priority = self._determine_priority(cleaned_content, subject)
            
            result = {
                "summary": summary,
                "key_points": key_info,
                "action_items": action_items,
                "important_dates": dates,
                "priority": priority,
                "sender": sender,
                "subject": subject,
                "word_count": len(cleaned_content.split()),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Email summarized successfully. Priority: {priority}")
            return result
            
        except Exception as e:
            logger.error(f"Error summarizing email: {e}")
            return {
                "summary": "Error: Could not summarize email",
                "error": str(e)
            }
    
    def summarize_notice(self, notice_content: str, title: str = "") -> Dict[str, Any]:
        """Summarize a college notice or announcement
        
        Args:
            notice_content: Full notice content
            title: Notice title (optional)
            
        Returns:
            Dictionary containing summary and metadata
        """
        try:
            # Clean content
            cleaned_content = self._clean_notice_content(notice_content)
            
            # Extract key information specific to notices
            key_info = self._extract_notice_key_info(cleaned_content)
            
            # Generate summary
            summary = self._generate_summary(cleaned_content)
            
            # Extract deadlines and important dates
            dates = self._extract_dates(cleaned_content)
            
            # Extract affected groups (students, faculty, etc.)
            affected_groups = self._extract_affected_groups(cleaned_content)
            
            # Determine urgency
            urgency = self._determine_urgency(cleaned_content, title)
            
            result = {
                "summary": summary,
                "key_points": key_info,
                "important_dates": dates,
                "affected_groups": affected_groups,
                "urgency": urgency,
                "title": title,
                "word_count": len(cleaned_content.split()),
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"Notice summarized successfully. Urgency: {urgency}")
            return result
            
        except Exception as e:
            logger.error(f"Error summarizing notice: {e}")
            return {
                "summary": "Error: Could not summarize notice",
                "error": str(e)
            }
    
    def _clean_email_content(self, content: str) -> str:
        """Clean email content by removing headers, signatures, etc."""
        # Remove email headers
        content = re.sub(r'^(From|To|Subject|Date|CC|BCC):.*$', '', content, flags=re.MULTILINE)
        
        # Remove email signatures (common patterns)
        content = re.sub(r'\n--\s*\n.*$', '', content, flags=re.DOTALL)
        content = re.sub(r'\nBest regards.*$', '', content, flags=re.DOTALL)
        content = re.sub(r'\nSincerely.*$', '', content, flags=re.DOTALL)
        
        # Remove excessive whitespace
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()
        
        return content
    
    def _clean_notice_content(self, content: str) -> str:
        """Clean notice content"""
        # Remove excessive whitespace and formatting
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'\s+', ' ', content)
        content = content.strip()
        
        return content
    
    def _extract_key_information(self, content: str) -> List[str]:
        """Extract key information from content"""
        key_points = []
        
        # Look for sentences containing key terms
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in self.key_sections):
                if len(sentence) > 10:  # Avoid very short fragments
                    key_points.append(sentence + '.')
        
        # Limit to top 5 key points
        return key_points[:5]
    
    def _extract_notice_key_info(self, content: str) -> List[str]:
        """Extract key information specific to notices"""
        key_points = []
        
        # Look for policy changes, new procedures, etc.
        notice_keywords = [
            "policy", "procedure", "requirement", "mandatory", "optional",
            "new", "change", "update", "effective", "implementation"
        ]
        
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(keyword in sentence.lower() for keyword in notice_keywords):
                if len(sentence) > 10:
                    key_points.append(sentence + '.')
        
        return key_points[:5]
    
    def _generate_summary(self, content: str) -> str:
        """Generate a concise summary of the content"""
        # Simple extractive summarization
        sentences = content.split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if not sentences:
            return "No substantial content to summarize."
        
        # Take first few sentences and most important ones
        summary_sentences = []
        
        # Always include the first sentence
        if sentences:
            summary_sentences.append(sentences[0])
        
        # Add sentences with key terms
        for sentence in sentences[1:]:
            if len(' '.join(summary_sentences).split()) >= self.max_summary_length:
                break
            if any(keyword in sentence.lower() for keyword in self.key_sections):
                summary_sentences.append(sentence)
        
        # If still under limit, add more sentences
        for sentence in sentences:
            if len(' '.join(summary_sentences).split()) >= self.max_summary_length:
                break
            if sentence not in summary_sentences:
                summary_sentences.append(sentence)
        
        summary = '. '.join(summary_sentences[:3])  # Limit to 3 sentences
        return summary + '.' if not summary.endswith('.') else summary
    
    def _extract_action_items(self, content: str) -> List[str]:
        """Extract action items from content"""
        action_items = []
        
        # Look for action-oriented phrases
        action_patterns = [
            r'please\s+\w+',
            r'you\s+must\s+\w+',
            r'required\s+to\s+\w+',
            r'need\s+to\s+\w+',
            r'should\s+\w+',
            r'submit\s+\w+',
            r'complete\s+\w+',
            r'register\s+\w+',
            r'attend\s+\w+'
        ]
        
        sentences = content.split('.')
        for sentence in sentences:
            sentence = sentence.strip()
            if any(re.search(pattern, sentence.lower()) for pattern in action_patterns):
                if len(sentence) > 10:
                    action_items.append(sentence + '.')
        
        return action_items[:3]  # Limit to top 3 action items
    
    def _extract_dates(self, content: str) -> List[str]:
        """Extract dates and deadlines from content"""
        dates = []
        
        # Common date patterns
        date_patterns = [
            r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # MM/DD/YYYY or MM-DD-YYYY
            r'\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{2,4}\b',
            r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{2,4}\b',
            r'\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),?\s+\w+\s+\d{1,2}\b'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            dates.extend(matches)
        
        # Remove duplicates and limit
        unique_dates = list(set(dates))
        return unique_dates[:5]
    
    def _extract_affected_groups(self, content: str) -> List[str]:
        """Extract groups affected by the notice"""
        groups = []
        
        group_keywords = [
            "students", "faculty", "staff", "undergraduate", "graduate",
            "freshmen", "sophomores", "juniors", "seniors", "alumni",
            "department", "college", "university", "administration"
        ]
        
        for keyword in group_keywords:
            if keyword in content.lower():
                groups.append(keyword.title())
        
        return list(set(groups))
    
    def _determine_priority(self, content: str, subject: str = "") -> str:
        """Determine priority level of email"""
        high_priority_keywords = [
            "urgent", "immediate", "asap", "deadline", "important",
            "critical", "emergency", "action required"
        ]
        
        medium_priority_keywords = [
            "reminder", "notice", "update", "announcement", "please"
        ]
        
        text_to_check = (content + " " + subject).lower()
        
        if any(keyword in text_to_check for keyword in high_priority_keywords):
            return "High"
        elif any(keyword in text_to_check for keyword in medium_priority_keywords):
            return "Medium"
        else:
            return "Low"
    
    def _determine_urgency(self, content: str, title: str = "") -> str:
        """Determine urgency level of notice"""
        urgent_keywords = [
            "immediate", "urgent", "emergency", "critical", "deadline today",
            "expires", "last chance", "final notice"
        ]
        
        moderate_keywords = [
            "deadline", "due", "reminder", "important", "attention"
        ]
        
        text_to_check = (content + " " + title).lower()
        
        if any(keyword in text_to_check for keyword in urgent_keywords):
            return "Urgent"
        elif any(keyword in text_to_check for keyword in moderate_keywords):
            return "Moderate"
        else:
            return "Low"
    
    def format_summary_for_telegram(self, summary_data: Dict[str, Any]) -> str:
        """Format summary for Telegram message"""
        try:
            formatted = f"📧 **Email Summary**\n\n"
            
            if summary_data.get("subject"):
                formatted += f"**Subject:** {summary_data['subject']}\n"
            if summary_data.get("sender"):
                formatted += f"**From:** {summary_data['sender']}\n"
            
            formatted += f"**Priority:** {summary_data.get('priority', 'Unknown')}\n\n"
            
            formatted += f"**Summary:**\n{summary_data.get('summary', 'No summary available')}\n\n"
            
            if summary_data.get("key_points"):
                formatted += "**Key Points:**\n"
                for point in summary_data["key_points"]:
                    formatted += f"• {point}\n"
                formatted += "\n"
            
            if summary_data.get("action_items"):
                formatted += "**Action Items:**\n"
                for item in summary_data["action_items"]:
                    formatted += f"🔸 {item}\n"
                formatted += "\n"
            
            if summary_data.get("important_dates"):
                formatted += "**Important Dates:**\n"
                for date in summary_data["important_dates"]:
                    formatted += f"📅 {date}\n"
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting summary: {e}")
            return "Error formatting summary"

def create_email_summarizer() -> EmailSummarizer:
    """Factory function to create email summarizer"""
    return EmailSummarizer()

