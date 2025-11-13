#!/usr/bin/env python3
"""
URGENT TEST - GET /api/lmv/mis-respuestas endpoint
Testing specifically for julio@evoll.es to see exact JSON response
"""

import asyncio
import aiohttp
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Get backend URL from frontend .env
def get_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

async def urgent_lmv_test():
    """URGENT: Test GET /api/lmv/mis-respuestas with julio@evoll.es credentials"""
    
    logger.info("🚨 URGENT TEST: GET /api/lmv/mis-respuestas")
    logger.info(f"🎯 Backend URL: {BASE_URL}")
    logger.info("👤 User: julio@evoll.es")
    logger.info("🔑 Password: test123")
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Login to get token
        logger.info("\n🔐 Step 1: Login to get authentication token")
        login_data = {
            "email": "julio@evoll.es",
            "password": "test123"
        }
        
        try:
            async with session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                logger.info(f"Login response status: {response.status}")
                
                if response.status == 200:
                    login_result = await response.json()
                    auth_token = login_result.get("access_token")
                    user_data = login_result.get("user", {})
                    
                    logger.info("✅ Login successful!")
                    logger.info(f"👤 User ID: {user_data.get('id')}")
                    logger.info(f"📧 Email: {user_data.get('email')}")
                    logger.info(f"👨‍💼 Name: {user_data.get('nombre')} {user_data.get('apellido')}")
                    
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Login failed: {response.status} - {error_text}")
                    return
                    
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return
        
        # Step 2: Call GET /api/lmv/mis-respuestas
        logger.info("\n📝 Step 2: GET /api/lmv/mis-respuestas")
        
        headers = {"Authorization": f"Bearer {auth_token}"}
        
        try:
            async with session.get(f"{API_BASE}/lmv/mis-respuestas", headers=headers) as response:
                logger.info(f"🔍 Response Status: {response.status}")
                logger.info(f"🔍 Response Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    logger.info("\n🎯 EXACT JSON RESPONSE FROM GET /api/lmv/mis-respuestas:")
                    logger.info("="*100)
                    logger.info(json.dumps(data, indent=2, ensure_ascii=False, default=str))
                    logger.info("="*100)
                    
                    # Analysis
                    logger.info(f"\n📊 ANALYSIS:")
                    logger.info(f"Response type: {type(data)}")
                    
                    if isinstance(data, list):
                        logger.info(f"Array length: {len(data)}")
                        
                        if len(data) == 0:
                            logger.warning("⚠️ EMPTY ARRAY - This is why frontend shows nothing!")
                            logger.info("🔍 Possible reasons:")
                            logger.info("   1. No L-M-V questions created for this user")
                            logger.info("   2. Database query issue")
                            logger.info("   3. User ID mismatch")
                        else:
                            logger.info(f"✅ Found {len(data)} items")
                            
                            # Show structure of each item
                            for i, item in enumerate(data[:3]):  # Show first 3 items
                                logger.info(f"\n📋 Item {i+1}:")
                                for key, value in item.items():
                                    if key == 'pregunta' and value:
                                        logger.info(f"   {key}: {str(value)[:80]}...")
                                    else:
                                        logger.info(f"   {key}: {value}")
                            
                            if len(data) > 3:
                                logger.info(f"   ... and {len(data) - 3} more items")
                            
                            # Check expected structure
                            expected_fields = ['id', 'user_id', 'semana', 'numero_envio', 'tipo', 'competencia', 'pregunta', 'respuesta', 'fecha_respuesta', 'puntos_otorgados']
                            first_item = data[0]
                            present_fields = list(first_item.keys())
                            missing_fields = [field for field in expected_fields if field not in first_item]
                            extra_fields = [field for field in first_item.keys() if field not in expected_fields]
                            
                            logger.info(f"\n🔍 FIELD ANALYSIS:")
                            logger.info(f"Present fields: {present_fields}")
                            if missing_fields:
                                logger.warning(f"Missing expected fields: {missing_fields}")
                            if extra_fields:
                                logger.info(f"Extra fields: {extra_fields}")
                            
                            # Check if questions have responses
                            answered = sum(1 for item in data if item.get('respuesta'))
                            unanswered = len(data) - answered
                            logger.info(f"\n📈 RESPONSE STATUS:")
                            logger.info(f"Answered questions: {answered}")
                            logger.info(f"Unanswered questions: {unanswered}")
                    else:
                        logger.error(f"❌ Expected array but got: {type(data)}")
                        logger.info(f"Actual data: {data}")
                
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Request failed: {response.status}")
                    logger.error(f"Error response: {error_text}")
                    
        except Exception as e:
            logger.error(f"❌ Request error: {e}")

if __name__ == "__main__":
    asyncio.run(urgent_lmv_test())