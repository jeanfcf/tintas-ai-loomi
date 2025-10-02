"""Application services."""
from typing import List, Optional
from sqlalchemy.orm import Session

from app.domain.entities import (
    User, UserCreate, UserUpdate, LoginRequest, Token, TokenData, UserRole, UserFilters, PaginationParams, PaginatedResponse,
    Paint, PaintCreate, PaintUpdate, PaintFilters, PaginatedPaintResponse,
    CSVImportRequest, CSVImportResponse, CSVImportResult, CSVRowError, PaintResponse
)
from app.domain.services import UserServiceInterface, AuthServiceInterface, AuthApplicationServiceInterface, PaintServiceInterface, CSVImportServiceInterface, AIOrchestratorServiceInterface
from app.domain.repositories import UserRepositoryInterface, PaintRepositoryInterface
from app.core.logging import get_logger
from app.core.settings import settings
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import base64
import csv
import io

logger = get_logger(__name__)


class AuthService(AuthServiceInterface):
    """Authentication service implementation."""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["pbkdf2_sha256"],
            deprecated="auto",
            pbkdf2_sha256__default_rounds=290000
        )
        self.secret_key = settings.security.secret_key
        self.algorithm = settings.security.algorithm
        self.access_token_expire_minutes = settings.security.access_token_expire_minutes

    def authenticate_user(self, db: Session, login_data: LoginRequest, user_repo: UserRepositoryInterface) -> Optional[User]:
        """Authenticate user with username and password."""
        result = user_repo.get_user_with_password(db, login_data.username)
        
        if not result:
            return None
            
        user, hashed_password = result
        if not self.verify_password(login_data.password, hashed_password):
            return None
            
        return user

    def create_access_token(self, user: User) -> str:
        """Create access token for user."""
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "exp": expire
        }
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            role: str = payload.get("role")
            
            if user_id is None or username is None or role is None:
                return None
                
            return TokenData(
                user_id=int(user_id),
                username=username,
                role=UserRole(role)
            )
        except JWTError:
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def hash_password(self, password: str) -> str:
        """Hash password using PBKDF2-SHA256."""
        try:
            return self.pwd_context.hash(password)
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError(f"Password hashing failed: {e}")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return self.pwd_context.verify(plain_password, hashed_password)


class UserService(UserServiceInterface):
    """User service implementation."""

    def __init__(self, user_repo: UserRepositoryInterface, auth_service: AuthServiceInterface):
        self.user_repo = user_repo
        self.auth_service = auth_service

    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        try:
            from app.domain.validators import UserValidator
            UserValidator.validate_create_data(user_data)

            if self.user_repo.exists_active_by_email(db, user_data.email):
                raise ValueError("User with this email already exists")

            if self.user_repo.exists_active_by_username(db, user_data.username):
                raise ValueError("User with this username already exists")

            hashed_password = self.auth_service.hash_password(user_data.password)
            user = self.user_repo.create(db, user_data, hashed_password)
            
            return user
            
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error creating user: {e}"
            logger.error(f"{error_msg} - username: {user_data.username}, email: {user_data.email}")
            raise Exception(error_msg)

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.user_repo.get_by_id(db, user_id)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return self.user_repo.get_by_email(db, email)

    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return self.user_repo.get_by_username(db, username)

    def get_users(self, db: Session, pagination: PaginationParams, filters: UserFilters) -> PaginatedResponse:
        """Get all users with pagination and filters."""
        users = self.user_repo.get_all(db, pagination, filters)
        total = self.user_repo.count_all(db, filters)
        
        return PaginatedResponse(
            items=users,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit,
            has_next=pagination.skip + pagination.limit < total,
            has_prev=pagination.skip > 0
        )

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user."""
        try:
            from app.domain.validators import UserValidator
            UserValidator.validate_update_data(user_data)
            
            if user_data.password and user_data.password.strip():
                hashed_password = self.auth_service.hash_password(user_data.password)
                
                from app.domain.entities import UserUpdate
                update_data = UserUpdate(
                    email=user_data.email,
                    username=user_data.username,
                    full_name=user_data.full_name,
                    role=user_data.role,
                    status=user_data.status,
                    password=hashed_password
                )
                return self.user_repo.update(db, user_id, update_data)
            else:
                return self.user_repo.update(db, user_id, user_data)
                
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error updating user: {e}"
            logger.error(f"{error_msg} - user_id: {user_id}")
            raise Exception(error_msg)

    def delete_user(self, db: Session, user_id: int) -> bool:
        """Soft delete user."""
        return self.user_repo.delete(db, user_id)


    def update_last_login(self, db: Session, user_id: int) -> None:
        """Update user's last login timestamp."""
        self.user_repo.update_last_login(db, user_id)


