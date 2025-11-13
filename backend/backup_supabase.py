#!/usr/bin/env python3.11
"""
Script de backup automático para Supabase
Exporta todas las tablas a JSON y las guarda en Railway Volumes
"""

import os
import json
from datetime import datetime
from supabase_client import supabase

# Tablas a respaldar
TABLES = [
    'usuarios',
    'respuestas_lmv',
    'posts_comunidad',
    'badges',
    'banco_preguntas',
    'telegram_users'
]

def backup_table(table_name):
    """Respalda una tabla específica"""
    try:
        print(f"📦 Respaldando tabla: {table_name}")
        response = supabase.table(table_name).select("*").execute()
        
        if response.data:
            return {
                'table': table_name,
                'count': len(response.data),
                'data': response.data,
                'timestamp': datetime.now().isoformat()
            }
        return None
    except Exception as e:
        print(f"❌ Error respaldando {table_name}: {str(e)}")
        return None

def main():
    """Función principal de backup"""
    print("🚀 Iniciando backup automático de Supabase...")
    
    # Crear directorio de backups si no existe
    backup_dir = "/app/backups"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Timestamp para el backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Respaldar todas las tablas
    backup_data = {
        'backup_date': datetime.now().isoformat(),
        'tables': {}
    }
    
    for table in TABLES:
        result = backup_table(table)
        if result:
            backup_data['tables'][table] = result
            print(f"✅ {table}: {result['count']} registros")
    
    # Guardar backup
    backup_file = f"{backup_dir}/backup_{timestamp}.json"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Backup completado: {backup_file}")
    
    # Limpiar backups antiguos (mantener últimos 7)
    cleanup_old_backups(backup_dir, keep=7)

def cleanup_old_backups(backup_dir, keep=7):
    """Elimina backups antiguos, mantiene los últimos N"""
    try:
        backups = sorted([
            f for f in os.listdir(backup_dir) 
            if f.startswith('backup_') and f.endswith('.json')
        ])
        
        if len(backups) > keep:
            for old_backup in backups[:-keep]:
                os.remove(os.path.join(backup_dir, old_backup))
                print(f"🗑️ Eliminado backup antiguo: {old_backup}")
    except Exception as e:
        print(f"⚠️ Error limpiando backups: {str(e)}")

if __name__ == "__main__":
    main()
