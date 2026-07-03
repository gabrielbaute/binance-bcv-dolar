"""
CLI principal para la migración de la base de datos.

Uso:
    python -m scripts.cli_migrator --help
"""
import sys
import asyncio
import logging

from app.config import DolarVzlaLogger, config
from app.migration.cli_parser import create_parser
from app.migration.cli_commands import cmd_inspect, cmd_migrate, cmd_validate


async def main():
    """
    Punto de entrada principal de la CLI.
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Configurar logging usando DolarVzlaLogger
    DolarVzlaLogger.setup_logging(
        logs_dir=config.LOGS_DIR,
        level=args.log_level
    )
    
    logger = logging.getLogger("cli_migrator")
    
    try:
        # Ejecutar comando
        if args.command == "inspect":
            return await cmd_inspect(args)
        elif args.command == "migrate":
            return await cmd_migrate(args)
        elif args.command == "validate":
            return await cmd_validate(args)
        else:
            logger.error(f"Comando desconocido: {args.command}")
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        logger.info("Migración interrumpida por el usuario")
        return 130
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))