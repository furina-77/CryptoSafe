"""
PostgreSQL 数据库模型
使用 SQLAlchemy ORM
"""
from sqlalchemy import create_engine, Column, String, DateTime, Integer, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class KeyType(str, enum.Enum):
    """密钥类型"""
    SYMMETRIC = 'symmetric'
    ASYMMETRIC_PUBLIC = 'asymmetric_public'
    ASYMMETRIC_PRIVATE = 'asymmetric_private'
    HMAC = 'hmac'


class KeyStatus(str, enum.Enum):
    """密钥状态"""
    ACTIVE = 'active'
    DISABLED = 'disabled'
    DELETED = 'deleted'
    EXPIRED = 'expired'


class Key(Base):
    """密钥表"""
    __tablename__ = 'keys'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_type = Column(SQLEnum(KeyType), nullable=False)
    algorithm = Column(String(50), nullable=False)
    status = Column(SQLEnum(KeyStatus), default=KeyStatus.ACTIVE)
    description = Column(String(500))
    tags = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    rotation_days = Column(Integer, default=90)

    # 关系
    audit_logs = relationship('AuditLog', back_populates='key', cascade='all, delete-orphan')


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = 'audit_logs'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_id = Column(String(36), ForeignKey('keys.id', ondelete='CASCADE'))
    operation = Column(String(20), nullable=False)
    operator = Column(String(100), default='system')
    details = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow)

    # 关系
    key = relationship('Key', back_populates='audit_logs')


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True, pool_recycle=3600)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """删除所有表"""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self):
        """获取数据库会话"""
        return self.SessionLocal()

    def init_db(self):
        """初始化数据库"""
        self.create_tables()