class AuthApplicationService(AuthApplicationServiceInterface):
    """Authentication application service."""

    def __init__(self, auth_service: AuthServiceInterface, user_service: UserServiceInterface):
        self.auth_service = auth_service
        self.user_service = user_service

    def login(self, db: Session, login_data: LoginRequest) -> Token:
        """Authenticate user and return token."""
        try:
            user = self.auth_service.authenticate_user(db, login_data, self.user_service.user_repo)
            if not user:
                raise ValueError("Invalid username or password")

            self.user_service.update_last_login(db, user.id)
            access_token = self.auth_service.create_access_token(user)
            
            logger.info(f"User login - username: {user.username}")
            
            return Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=self.auth_service.access_token_expire_minutes * 60
            )
            
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error during login: {e}"
            logger.error(f"{error_msg} - username: {login_data.username}")
            raise Exception(error_msg)

    def verify_token(self, token: str):
        """Verify token and return token data."""
        return self.auth_service.verify_token(token)


class PaintService(PaintServiceInterface):
    """Paint service implementation."""

    def __init__(self, paint_repo: PaintRepositoryInterface):
        self.paint_repo = paint_repo

    def create_paint(self, db: Session, paint_data: PaintCreate) -> Paint:
        """Create a new paint."""
        try:
            from app.domain.validators import PaintValidator
            PaintValidator.validate_paint_data(paint_data)

            if self.paint_repo.exists_active_by_name(db, paint_data.name):
                raise ValueError("Paint with this name already exists")

            paint = self.paint_repo.create(db, paint_data)
            
            return paint
            
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error creating paint: {e}"
            logger.error(f"{error_msg} - name: {paint_data.name}, color: {paint_data.color}")
            raise Exception(error_msg)

    def get_paint(self, db: Session, paint_id: int) -> Optional[Paint]:
        """Get paint by ID."""
        return self.paint_repo.get_by_id(db, paint_id)

    def get_paint_by_name(self, db: Session, name: str) -> Optional[Paint]:
        """Get paint by name."""
        return self.paint_repo.get_by_name(db, name)

    def get_paints(self, db: Session, pagination: PaginationParams, filters: PaintFilters) -> PaginatedPaintResponse:
        """Get all paints with pagination and filters."""
        paints = self.paint_repo.get_all(db, pagination, filters)
        total = self.paint_repo.count_all(db, filters)
        
        return PaginatedPaintResponse(
            items=paints,
            total=total,
            skip=pagination.skip,
            limit=pagination.limit,
            has_next=pagination.skip + pagination.limit < total,
            has_prev=pagination.skip > 0
        )

    def update_paint(self, db: Session, paint_id: int, paint_data: PaintUpdate) -> Optional[Paint]:
        """Update paint."""
        try:
            from app.domain.validators import PaintValidator
            PaintValidator.validate_paint_update(paint_data)
            
            # Check if name is being updated and if it already exists
            if paint_data.name and paint_data.name != self.paint_repo.get_by_id(db, paint_id).name:
                if self.paint_repo.exists_active_by_name(db, paint_data.name):
                    raise ValueError("Paint with this name already exists")
            
            return self.paint_repo.update(db, paint_id, paint_data)
                
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error updating paint: {e}"
            logger.error(f"{error_msg} - paint_id: {paint_id}")
            raise Exception(error_msg)

    def delete_paint(self, db: Session, paint_id: int) -> bool:
        """Soft delete paint."""
        return self.paint_repo.delete(db, paint_id)

    def get_paints_by_filters(self, db: Session, filters: PaintFilters) -> List[Paint]:
        """Get paints by specific filters without pagination."""
        return self.paint_repo.get_by_filters(db, filters)


