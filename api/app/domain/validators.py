"""Domain validators."""
import re
from typing import Optional
from app.core.logging import get_logger

logger = get_logger(__name__)


class PasswordValidator:
    """Password validation."""
    
    MIN_LENGTH = 8
    MAX_LENGTH = 128
    
    @classmethod
    def validate(cls, password: str) -> None:
        if not password:
            raise ValueError("Password is required")
        
        if len(password) < cls.MIN_LENGTH:
            raise ValueError(f"Password must be at least {cls.MIN_LENGTH} characters long")
        
        if len(password) > cls.MAX_LENGTH:
            raise ValueError(f"Password must be no more than {cls.MAX_LENGTH} characters long")


class EmailValidator:
    """Email validation."""
    
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    @classmethod
    def validate(cls, email: str) -> None:
        if not email:
            raise ValueError("Email is required")
        
        if not cls.EMAIL_REGEX.match(email):
            raise ValueError("Invalid email format")


class UsernameValidator:
    """Username validation."""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 50
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    @classmethod
    def validate(cls, username: str) -> None:
        if not username:
            raise ValueError("Username is required")
        
        if len(username) < cls.MIN_LENGTH:
            raise ValueError(f"Username must be at least {cls.MIN_LENGTH} characters long")
        
        if len(username) > cls.MAX_LENGTH:
            raise ValueError(f"Username must be no more than {cls.MAX_LENGTH} characters long")
        
        if not cls.USERNAME_REGEX.match(username):
            raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")


class UserValidator:
    """User entity validation."""
    
    @staticmethod
    def validate_create_data(user_data) -> None:
        EmailValidator.validate(user_data.email)
        UsernameValidator.validate(user_data.username)
        PasswordValidator.validate(user_data.password)
        if not user_data.full_name or not user_data.full_name.strip():
            raise ValueError("Full name is required")
        
        if len(user_data.full_name.strip()) < 2:
            raise ValueError("Full name must be at least 2 characters long")
        
        if len(user_data.full_name) > 255:
            raise ValueError("Full name must be no more than 255 characters long")
    
    @staticmethod
    def validate_update_data(user_data) -> None:
        if user_data.email is not None:
            EmailValidator.validate(user_data.email)
        
        if user_data.username is not None:
            UsernameValidator.validate(user_data.username)
        
        if user_data.password is not None and user_data.password.strip():
            PasswordValidator.validate(user_data.password)
        
        if user_data.full_name is not None:
            if not user_data.full_name.strip():
                raise ValueError("Full name cannot be empty")
            
            if len(user_data.full_name.strip()) < 2:
                raise ValueError("Full name must be at least 2 characters long")
            
            if len(user_data.full_name) > 255:
                raise ValueError("Full name must be no more than 255 characters long")


class PaginationValidator:
    """Pagination parameters validation."""
    
    MAX_LIMIT = 1000
    MIN_LIMIT = 1
    
    @classmethod
    def validate(cls, skip: int, limit: int) -> None:
        if skip < 0:
            raise ValueError("Skip must be non-negative")
        
        if limit < cls.MIN_LIMIT:
            raise ValueError(f"Limit must be at least {cls.MIN_LIMIT}")
        
        if limit > cls.MAX_LIMIT:
            raise ValueError(f"Limit must be no more than {cls.MAX_LIMIT}")


class FilterValidator:
    """Filter parameters validation."""
    
    MAX_SEARCH_LENGTH = 100
    MAX_COLOR_LENGTH = 50
    MAX_FEATURE_LENGTH = 50
    MAX_FEATURES_COUNT = 10
    
    @classmethod
    def validate_filters(cls, filters) -> None:
        """Validate filter parameters to prevent backend errors."""
        # Validate search term
        if filters.search is not None:
            if not isinstance(filters.search, str):
                raise ValueError("Search term must be a string")
            
            if len(filters.search) > cls.MAX_SEARCH_LENGTH:
                raise ValueError(f"Search term must be no more than {cls.MAX_SEARCH_LENGTH} characters long")
            
            if len(filters.search.strip()) == 0:
                raise ValueError("Search term cannot be empty")
        
        # Validate color filter (paint-specific)
        if hasattr(filters, 'color') and filters.color is not None:
            if not isinstance(filters.color, str):
                raise ValueError("Color filter must be a string")
            
            if len(filters.color) > cls.MAX_COLOR_LENGTH:
                raise ValueError(f"Color filter must be no more than {cls.MAX_COLOR_LENGTH} characters long")
            
            if len(filters.color.strip()) == 0:
                raise ValueError("Color filter cannot be empty")
        
        # Validate features filter (paint-specific)
        if hasattr(filters, 'features') and filters.features is not None:
            if not isinstance(filters.features, list):
                raise ValueError("Features filter must be a list")
            
            if len(filters.features) > cls.MAX_FEATURES_COUNT:
                raise ValueError(f"Features filter cannot have more than {cls.MAX_FEATURES_COUNT} items")
            
            for feature in filters.features:
                if not isinstance(feature, str):
                    raise ValueError("Each feature must be a string")
                
                if len(feature.strip()) == 0:
                    raise ValueError("Feature cannot be empty")
                
                if len(feature) > cls.MAX_FEATURE_LENGTH:
                    raise ValueError(f"Feature must be no more than {cls.MAX_FEATURE_LENGTH} characters long")
        
        # Validate enum filters (these should be validated by Pydantic, but let's be extra safe)
        if hasattr(filters, 'surface_types') and filters.surface_types is not None:
            from app.domain.entities import SurfaceType
            if not isinstance(filters.surface_types, list):
                raise ValueError("Surface types must be a list")
            for surface_type in filters.surface_types:
                if not isinstance(surface_type, SurfaceType):
                    raise ValueError("Invalid surface type")
        
        if hasattr(filters, 'environment') and filters.environment is not None:
            from app.domain.entities import Environment
            if not isinstance(filters.environment, Environment):
                raise ValueError("Invalid environment")
        
        if hasattr(filters, 'finish_type') and filters.finish_type is not None:
            from app.domain.entities import FinishType
            if not isinstance(filters.finish_type, FinishType):
                raise ValueError("Invalid finish type")
        
        if hasattr(filters, 'line') and filters.line is not None:
            from app.domain.entities import PaintLine
            if not isinstance(filters.line, PaintLine):
                raise ValueError("Invalid paint line")


