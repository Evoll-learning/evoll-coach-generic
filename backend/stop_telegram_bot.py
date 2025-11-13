#!/usr/bin/env python3
"""
Script de utilidad para detener cualquier instancia del bot de Telegram
Útil cuando hay conflictos de múltiples instancias
"""

import asyncio
import os
from telegram import Bot
from dotenv import load_dotenv

load_dotenv()

async def stop_all_bot_instances():
    """Detiene todas las instancias del bot eliminando el webhook"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN no configurado")
        return
    
    try:
        bot = Bot(token=token)
        
        # Eliminar webhook y limpiar updates pendientes
        result = await bot.delete_webhook(drop_pending_updates=True)
        
        if result:
            print("✅ Todas las instancias del bot han sido detenidas")
            print("✅ Webhook eliminado y updates pendientes limpiados")
            print("💡 Ahora puedes reiniciar el servidor backend")
        else:
            print("⚠️ No se pudo eliminar el webhook (puede que no existiera)")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🛑 Deteniendo todas las instancias del bot de Telegram...")
    asyncio.run(stop_all_bot_instances())
