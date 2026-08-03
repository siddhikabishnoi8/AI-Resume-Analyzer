import os
import secrets

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    
    # Upload folder
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # DB fallback configurations
    MYSQL_DB_URI = os.environ.get('MYSQL_DATABASE_URI', 'mysql+pymysql://root:@localhost/ai_resume_analyzer')
    SQLITE_DB_URI = 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'resume_analyzer.db')
    
    # Determine the database URI dynamically
    SQLALCHEMY_DATABASE_URI = SQLITE_DB_URI  # Default
    
    @classmethod
    def init_database_uri(cls):
        # We try to test if MySQL is accessible, else we fall back to SQLite
        try:
            import pymysql
            # Split URI to test connection
            # URI format: mysql+pymysql://user:password@host/dbname
            # We will try to parse host and user and connect
            uri = cls.MYSQL_DB_URI.replace('mysql+pymysql://', '')
            user_pass, host_db = uri.split('@')
            user = user_pass.split(':')[0]
            password = user_pass.split(':')[1] if ':' in user_pass else ''
            
            host_port_db = host_db.split('/')
            host_port = host_port_db[0]
            db = host_port_db[1]
            
            host = host_port.split(':')[0]
            port = int(host_port.split(':')[1]) if ':' in host_port else 3306
            
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                connect_timeout=2
            )
            
            # Check if db exists, if not create it
            with conn.cursor() as cursor:
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
            conn.close()
            
            cls.SQLALCHEMY_DATABASE_URI = cls.MYSQL_DB_URI
            print(f"[Database] Successfully connected to MySQL database: {db}")
        except Exception as e:
            print(f"[Database] MySQL connection failed: {e}. Falling back to SQLite: {cls.SQLITE_DB_URI}")
            cls.SQLALCHEMY_DATABASE_URI = cls.SQLITE_DB_URI

# Execute dynamic DB selection
Config.init_database_uri()
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