class PaintValidator:
    """Paint entity validation."""
    
    MAX_NAME_LENGTH = 255
    MAX_COLOR_LENGTH = 100
    MAX_DESCRIPTION_LENGTH = 1000
    MAX_FEATURES = 20
    
    @classmethod
    def validate_paint_data(cls, paint_data) -> None:
        """Validate paint creation data."""
        if not paint_data.name or not paint_data.name.strip():
            raise ValueError("Paint name is required")
        
        if len(paint_data.name.strip()) < 2:
            raise ValueError("Paint name must be at least 2 characters long")
        
        if len(paint_data.name) > cls.MAX_NAME_LENGTH:
            raise ValueError(f"Paint name must be no more than {cls.MAX_NAME_LENGTH} characters long")
        
        if not paint_data.color or not paint_data.color.strip():
            raise ValueError("Paint color is required")
        
        if len(paint_data.color.strip()) < 2:
            raise ValueError("Paint color must be at least 2 characters long")
        
        if len(paint_data.color) > cls.MAX_COLOR_LENGTH:
            raise ValueError(f"Paint color must be no more than {cls.MAX_COLOR_LENGTH} characters long")
        
        if paint_data.description and len(paint_data.description) > cls.MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"Description must be no more than {cls.MAX_DESCRIPTION_LENGTH} characters long")
        
        if len(paint_data.features) > cls.MAX_FEATURES:
            raise ValueError(f"Features list cannot have more than {cls.MAX_FEATURES} items")
        
        # Validate features are not empty strings
        for feature in paint_data.features:
            if not feature or not feature.strip():
                raise ValueError("Feature cannot be empty")
        
        # Validate surface_types
        if not paint_data.surface_types or len(paint_data.surface_types) == 0:
            raise ValueError("At least one surface type is required")
        
        if len(paint_data.surface_types) > 10:  # Reasonable limit
            raise ValueError("Surface types list cannot have more than 10 items")
    
    @classmethod
    def validate_paint_update(cls, paint_data) -> None:
        """Validate paint update data."""
        if paint_data.name is not None:
            if not paint_data.name.strip():
                raise ValueError("Paint name cannot be empty")
            
            if len(paint_data.name.strip()) < 2:
                raise ValueError("Paint name must be at least 2 characters long")
            
            if len(paint_data.name) > cls.MAX_NAME_LENGTH:
                raise ValueError(f"Paint name must be no more than {cls.MAX_NAME_LENGTH} characters long")
        
        if paint_data.color is not None:
            if not paint_data.color.strip():
                raise ValueError("Paint color cannot be empty")
            
            if len(paint_data.color.strip()) < 2:
                raise ValueError("Paint color must be at least 2 characters long")
            
            if len(paint_data.color) > cls.MAX_COLOR_LENGTH:
                raise ValueError(f"Paint color must be no more than {cls.MAX_COLOR_LENGTH} characters long")
        
        if paint_data.description is not None and len(paint_data.description) > cls.MAX_DESCRIPTION_LENGTH:
            raise ValueError(f"Description must be no more than {cls.MAX_DESCRIPTION_LENGTH} characters long")
        
        if paint_data.features is not None:
            if len(paint_data.features) > cls.MAX_FEATURES:
                raise ValueError(f"Features list cannot have more than {cls.MAX_FEATURES} items")
            
            # Validate features are not empty strings
            for feature in paint_data.features:
                if not feature or not feature.strip():
                    raise ValueError("Feature cannot be empty")


