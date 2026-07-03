"""
Módulo que contiene las funciones de ejecución para cada comando de la CLI.
"""
import logging
from pathlib import Path

from app.migration.database_connection import DatabaseConnection
from app.migration.database_migrator import DatabaseMigrator


async def cmd_inspect(args) -> int:
    """
    Comando: Inspecciona la base de datos antigua y muestra un resumen.
    
    Args:
        args: Argumentos parseados de la CLI.
        
    Returns:
        int: Código de salida (0 = éxito, 1 = error).
    """
    logger = logging.getLogger("cli_commands")
    old_db_path = Path(args.old_db)
    
    if not old_db_path.exists():
        logger.error(f"Base de datos antigua no encontrada: {old_db_path}")
        return 1
    
    old_db = DatabaseConnection(old_db_path)
    
    try:
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE LA BASE DE DATOS ANTIGUA")
        print("=" * 60)
        print(f"📁 Archivo: {old_db_path}")
        print(f"📦 Tamaño: {old_db_path.stat().st_size / 1024:.2f} KB")
        
        # Verificar tablas
        has_bcv = old_db.table_exists("bcv_rates")
        has_binance = old_db.table_exists("binance_rates")
        
        print("\n📈 TABLAS ENCONTRADAS:")
        print(f"   {'✅' if has_bcv else '❌'} bcv_rates")
        print(f"   {'✅' if has_binance else '❌'} binance_rates")
        
        if has_bcv:
            result = old_db.execute_sync_one("SELECT COUNT(*) as count FROM bcv_rates")
            bcv_count = result["count"] if result else 0
            
            result = old_db.execute_sync_one("SELECT MIN(date) as min_date, MAX(date) as max_date FROM bcv_rates")
            if result:
                print(f"\n📈 REGISTROS DE BCV:")
                print(f"   • Total: {bcv_count}")
                if result["min_date"] and result["max_date"]:
                    print(f"   • Desde: {result['min_date']}")
                    print(f"   • Hasta: {result['max_date']}")
        
        if has_binance:
            result = old_db.execute_sync_one("SELECT COUNT(*) as count FROM binance_rates")
            binance_count = result["count"] if result else 0
            
            result = old_db.execute_sync_one("SELECT MIN(date) as min_date, MAX(date) as max_date FROM binance_rates")
            if result:
                print(f"\n📈 REGISTROS DE BINANCE:")
                print(f"   • Total: {binance_count}")
                if result["min_date"] and result["max_date"]:
                    print(f"   • Desde: {result['min_date']}")
                    print(f"   • Hasta: {result['max_date']}")
        
        print("=" * 60)
        return 0
        
    except Exception as e:
        logger.error(f"Error inspeccionando la base de datos: {e}")
        return 1
    finally:
        await old_db.dispose()

async def cmd_migrate(args) -> int:
    """
    Comando: Ejecuta la migración de datos.
    """
    logger = logging.getLogger("cli_commands")
    old_db_path = Path(args.old_db)
    new_db_path = Path(args.new_db)
    
    print("\n" + "=" * 60)
    print("🚀 INICIANDO MIGRACIÓN DE BASE DE DATOS")
    print("=" * 60)
    print(f"📁 Base de datos antigua: {old_db_path}")
    print(f"📁 Base de datos nueva: {new_db_path}")
    print(f"📦 Tamaño de lote: {args.batch_size}")
    print(f"🧪 Dry run: {'✅' if args.dry_run else '❌'}")
    print(f"📝 Verbose: {'✅' if args.verbose else '❌'}")
    print(f"⏭️  Saltar BCV: {'✅' if args.skip_bcv else '❌'}")
    print(f"⏭️  Saltar Binance: {'✅' if args.skip_binance else '❌'}")
    print("=" * 60 + "\n")
    
    try:
        migrator = DatabaseMigrator(verbose=args.verbose)
        
        results = await migrator.run_migration(
            old_db_path=old_db_path,
            new_db_path=new_db_path,
            batch_size=args.batch_size,
            dry_run=args.dry_run,
            skip_bcv=args.skip_bcv,
            skip_binance=args.skip_binance,
            verbose=args.verbose,
        )
        
        print("\n" + "=" * 60)
        print("✅ MIGRACIÓN COMPLETADA" if not args.dry_run else "🧪 DRY RUN COMPLETADO")
        print("=" * 60)
        
        bcv = results["bcv"]
        binance = results["binance"]
        
        print(f"📊 BCV:")
        print(f"   • Total: {bcv['total']}")
        print(f"   • Migrados: {bcv['inserted']}")
        if bcv['errors'] > 0:
            print(f"   • ⚠️  Errores: {bcv['errors']}")
        
        print(f"\n📊 Binance:")
        print(f"   • Total: {binance['total']}")
        print(f"   • Migrados: {binance['inserted']}")
        if binance['errors'] > 0:
            print(f"   • ⚠️  Errores: {binance['errors']}")
        
        if results["total_errors"] > 0:
            print(f"\n⚠️  Total de errores: {results['total_errors']}")
            if args.verbose:
                print("   (Detalles mostrados arriba)")
            else:
                print("   Usa --verbose para ver los detalles de cada error")
        
        if args.dry_run:
            print("\n⚠️  Ejecución en modo DRY RUN - No se escribieron datos")
        
        print("=" * 60)
        return 0 if not migrator.has_errors else 1
        
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        return 1
    except ValueError as e:
        logger.error(f"❌ {e}")
        return 1
    except Exception as e:
        logger.error(f"❌ Error durante la migración: {e}", exc_info=True)
        return 1

async def cmd_validate(args) -> int:
    """
    Comando: Valida la estructura de la base de datos nueva.
    
    Args:
        args: Argumentos parseados de la CLI.
        
    Returns:
        int: Código de salida (0 = éxito, 1 = error).
    """
    logger = logging.getLogger("cli_commands")
    new_db_path = Path(args.new_db)
    
    if not new_db_path.exists():
        logger.error(f"Base de datos nueva no encontrada: {new_db_path}")
        return 1
    
    new_db = DatabaseConnection(new_db_path)
    
    try:
        migrator = DatabaseMigrator()
        is_valid = await migrator.validate_new_database(new_db)
        
        if is_valid:
            print("\n" + "=" * 60)
            print("✅ ESTRUCTURA DE BASE DE DATOS VÁLIDA")
            print("=" * 60)
            print(f"📁 {new_db_path}")
            print("✓ Todas las tablas y columnas requeridas existen")
            print("=" * 60)
            return 0
        else:
            print("\n" + "=" * 60)
            print("❌ ESTRUCTURA DE BASE DE DATOS INVÁLIDA")
            print("=" * 60)
            print(f"📁 {new_db_path}")
            print("✗ Faltan tablas o columnas requeridas")
            print("=" * 60)
            return 1
            
    except Exception as e:
        logger.error(f"Error validando la base de datos: {e}", exc_info=True)
        return 1
    finally:
        await new_db.dispose()