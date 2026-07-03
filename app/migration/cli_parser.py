"""
Módulo para la configuración del parser de línea de comandos.
"""
from argparse import ArgumentParser, RawDescriptionHelpFormatter


def create_parser() -> ArgumentParser:
    """
    Crea y configura el parser de argumentos para la CLI de migración.
    
    Returns:
        ArgumentParser: Parser configurado con todos los comandos y opciones.
    """
    parser = ArgumentParser(
        prog="dolar-migrate",
        description="""
Migra la base de datos legacy de versiones anteriores a la versión 1.0.

COMANDOS DISPONIBLES:
  inspect   - Inspecciona la base de datos antigua y muestra un resumen
  migrate   - Ejecuta la migración completa de los datos
  validate  - Valida que la base de datos nueva tenga la estructura correcta

EJEMPLOS:
  %(prog)s inspect --old-db instance/backup.db
  %(prog)s migrate --old-db instance/backup.db --batch-size 500
  %(prog)s validate --new-db instance/dolar_vzla.db
        """,
        formatter_class=RawDescriptionHelpFormatter,
        add_help=True,
        allow_abbrev=True,
        exit_on_error=True,
    )

    # Subparsers para diferentes comandos
    subparsers = parser.add_subparsers(dest="command", title="Comandos", description="Comandos disponibles para la migración", required=True, help="Comando a ejecutar",)

    # Comando: inspect
    inspect_parser = subparsers.add_parser("inspect", help="Inspecciona la base de datos antigua", description="Muestra un resumen de los datos en la base de datos antigua.",)
    inspect_parser.add_argument("--old-db", default="instance/dolar_vzla_old.db", help="Ruta a la base de datos antigua (SQLite).",
    )

    # Comando: migrate
    migrate_parser = subparsers.add_parser("migrate", help="Ejecuta la migración de datos", description="Migra los datos de la base de datos antigua a la nueva estructura.",)
    migrate_parser.add_argument("--old-db", default="instance/exchange_rates.db", help="Ruta a la base de datos antigua (SQLite).",)
    migrate_parser.add_argument("--new-db", default="instance/dolar_vzla.db", help="Ruta a la base de datos nueva (SQLite).", )
    migrate_parser.add_argument("--batch-size", type=int, default=1000, help="Tamaño del lote para inserciones (default: 1000).",)
    migrate_parser.add_argument("--dry-run", action="store_true", help="Simula la migración sin escribir en la base de datos.",)
    migrate_parser.add_argument("--skip-bcv", action="store_true", help="Omite la migración de los datos de BCV.",)
    migrate_parser.add_argument("--skip-binance", action="store_true", help="Omite la migración de los datos de Binance.",)
    migrate_parser.add_argument("--verbose", action="store_true", help="Muestra detalles registro por registro durante la migración.",)

    # Comando: validate
    validate_parser = subparsers.add_parser("validate", help="Valida la estructura de la base de datos nueva", description="Verifica que la base de datos nueva tenga la estructura correcta.",)
    validate_parser.add_argument("--new-db", default="instance/dolar_vzla.db", help="Ruta a la base de datos nueva (SQLite).",)

    # Opciones globales
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], help="Nivel de logging (default: INFO).",)
    parser.add_argument("--log-file", help="Archivo de log opcional (si no se especifica, solo se usa consola).",)

    return parser