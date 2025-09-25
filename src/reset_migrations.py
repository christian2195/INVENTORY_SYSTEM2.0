#!/usr/bin/env python
import os
import shutil
from pathlib import Path

def reset_migrations():
    apps = [
        'inventory',
        'dispatch_notes',
        'movements', 
        'orders',
        'quotations',
        'reception_notes',
        'returns',
        'users'
    ]
    
    for app in apps:
        migrations_dir = Path(f"apps/{app}/migrations")
        if migrations_dir.exists():
            # Eliminar todas las migraciones excepto __init__.py
            for file in migrations_dir.iterdir():
                if file.name != "__init__.py":
                    if file.is_file():
                        file.unlink()
                    else:
                        shutil.rmtree(file)
            print(f"✅ Migraciones reseteadas para {app}")
        else:
            print(f"⚠️  No existe directorio para {app}")

if __name__ == "__main__":
    reset_migrations()