class CSVValidator:
    """CSV import validation."""
    
    REQUIRED_COLUMNS = [
        'nome', 'cor', 'tipo_parede', 'ambiente', 'acabamento', 'features', 'linha'
    ]
    
    @classmethod
    def validate_csv_structure(cls, csv_content: str) -> None:
        """Validate CSV structure and required columns."""
        if not csv_content or not csv_content.strip():
            raise ValueError("CSV content is required")
        
        lines = csv_content.strip().split('\n')
        if len(lines) < 2:
            raise ValueError("CSV must have at least a header row and one data row")
        
        # Check header
        header = lines[0].strip().lower()
        header_columns = [col.strip() for col in header.split(',')]
        
        for required_col in cls.REQUIRED_COLUMNS:
            if required_col not in header_columns:
                raise ValueError(f"Required column '{required_col}' not found in CSV header")
    
    @classmethod
    def validate_csv_row(cls, row_data: dict, row_number: int) -> None:
        """Validate a single CSV row."""
        errors = []
        
        # Validate required fields
        required_fields = {
            'nome': 'Paint name',
            'cor': 'Color',
            'tipo_parede': 'Surface type',
            'ambiente': 'Environment',
            'acabamento': 'Finish type',
            'linha': 'Paint line'
        }
        
        for field, display_name in required_fields.items():
            if not row_data.get(field) or not str(row_data[field]).strip():
                errors.append(f"{display_name} is required")
        
        # Validate features field (can be empty but if present should be valid)
        features = row_data.get('features', '')
        if features and features.strip():
            # Features should be a comma-separated list
            feature_list = [f.strip() for f in str(features).split(',') if f.strip()]
            if len(feature_list) > 20:
                errors.append("Features list cannot have more than 20 items")
        
        if errors:
            error_msg = f"Row {row_number}: " + "; ".join(errors)
            raise ValueError(error_msg)
    
    @classmethod
    def validate_enum_values(cls, row_data: dict, row_number: int) -> None:
        """Validate enum values in CSV row."""
        from app.domain.entities import SurfaceType, Environment, FinishType, PaintLine
        
        errors = []
        
        # Validate surface types
        surface_types_str = str(row_data.get('tipo_parede', '')).strip()
        valid_surface_types = [e.value for e in SurfaceType]
        if surface_types_str:
            surface_types = [s.strip().lower() for s in surface_types_str.split(',') if s.strip()]
            for surface_type in surface_types:
                if surface_type not in valid_surface_types:
                    errors.append(f"Invalid surface type '{surface_type}'. Valid values: {', '.join(valid_surface_types)}")
        
        # Validate environment
        environment = str(row_data.get('ambiente', '')).strip().lower()
        valid_environments = [e.value for e in Environment]
        if environment not in valid_environments:
            errors.append(f"Invalid environment '{environment}'. Valid values: {', '.join(valid_environments)}")
        
        # Validate finish type
        finish_type = str(row_data.get('acabamento', '')).strip().lower()
        valid_finish_types = [e.value for e in FinishType]
        if finish_type not in valid_finish_types:
            errors.append(f"Invalid finish type '{finish_type}'. Valid values: {', '.join(valid_finish_types)}")
        
        # Validate paint line
        paint_line = str(row_data.get('linha', '')).strip().lower()
        valid_paint_lines = [e.value for e in PaintLine]
        if paint_line not in valid_paint_lines:
            errors.append(f"Invalid paint line '{paint_line}'. Valid values: {', '.join(valid_paint_lines)}")
        
        if errors:
            error_msg = f"Row {row_number}: " + "; ".join(errors)
            raise ValueError(error_msg)


class ChatValidator:
    """Chat message validation."""
    
    MIN_MESSAGE_LENGTH = 1
    MAX_MESSAGE_LENGTH = 2000
    
    @classmethod
    def validate_message(cls, message: str) -> None:
        """Validate chat message."""
        if not message:
            raise ValueError("Message is required")
        
        if not message.strip():
            raise ValueError("Message cannot be empty")
        
        if len(message) < cls.MIN_MESSAGE_LENGTH:
            raise ValueError(f"Message must be at least {cls.MIN_MESSAGE_LENGTH} character long")
        
        if len(message) > cls.MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message must be no more than {cls.MAX_MESSAGE_LENGTH} characters long")
        
        # Check for potentially harmful content
        if cls._contains_suspicious_content(message):
            raise ValueError("Message contains potentially harmful content")
    
    @classmethod
    def _contains_suspicious_content(cls, message: str) -> bool:
        """Check for suspicious content in message."""
        suspicious_patterns = [
            r'<script.*?>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocol
            r'data:text/html',  # Data URLs
            r'vbscript:',  # VBScript protocol
        ]
        
        message_lower = message.lower()
        for pattern in suspicious_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
        
        return False
