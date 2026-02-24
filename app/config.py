"""
Flask Application Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', '________________________')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        '_______________________________________________________________'#modified by KLEART ADRI
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.environ.get('REDIS_URL', '_____________________________________')
    
    # File Upload
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 500 * 1024 * 1024))  # 500MB
    
    # Allowed extensions
    ALLOWED_IMAGE_EXTENSIONS = set(
        os.environ.get('ALLOWED_IMAGE_EXTENSIONS', 'jpg,jpeg,png,gif,bmp,webp').split(',')
    )
    ALLOWED_AUDIO_EXTENSIONS = set(
        os.environ.get('ALLOWED_AUDIO_EXTENSIONS', 'mp3,wav,flac,ogg,m4a').split(',')
    )
    ALLOWED_VIDEO_EXTENSIONS = set(
        os.environ.get('ALLOWED_VIDEO_EXTENSIONS', 'mp4,avi,mov,mkv,webm').split(',')
    )
    
    # Feature extraction
    EXTRACT_DEEP_FEATURES = os.environ.get('EXTRACT_DEEP_FEATURES', 'true').lower() == 'true'
    MOBILENET_BATCH_SIZE = int(os.environ.get('MOBILENET_BATCH_SIZE', 32))
    
    # Thumbnails
    THUMBNAIL_SIZE = int(os.environ.get('THUMBNAIL_SIZE', 256))
    THUMBNAIL_FOLDER = os.path.join(UPLOAD_FOLDER, 'thumbnails')
    VIDEO_THUMBNAIL_COUNT = int(os.environ.get('VIDEO_THUMBNAIL_COUNT', 5))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = '_______________________________________________________'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