class CSVImportService(CSVImportServiceInterface):
    """CSV import service implementation."""

    def __init__(self, paint_service: PaintServiceInterface):
        self.paint_service = paint_service

    async def import_paints_from_csv(self, db: Session, import_request: CSVImportRequest) -> CSVImportResponse:
        """Import paints from CSV file."""
        try:
            # Decode base64 content
            csv_content = self._decode_csv_content(import_request.file_content)
            
            # Validate CSV structure
            self.validate_csv_file(csv_content)
            
            # Parse CSV content
            csv_rows = self.parse_csv_content(csv_content)
            
            # Process each row
            result = await self._process_csv_rows(db, csv_rows, import_request)
            
            return CSVImportResponse(
                success=True,
                message=f"Successfully imported {result.successful_imports} out of {result.total_rows} paints",
                result=result
            )
            
        except ValueError as e:
            logger.error(f"CSV validation error: {e}")
            return CSVImportResponse(
                success=False,
                message=f"CSV validation failed: {str(e)}",
                errors=[]
            )
        except Exception as e:
            logger.error(f"Unexpected error during CSV import: {e}")
            return CSVImportResponse(
                success=False,
                message=f"Unexpected error during import: {str(e)}",
                errors=[]
            )

    def validate_csv_file(self, csv_content: str) -> bool:
        """Validate CSV file structure and format."""
        from app.domain.validators import CSVValidator
        CSVValidator.validate_csv_structure(csv_content)
        return True

    def parse_csv_content(self, csv_content: str) -> List[dict]:
        """Parse CSV content into list of dictionaries."""
        try:
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            return list(csv_reader)
        except Exception as e:
            raise ValueError(f"Error parsing CSV content: {str(e)}")

    def _decode_csv_content(self, base64_content: str) -> str:
        """Decode base64 encoded CSV content."""
        try:
            decoded_bytes = base64.b64decode(base64_content)
            return decoded_bytes.decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error decoding CSV content: {str(e)}")

    async def _process_csv_rows(self, db: Session, csv_rows: List[dict], import_request: CSVImportRequest) -> CSVImportResult:
        """Process CSV rows and import paints."""
        from app.domain.validators import CSVValidator
        from app.domain.entities import SurfaceType, Environment, FinishType, PaintLine, PaintCreate
        
        result = CSVImportResult(
            total_rows=len(csv_rows),
            successful_imports=0,
            failed_imports=0,
            errors=[],
            imported_paints=[]
        )
        
        for i, row in enumerate(csv_rows, start=2):  # Start at 2 because header is row 1
            try:
                # Validate row data
                CSVValidator.validate_csv_row(row, i)
                CSVValidator.validate_enum_values(row, i)
                
                # Parse features
                features = []
                if row.get('features') and row['features'].strip():
                    features = [f.strip() for f in row['features'].split(',') if f.strip()]
                
                # Parse surface types
                surface_types = []
                if row.get('tipo_parede') and row['tipo_parede'].strip():
                    surface_types = [SurfaceType(s.strip().lower()) for s in row['tipo_parede'].split(',') if s.strip()]
                
                # Create paint data
                paint_data = PaintCreate(
                    name=row['nome'].strip(),
                    color=row['cor'].strip(),
                    surface_types=surface_types,
                    environment=Environment(row['ambiente'].strip().lower()),
                    finish_type=FinishType(row['acabamento'].strip().lower()),
                    features=features,
                    line=PaintLine(row['linha'].strip().lower())
                )
                
                # Check if paint already exists
                existing_paint = self.paint_service.get_paint_by_name(db, paint_data.name)
                
                if existing_paint:
                    if import_request.skip_duplicates:
                        result.errors.append(f"Row {i}: Paint '{paint_data.name}' already exists, skipping")
                        result.failed_imports += 1
                        continue
                    elif import_request.update_existing:
                        # Update existing paint
                        from app.domain.entities import PaintUpdate
                        update_data = PaintUpdate(
                            color=paint_data.color,
                            surface_types=paint_data.surface_types,
                            environment=paint_data.environment,
                            finish_type=paint_data.finish_type,
                            features=paint_data.features,
                            line=paint_data.line
                        )
                        updated_paint = self.paint_service.update_paint(db, existing_paint.id, update_data)
                        if updated_paint:
                            # Regenerate and store embedding for the updated paint
                            try:
                                from app.core.container import container
                                embedding_service = container.get_embedding_service()
                                import asyncio
                                asyncio.run(embedding_service.generate_and_store_embedding(db, updated_paint.id))
                                logger.info(f"Regenerated embedding for updated paint: {updated_paint.name}")
                            except Exception as e:
                                logger.warning(f"Failed to regenerate embedding for paint {updated_paint.name}: {e}")
                                # Continue with import even if embedding generation fails
                            
                            result.imported_paints.append(PaintResponse.model_validate(updated_paint))
                            result.successful_imports += 1
                        else:
                            result.errors.append(f"Row {i}: Failed to update paint '{paint_data.name}'")
                            result.failed_imports += 1
                        continue
                    else:
                        result.errors.append(f"Row {i}: Paint '{paint_data.name}' already exists")
                        result.failed_imports += 1
                        continue
                
                # Create new paint
                created_paint = self.paint_service.create_paint(db, paint_data)
                
                # Generate and store embedding for the new paint
                try:
                    from app.core.container import container
                    embedding_service = container.get_embedding_service()
                    await embedding_service.generate_and_store_embedding(db, created_paint.id)
                    logger.info(f"Generated embedding for imported paint: {created_paint.name}")
                except Exception as e:
                    logger.warning(f"Failed to generate embedding for paint {created_paint.name}: {e}")
                    # Continue with import even if embedding generation fails
                
                result.imported_paints.append(PaintResponse.model_validate(created_paint))
                result.successful_imports += 1
                
            except ValueError as e:
                result.errors.append(f"Row {i}: {str(e)}")
                result.failed_imports += 1
            except Exception as e:
                result.errors.append(f"Row {i}: Unexpected error - {str(e)}")
                result.failed_imports += 1
                logger.error(f"Error processing CSV row {i}: {e}")
        
        return result
