"""
Este módulo ejecuta una CLI para ayudar a migrar la base de datos de forma más eficiente y segura. Está pensado para migrar a la versión 1.0.
"""
from app.migration.database_migrator import DatabaseMigrator
from app.migration.database_connection import DatabaseConnection