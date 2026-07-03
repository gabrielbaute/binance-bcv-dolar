"""
Módulo para gestionar conexiones a bases de datos SQLite.
"""
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from typing import Optional, AsyncGenerator, List, Dict, Any
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

class DatabaseConnection:
    """
    Gestor de conexión a una base de datos SQLite. Proporciona métodos tanto síncronos (para lectura de la base de datos legacy) como asíncronos (para escritura con SQLAlchemy en la base de dato actualizada).
    """
    
    def __init__(self, db_path: Path, echo: bool = False):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            db_path: Ruta al archivo de la base de datos SQLite.
            echo: Si es True, muestra las consultas SQL en logs.
        """
        self.db_path = Path(db_path)
        self.echo = echo
        self._engine = None
        self._session_maker = None
    
    @property
    def engine(self):
        """Retorna el engine asíncrono, creándolo si no existe."""
        if self._engine is None:
            self._engine = create_async_engine(
                f"sqlite+aiosqlite:///{self.db_path}",
                echo=self.echo,
                connect_args={"check_same_thread": False}
            )
        return self._engine
    
    @property
    def session_maker(self) -> sessionmaker:
        """Retorna el sessionmaker asíncrono, creándolo si no existe."""
        if self._session_maker is None:
            self._session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._session_maker
    
    # ============== MÉTODOS SÍNCRONOS (para lectura legacy) ==============
    def execute_sync(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL de forma síncrona y retorna los resultados como diccionarios. Útil para leer bases de datos legacy que no tienen modelos SQLAlchemy.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
            
        Returns:
            Lista de diccionarios con los resultados.
        """
        import sqlite3
        with sqlite3.connect(str(self.db_path)) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def execute_sync_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL de forma síncrona y retorna un solo resultado.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
            
        Returns:
            Diccionario con el resultado o None si no hay.
        """
        results = self.execute_sync(query, params)
        return results[0] if results else None
    
    def table_exists(self, table_name: str) -> bool:
        """
        Verifica si una tabla existe en la base de datos.
        
        Args:
            table_name: Nombre de la tabla.
            
        Returns:
            True si la tabla existe, False en caso contrario.
        """
        result = self.execute_sync_one(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?",
            (table_name,)
        )
        return result is not None
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Obtiene los nombres de las columnas de una tabla.
        
        Args:
            table_name: Nombre de la tabla.
            
        Returns:
            Lista de nombres de columnas.
        """
        results = self.execute_sync(f"PRAGMA table_info({table_name})")
        return [row["name"] for row in results]
    
    # ============== MÉTODOS ASÍNCRONOS (para escritura con SQLAlchemy) ==============
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Genera una sesión asíncrona para operaciones."""
        async with self.session_maker() as session:
            try:
                yield session
            finally:
                await session.close()
    
    async def execute_async(self, query: str, params: dict = None) -> List[Dict[str, Any]]:
        """
        Ejecuta una consulta SQL de forma asíncrona.
        
        Args:
            query: Consulta SQL a ejecutar.
            params: Parámetros para la consulta.
            
        Returns:
            Lista de diccionarios con los resultados.
        """
        async with self.session_maker() as session:
            result = await session.execute(text(query), params or {})
            rows = result.fetchall()
            if not rows:
                return []
            # Convertir a diccionarios
            keys = result.keys()
            return [dict(zip(keys, row)) for row in rows]
    
    async def dispose(self):
        """Cierra el engine y libera recursos."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._session_maker = None