"""
Módulo que contiene la lógica de migración de la base de datos.
"""
import logging
from uuid import uuid4
from pathlib import Path
from datetime import datetime
from pydantic import ValidationError
from typing import Dict, List, Any, Tuple

from app.errors import MigrationError
from app.migration.database_connection import DatabaseConnection
from app.enums import Currency, TradeType, FiatCurrency, BinanceAsset
from app.database.models import BCVRateSQLModel, BinanceRateSQLModel

class DatabaseMigrator:
    """
    Clase responsable de la migración de datos entre versiones de la base de datos.
    """
    def __init__(self, verbose: bool = False):
        """Inicializa el migrador."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.verbose = verbose
        self._errors: List[MigrationError] = []
    
    # ============== PROPIEDADES Y MÉTODOS AUXILIARES ==============
    @property
    def has_errors(self) -> bool:
        """Indica si hubo errores durante la migración."""
        return len(self._errors) > 0

    @property
    def error_count(self) -> int:
        """Número de errores encontrados."""
        return len(self._errors)

    def _log_verbose(self, message: str, level: str = "info"):
        """Loggea un mensaje solo si verbose está activado."""
        if self.verbose:
            getattr(self.logger, level)(message)

    # ============== MÉTODOS DE PARSING ==============
    def parse_currency(self, value: str) -> Currency:
        """Convierte un string a Currency enum."""
        mapping = {
            "dolar": Currency.DOLAR,
            "euro": Currency.EURO,
            "yuan": Currency.YUAN,
            "lira": Currency.LIRA,
            "rublo": Currency.RUBLE,
            "USD": Currency.DOLAR,
            "EUR": Currency.EURO,
            "CNY": Currency.YUAN,
            "TRY": Currency.LIRA,
            "RUB": Currency.RUBLE,
        }
        normalized = str(value).lower()
        if normalized in mapping:
            return mapping[normalized]
        try:
            return Currency(value)
        except ValueError:
            self.logger.warning(f"Moneda no reconocida: {value}, usando DOLAR como fallback")
            return Currency.DOLAR

    def parse_fiat_currency(self, value: str) -> FiatCurrency:
        """Convierte un string a FiatCurrency enum."""
        try:
            return FiatCurrency(value.upper())
        except ValueError:
            self.logger.warning(f"Fiat no reconocido: {value}, usando VES como fallback")
            return FiatCurrency.VES

    def parse_binance_asset(self, value: str) -> BinanceAsset:
        """Convierte un string a BinanceAsset enum."""
        try:
            return BinanceAsset(value.upper())
        except ValueError:
            self.logger.warning(f"Asset no reconocido: {value}, usando USDT como fallback")
            return BinanceAsset.USDT

    def parse_trade_type(self, value: str) -> TradeType:
        """Convierte un string a TradeType enum."""
        try:
            return TradeType(value.upper())
        except ValueError:
            self.logger.warning(f"Trade type no reconocido: {value}, usando BUY como fallback")
            return TradeType.BUY

    # ============== MÉTODOS DE LECTURA ==============
    def read_old_database(self, old_db: DatabaseConnection) -> Dict[str, List[Dict[str, Any]]]:
        """
        Lee todos los datos de la base de datos antigua.
        
        Args:
            old_db: Conexión a la base de datos antigua.
            
        Returns:
            Dict con los datos de BCV y Binance.
        """
        self.logger.info(f"Leyendo base de datos antigua: {old_db.db_path}")
        
        bcv_records = old_db.execute_sync("""
            SELECT id, currency, rate, date
            FROM bcv_rates
            ORDER BY date ASC
        """)
        
        binance_records = old_db.execute_sync("""
            SELECT id, fiat, asset, trade_type, average_price, date
            FROM binance_rates
            ORDER BY date ASC
        """)
        
        # Parsear fechas
        for record in bcv_records:
            if isinstance(record["date"], str):
                try:
                    record["date"] = datetime.fromisoformat(record["date"])
                except ValueError:
                    record["date"] = datetime.strptime(record["date"], "%Y-%m-%d %H:%M:%S")
        
        for record in binance_records:
            if isinstance(record["date"], str):
                try:
                    record["date"] = datetime.fromisoformat(record["date"])
                except ValueError:
                    record["date"] = datetime.strptime(record["date"], "%Y-%m-%d %H:%M:%S")
        
        return {
            "bcv": bcv_records,
            "binance": binance_records,
        }

    # ============== MÉTODOS DE TRANSFORMACIÓN ==============
    def transform_bcv_record(self, old_record: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma un registro antiguo de BCV al nuevo formato."""
        return {
            "id": uuid4(),
            "currency": self.parse_currency(old_record["currency"]),
            "trade_type": TradeType.SELL,
            "rate": float(old_record["rate"]),
            "date": old_record["date"],
        }

    def transform_binance_record(self, old_record: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma un registro antiguo de Binance al nuevo formato."""
        return {
            "id": uuid4(),
            "fiat": self.parse_fiat_currency(old_record["fiat"]),
            "asset": self.parse_binance_asset(old_record["asset"]),
            "trade_type": self.parse_trade_type(old_record["trade_type"]),
            "average_price": float(old_record["average_price"]),
            "median_price": None,
            "date": old_record["date"],
        }

    # ============== MÉTODOS DE VALIDACIÓN ==============    
    def validate_bcv_record(self, record: Dict[str, Any], index: int) -> bool:
        """Valida un registro transformado de BCV contra el modelo SQLAlchemy."""
        try:
            BCVRateSQLModel(**record)
            return True
        except ValidationError as e:
            self._errors.append(MigrationError(
                record_index=index,
                original_record=record,
                error=str(e)
            ))
            return False

    def validate_binance_record(self, record: Dict[str, Any], index: int) -> bool:
        """Valida un registro transformado de Binance contra el modelo SQLAlchemy."""
        try:
            BinanceRateSQLModel(**record)
            return True
        except ValidationError as e:
            self._errors.append(MigrationError(
                record_index=index,
                original_record=record,
                error=str(e)
            ))
            return False

    async def validate_new_database(self, new_db: DatabaseConnection) -> bool:
        """
        Valida que la nueva base de datos tenga la estructura correcta.
        
        Args:
            new_db: Conexión a la base de datos nueva.
            
        Returns:
            bool: True si la estructura es correcta.
        """
        self.logger.info(f"Validando estructura de la base de datos: {new_db.db_path}")
        
        try:
            # Verificar tablas
            if not new_db.table_exists("rates"):
                self.logger.error("Tabla 'rates' no encontrada")
                return False
            
            if not new_db.table_exists("binance_rates"):
                self.logger.error("Tabla 'binance_rates' no encontrada")
                return False
            
            # Verificar columnas de rates
            bcv_columns = new_db.get_table_columns("rates")
            required_bcv = ['id', 'currency', 'trade_type', 'rate', 'date']
            missing_bcv = [col for col in required_bcv if col not in bcv_columns]
            if missing_bcv:
                self.logger.error(f"Columnas faltantes en 'rates': {missing_bcv}")
                return False
            
            # Verificar columnas de binance_rates
            binance_columns = new_db.get_table_columns("binance_rates")
            required_binance = ['id', 'fiat', 'asset', 'trade_type', 'average_price', 'median_price', 'date']
            missing_binance = [col for col in required_binance if col not in binance_columns]
            if missing_binance:
                self.logger.error(f"Columnas faltantes en 'binance_rates': {missing_binance}")
                return False
            
            self.logger.info("✓ Estructura de la base de datos validada correctamente")
            return True
                
        except Exception as e:
            self.logger.error(f"Error validando la base de datos: {e}")
            return False

    # ============== MÉTODOS DE MIGRACIÓN ==============
    async def migrate_bcv_rates(
        self,
        old_records: List[Dict[str, Any]],
        new_db: DatabaseConnection,
        batch_size: int = 1000,
        dry_run: bool = False,
    ) -> Tuple[int, int, int]:
        """
        Migra los registros de BCV a la nueva base de datos.
        
        Returns:
            Tuple[int, int, int]: (total, insertados, errores)
        """
        total_records = len(old_records)
        self.logger.info(f"Iniciando migración de BCV: {total_records} registros")
        
        if total_records == 0:
            self.logger.info("No hay registros de BCV para migrar.")
            return 0, 0, 0
        
        transformed = []
        self._log_verbose("\n📋 Transformando registros de BCV:")
        
        for idx, record in enumerate(old_records):
            try:
                transformed_record = self.transform_bcv_record(record)
                if self.validate_bcv_record(transformed_record, idx):
                    transformed.append(transformed_record)
                    self._log_verbose(f"  ✅ Registro {idx + 1}: OK")
                else:
                    self._log_verbose(f"  ❌ Registro {idx + 1}: ERROR de validación")
            except Exception as e:
                self._errors.append(MigrationError(
                    record_index=idx,
                    original_record=record,
                    error=f"Error en transformación: {str(e)}"
                ))
                self._log_verbose(f"  ❌ Registro {idx + 1}: ERROR en transformación: {e}")
        
        if self.has_errors and not dry_run:
            self.logger.warning(f"Se encontraron {self.error_count} errores en los datos")
            self.logger.warning("Los registros con error serán omitidos. Continuando con los válidos...")
        
        if dry_run:
            self.logger.info(f"DRY RUN: {len(transformed)}/{total_records} registros serían migrados")
            if self.has_errors:
                self.logger.warning(f"  ⚠️  {self.error_count} registros con errores")
            return total_records, len(transformed), self.error_count
        
        inserted = 0
        for i in range(0, len(transformed), batch_size):
            batch = transformed[i:i + batch_size]
            
            async with new_db.session_maker() as session:
                async with session.begin():
                    for record in batch:
                        new_record = BCVRateSQLModel(**record)
                        session.add(new_record)
                    await session.commit()
            
            inserted += len(batch)
            self.logger.info(f"Progreso BCV: {inserted}/{len(transformed)} registros insertados")
        
        self.logger.info(f"Migración de BCV completada: {inserted} registros insertados")
        return total_records, inserted, self.error_count

    async def migrate_binance_rates(
        self,
        old_records: List[Dict[str, Any]],
        new_db: DatabaseConnection,
        batch_size: int = 1000,
        dry_run: bool = False,
    ) -> Tuple[int, int, int]:
        """
        Migra los registros de Binance a la nueva base de datos.
        
        Returns:
            Tuple[int, int, int]: (total, insertados, errores)
        """
        total_records = len(old_records)
        self.logger.info(f"Iniciando migración de Binance: {total_records} registros")
        
        if total_records == 0:
            self.logger.info("No hay registros de Binance para migrar.")
            return 0, 0, 0
        
        transformed = []
        self._log_verbose("\n📋 Transformando registros de Binance:")
        
        for idx, record in enumerate(old_records):
            try:
                transformed_record = self.transform_binance_record(record)
                if self.validate_binance_record(transformed_record, idx):
                    transformed.append(transformed_record)
                    self._log_verbose(f"  ✅ Registro {idx + 1}: OK")
                else:
                    self._log_verbose(f"  ❌ Registro {idx + 1}: ERROR de validación")
            except Exception as e:
                self._errors.append(MigrationError(
                    record_index=idx,
                    original_record=record,
                    error=f"Error en transformación: {str(e)}"
                ))
                self._log_verbose(f"  ❌ Registro {idx + 1}: ERROR en transformación: {e}")
        
        if self.has_errors and not dry_run:
            self.logger.warning(f"Se encontraron {self.error_count} errores en los datos")
            self.logger.warning("Los registros con error serán omitidos. Continuando con los válidos...")
        
        if dry_run:
            self.logger.info(f"DRY RUN: {len(transformed)}/{total_records} registros serían migrados")
            if self.has_errors:
                self.logger.warning(f"  ⚠️  {self.error_count} registros con errores")
            return total_records, len(transformed), self.error_count
        
        inserted = 0
        for i in range(0, len(transformed), batch_size):
            batch = transformed[i:i + batch_size]
            
            async with new_db.session_maker() as session:
                async with session.begin():
                    for record in batch:
                        new_record = BinanceRateSQLModel(**record)
                        session.add(new_record)
                    await session.commit()
            
            inserted += len(batch)
            self.logger.info(f"Progreso Binance: {inserted}/{len(transformed)} registros insertados")
        
        self.logger.info(f"Migración de Binance completada: {inserted} registros insertados")
        return total_records, inserted, self.error_count

    # ============== MÉTODO PRINCIPAL ==============
    async def run_migration(
        self,
        old_db_path: Path,
        new_db_path: Path,
        batch_size: int = 1000,
        dry_run: bool = False,
        skip_bcv: bool = False,
        skip_binance: bool = False,
        verbose: bool = False,
    ) -> Dict[str, Any]:
        """
        Ejecuta el proceso completo de migración.
        """
        self.verbose = verbose
        self._errors = []
        
        results = {
            "bcv": {"total": 0, "inserted": 0, "errors": 0},
            "binance": {"total": 0, "inserted": 0, "errors": 0},
            "total_errors": 0,
        }
        
        # Validar existencia de archivos
        if not old_db_path.exists():
            raise FileNotFoundError(f"Base de datos antigua no encontrada: {old_db_path}")
        
        if not new_db_path.exists():
            raise FileNotFoundError(f"Base de datos nueva no encontrada: {new_db_path}")
        
        # Crear conexiones
        old_db = DatabaseConnection(old_db_path)
        new_db = DatabaseConnection(new_db_path)
        
        try:
            # Validar estructura de la nueva base de datos
            if not await self.validate_new_database(new_db):
                raise ValueError("La estructura de la base de datos nueva no es válida")
            
            # Leer datos antiguos
            old_data = self.read_old_database(old_db)
            
            # Migrar BCV
            if not skip_bcv:
                total, inserted, errors = await self.migrate_bcv_rates(
                    old_data["bcv"],
                    new_db=new_db,
                    batch_size=batch_size,
                    dry_run=dry_run,
                )
                results["bcv"] = {"total": total, "inserted": inserted, "errors": errors}
            
            # Migrar Binance
            if not skip_binance:
                total, inserted, errors = await self.migrate_binance_rates(
                    old_data["binance"],
                    new_db=new_db,
                    batch_size=batch_size,
                    dry_run=dry_run,
                )
                results["binance"] = {"total": total, "inserted": inserted, "errors": errors}
            
            results["total_errors"] = self.error_count
            
            # Mostrar detalles de errores si hay y verbose está activado
            if self.has_errors and verbose:
                print("\n" + "=" * 60)
                print("❌ DETALLE DE ERRORES")
                print("=" * 60)
                for err in self._errors:
                    print(f"\nRegistro #{err.record_index + 1}:")
                    print(f"  Error: {err.error}")
                    print(f"  Datos: {err.original_record}")
                print("=" * 60)
            
            return results
            
        finally:
            await old_db.dispose()
            await new_db.dispose()