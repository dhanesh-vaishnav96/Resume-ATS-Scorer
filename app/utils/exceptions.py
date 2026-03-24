class ResumeIQException(Exception):
    """Base exception for all ResumeIQ errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ExtractionError(ResumeIQException):
    """Failed to extract text from PDF or job description."""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class ScoringError(ResumeIQException):
    """Failed to calculate scores."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class AIProviderError(ResumeIQException):
    """Error from external AI provider (Gemini)."""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)

class RateLimitError(ResumeIQException):
    """API rate limit exceeded."""
    def __init__(self, message: str):
        super().__init__(message, status_code=429)

class ValidationError(ResumeIQException):
    """Input data validation failed."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)
