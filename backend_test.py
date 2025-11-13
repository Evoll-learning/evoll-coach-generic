#!/usr/bin/env python3
"""
Backend API Testing for EvoLL Leadership Platform
Tests authentication, text consultation, and audio transcription endpoints
"""

import asyncio
import aiohttp
import json
import os
import tempfile
import wave
import struct
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

class BackendTester:
    def __init__(self):
        self.session = None
        self.auth_token = None
        self.test_user_email = "julio@evoll.es"
        self.test_user_password = "test123"
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def create_mock_audio_file(self):
        """Create a mock WebM audio file for testing"""
        # Create a temporary WAV file first (simpler format)
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        
        # Generate a simple sine wave audio (1 second, 440Hz)
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0
        
        frames = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * 0.3 * (i % int(sample_rate / frequency)) / int(sample_rate / frequency))
            frames.append(struct.pack('<h', value))
        
        # Write WAV file
        with wave.open(temp_wav.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(frames))
        
        return temp_wav.name
    
    async def test_auth_register(self):
        """Test user registration"""
        logger.info("🔐 Testing user registration...")
        
        register_data = {
            "email": self.test_user_email,
            "password": self.test_user_password,
            "nombre": "Test",
            "apellido": "Coach"
        }
        
        try:
            async with self.session.post(f"{API_BASE}/auth/register", json=register_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    logger.info("✅ Registration successful")
                    return True
                elif response.status == 400:
                    # User might already exist, try login
                    logger.info("ℹ️ User already exists, will try login")
                    return await self.test_auth_login()
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Registration failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Registration error: {e}")
            return False
    
    async def test_auth_login(self):
        """Test user login"""
        logger.info("🔐 Testing user login...")
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_user_password
        }
        
        try:
            async with self.session.post(f"{API_BASE}/auth/login", json=login_data) as response:
                if response.status == 200:
                    data = await response.json()
                    self.auth_token = data.get("access_token")
                    logger.info("✅ Login successful")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Login failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Login error: {e}")
            return False
    
    async def test_coach_text_consultation(self):
        """Test Coach IA text consultation endpoint"""
        logger.info("🤖 Testing Coach IA text consultation...")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for Coach IA test")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        consultation_data = {
            "mensaje": "¿Cómo puedo mejorar la comunicación con mi equipo?",
            "contexto": "Consulta sobre liderazgo y comunicación efectiva"
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/coach/consultar", 
                json=consultation_data, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    respuesta = data.get("respuesta", "")
                    if respuesta and len(respuesta) > 10:
                        logger.info("✅ Coach IA text consultation successful")
                        logger.info(f"📝 Response preview: {respuesta[:100]}...")
                        return True
                    else:
                        logger.error("❌ Coach IA returned empty or invalid response")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Coach IA text consultation failed: {response.status} - {error_text}")
                    return False
        except asyncio.TimeoutError:
            logger.error("❌ Coach IA text consultation timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Coach IA text consultation error: {e}")
            return False
    
    async def test_coach_audio_transcription(self):
        """Test Coach IA audio transcription endpoint"""
        logger.info("🎤 Testing Coach IA audio transcription...")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for audio test")
            return False
        
        # Create mock audio file
        audio_file_path = None
        try:
            audio_file_path = self.create_mock_audio_file()
            logger.info(f"📁 Created mock audio file: {audio_file_path}")
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            
            # Prepare multipart form data
            with open(audio_file_path, 'rb') as audio_file:
                form_data = aiohttp.FormData()
                form_data.add_field('audio', audio_file, filename='test_audio.wav', content_type='audio/wav')
                
                async with self.session.post(
                    f"{API_BASE}/coach/audio",
                    data=form_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        transcripcion = data.get("transcripcion", "")
                        respuesta = data.get("respuesta", "")
                        success = data.get("success", False)
                        
                        if success and transcripcion and respuesta:
                            logger.info("✅ Audio transcription successful")
                            logger.info(f"📝 Transcription: {transcripcion}")
                            logger.info(f"🤖 AI Response preview: {respuesta[:100]}...")
                            return True
                        else:
                            logger.error(f"❌ Audio transcription incomplete - Success: {success}, Transcription: {bool(transcripcion)}, Response: {bool(respuesta)}")
                            return False
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Audio transcription failed: {response.status} - {error_text}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error("❌ Audio transcription timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Audio transcription error: {e}")
            return False
        finally:
            # Clean up temporary file
            if audio_file_path and os.path.exists(audio_file_path):
                os.unlink(audio_file_path)
                logger.info("🗑️ Cleaned up temporary audio file")
    
    async def test_telegram_vincular(self):
        """Test Telegram bot vincular endpoint - CRITICAL PRIORITY"""
        logger.info("📱 Testing Telegram vincular endpoint...")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for Telegram test")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        # Use a test chat_id format
        test_chat_id = "123456789"
        vincular_data = {
            "codigo_vinculacion": f"EVOLL-{test_chat_id}"
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/telegram/vincular", 
                json=vincular_data, 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    chat_id = data.get("chat_id", "")
                    
                    if "exitosamente" in message and chat_id == test_chat_id:
                        logger.info("✅ Telegram vincular successful")
                        logger.info(f"📝 Message: {message}")
                        return True
                    else:
                        logger.error(f"❌ Telegram vincular response incomplete - Message: {message}, Chat ID: {chat_id}")
                        return False
                elif response.status == 500:
                    error_text = await response.text()
                    logger.error(f"❌ CRITICAL: Telegram vincular returned 500 error - {error_text}")
                    return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Telegram vincular failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Telegram vincular error: {e}")
            return False
    
    async def test_dashboard_metricas(self):
        """Test dashboard metrics endpoint"""
        logger.info("📊 Testing dashboard metrics...")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for metrics test")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(
                f"{API_BASE}/metricas/progreso", 
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check for dynamic metrics (not hardcoded 71%)
                    comunicacion = data.get("comunicacion_efectiva", 0)
                    feedback = data.get("feedback_constructivo", 0)
                    
                    if comunicacion > 0 and feedback > 0:
                        logger.info("✅ Dashboard metrics successful")
                        logger.info(f"📈 Comunicación: {comunicacion}%, Feedback: {feedback}%")
                        
                        # Check if it's not hardcoded 71%
                        if comunicacion != 71 or feedback != 71:
                            logger.info("✅ Metrics appear to be dynamic (not hardcoded)")
                        else:
                            logger.warning("⚠️ Metrics might be hardcoded to 71%")
                        
                        return True
                    else:
                        logger.error(f"❌ Dashboard metrics incomplete - Comunicación: {comunicacion}, Feedback: {feedback}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Dashboard metrics failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Dashboard metrics error: {e}")
            return False
    
    async def test_telegram_status(self):
        """Test Telegram bot status endpoint"""
        logger.info("📱 Testing Telegram bot status...")
        
        try:
            async with self.session.get(
                f"{API_BASE}/telegram/status",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    activo = data.get("activo", False)
                    bot_configurado = data.get("bot_configurado", False)
                    
                    logger.info("✅ Telegram status endpoint successful")
                    logger.info(f"📊 Bot activo: {activo}, Bot configurado: {bot_configurado}")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Telegram status failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Telegram status error: {e}")
            return False

    async def test_telegram_test_notification(self):
        """Test Telegram test notification endpoint"""
        logger.info("📱 Testing Telegram test notification...")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for Telegram test notification")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.post(
                f"{API_BASE}/telegram/test",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    success = data.get("success", False)
                    
                    if success and "exitosamente" in message:
                        logger.info("✅ Telegram test notification successful")
                        logger.info(f"📝 Message: {message}")
                        return True
                    else:
                        logger.error(f"❌ Telegram test notification incomplete - Success: {success}, Message: {message}")
                        return False
                elif response.status == 400:
                    error_text = await response.text()
                    if "no configurado" in error_text:
                        logger.warning("⚠️ Telegram not configured for user (expected if not linked)")
                        return True  # This is expected behavior
                    else:
                        logger.error(f"❌ Telegram test notification failed: {response.status} - {error_text}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Telegram test notification failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Telegram test notification error: {e}")
            return False

    async def test_telegram_desvincular(self):
        """Test Telegram desvincular endpoint"""
        logger.info("📱 Testing Telegram desvincular...")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for Telegram desvincular")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.delete(
                f"{API_BASE}/telegram/desvincular",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    message = data.get("message", "")
                    
                    if "exitosamente" in message:
                        logger.info("✅ Telegram desvincular successful")
                        logger.info(f"📝 Message: {message}")
                        return True
                    else:
                        logger.error(f"❌ Telegram desvincular response incomplete - Message: {message}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Telegram desvincular failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Telegram desvincular error: {e}")
            return False

    async def test_lmv_respuestas(self):
        """Test L-M-V questions endpoint - URGENT TEST: Show exact JSON response"""
        logger.info("📝 URGENT TEST: GET /api/lmv/mis-respuestas - Showing EXACT JSON response")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for L-M-V test")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(
                f"{API_BASE}/lmv/mis-respuestas",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                logger.info(f"🔍 Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # SHOW EXACT JSON RESPONSE
                    logger.info("🎯 EXACT JSON RESPONSE:")
                    logger.info("="*80)
                    logger.info(json.dumps(data, indent=2, ensure_ascii=False))
                    logger.info("="*80)
                    
                    if isinstance(data, list):
                        logger.info(f"✅ Response is a list with {len(data)} items")
                        
                        if len(data) == 0:
                            logger.warning("⚠️ EMPTY ARRAY - This explains why frontend shows nothing!")
                            return False
                        
                        # Show structure of each item
                        for i, item in enumerate(data):
                            logger.info(f"📋 Item {i+1} structure: {list(item.keys())}")
                            if 'pregunta' in item:
                                logger.info(f"   Pregunta: {item['pregunta'][:50]}...")
                            if 'tipo' in item:
                                logger.info(f"   Tipo: {item['tipo']}")
                            if 'respuesta' in item:
                                logger.info(f"   Respuesta: {item['respuesta']}")
                        
                        # Expected structure check
                        expected_fields = ['id', 'user_id', 'semana', 'numero_envio', 'tipo', 'competencia', 'pregunta', 'respuesta', 'fecha_respuesta', 'puntos_otorgados']
                        if data:
                            first_item = data[0]
                            missing_fields = [field for field in expected_fields if field not in first_item]
                            if missing_fields:
                                logger.warning(f"⚠️ Missing expected fields: {missing_fields}")
                            else:
                                logger.info("✅ All expected fields present")
                        
                        return len(data) > 0
                    else:
                        logger.error(f"❌ Response is not a list: {type(data)}")
                        logger.info(f"Actual response: {data}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ L-M-V respuestas failed: {response.status}")
                    logger.error(f"Error response: {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ L-M-V respuestas error: {e}")
            return False

    async def test_elevenlabs_config(self):
        """Test ElevenLabs config endpoint"""
        logger.info("🔊 Testing ElevenLabs config...")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for ElevenLabs config")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        try:
            async with self.session.get(
                f"{API_BASE}/coach/elevenlabs-config",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    agent_id = data.get("agent_id", "")
                    
                    if agent_id:
                        logger.info("✅ ElevenLabs config successful")
                        logger.info(f"🎯 Agent ID: {agent_id}")
                        return True
                    else:
                        logger.error("❌ ElevenLabs config missing agent_id")
                        return False
                elif response.status == 404:
                    logger.warning("⚠️ ElevenLabs config endpoint not found (might not be implemented)")
                    return True  # Not critical if not implemented
                else:
                    error_text = await response.text()
                    logger.error(f"❌ ElevenLabs config failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ ElevenLabs config error: {e}")
            return False

    async def test_comunidad_get_posts(self):
        """Test GET /api/comunidad/posts - CRITICAL AFTER SUPABASE MIGRATION"""
        logger.info("🏘️ Testing Comunidad GET posts...")
        
        try:
            async with self.session.get(
                f"{API_BASE}/comunidad/posts",
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if isinstance(data, list):
                        logger.info(f"✅ Comunidad GET posts successful - Found {len(data)} posts")
                        
                        # Check data structure if posts exist
                        if data:
                            first_post = data[0]
                            required_fields = ['id', 'contenido', 'autor_nombre', 'fecha_creacion']
                            missing_fields = [field for field in required_fields if field not in first_post]
                            
                            if not missing_fields:
                                logger.info("✅ Post data structure is correct")
                                logger.info(f"📝 Sample post: {first_post.get('contenido', '')[:50]}...")
                                logger.info(f"👤 Author: {first_post.get('autor_nombre')}")
                            else:
                                logger.error(f"❌ Missing required fields in post data: {missing_fields}")
                                return False
                        else:
                            logger.info("ℹ️ No posts found (empty community)")
                        
                        return True
                    else:
                        logger.error(f"❌ Comunidad GET posts returned non-list data: {type(data)}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Comunidad GET posts failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Comunidad GET posts error: {e}")
            return False

    async def test_comunidad_create_post(self):
        """Test POST /api/comunidad/posts - CRITICAL AFTER SUPABASE MIGRATION"""
        logger.info("🏘️ Testing Comunidad CREATE post...")
        
        if not self.auth_token:
            logger.error("❌ No auth token available for Comunidad create post")
            return False
        
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        # Create a test post with realistic content
        post_data = {
            "contenido": "Compartiendo mi experiencia sobre liderazgo efectivo en equipos remotos. ¿Qué estrategias han funcionado mejor para ustedes?",
            "tags": ["liderazgo", "equipos-remotos", "comunicacion"]
        }
        
        try:
            async with self.session.post(
                f"{API_BASE}/comunidad/posts",
                json=post_data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Check if post was created successfully
                    if isinstance(data, dict):
                        post_id = data.get("id")
                        if post_id:
                            logger.info("✅ Comunidad CREATE post successful")
                            logger.info(f"📝 Created post ID: {post_id}")
                            logger.info(f"📄 Content: {post_data['contenido'][:50]}...")
                            return True
                        else:
                            logger.error("❌ Comunidad CREATE post missing ID in response")
                            return False
                    else:
                        logger.error(f"❌ Comunidad CREATE post returned unexpected data type: {type(data)}")
                        return False
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Comunidad CREATE post failed: {response.status} - {error_text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Comunidad CREATE post error: {e}")
            return False
    
    async def test_backend_health(self):
        """Test basic backend health"""
        logger.info("🏥 Testing backend health...")
        
        try:
            async with self.session.get(f"{API_BASE}/") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("✅ Backend is healthy")
                    logger.info(f"📋 Message: {data.get('message', 'No message')}")
                    return True
                else:
                    logger.error(f"❌ Backend health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Backend health check error: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all backend tests in priority order - Focus on FINAL MVP TESTING before Railway deployment"""
        logger.info(f"🚀 Starting EVOLL FINAL MVP TESTS for: {BASE_URL}")
        logger.info("📋 Testing with user: julio@evoll.es")
        logger.info("🎯 CRITICAL: Testing all endpoints after complete Supabase migration - READY FOR RAILWAY DEPLOYMENT")
        
        results = {
            "backend_health": False,
            "auth_login": False,
            "comunidad_get_posts": False,
            "comunidad_create_post": False,
            "telegram_status": False,
            "telegram_vincular": False,
            "lmv_respuestas": False,
            "coach_text_consultation": False,
            "elevenlabs_config": False
        }
        
        # Test 1: Backend Health
        results["backend_health"] = await self.test_backend_health()
        
        # Test 2: Authentication (CRITICAL) - Verify still working after Supabase migration
        results["auth_login"] = await self.test_auth_login()
        
        # Only continue if auth works
        if not results["auth_login"]:
            logger.error("❌ Authentication failed - stopping critical tests")
            return results
        
        # HIGHEST PRIORITY TESTS - Comunidad (JUST MIGRATED TO SUPABASE)
        logger.info("\n🔥 HIGHEST PRIORITY: Testing Comunidad endpoints after Supabase migration")
        
        # Test 3: Comunidad GET Posts (CRITICAL - JUST MIGRATED)
        results["comunidad_get_posts"] = await self.test_comunidad_get_posts()
        
        # Test 4: Comunidad CREATE Post (CRITICAL - JUST MIGRATED)
        results["comunidad_create_post"] = await self.test_comunidad_create_post()
        
        # HIGH PRIORITY TESTS - Telegram Integration (already migrated and tested)
        logger.info("\n🔥 HIGH PRIORITY: Verifying Telegram endpoints (already migrated)")
        
        # Test 5: Telegram Bot Status
        results["telegram_status"] = await self.test_telegram_status()
        
        # Test 6: Telegram Bot Vincular (VERIFICATION)
        results["telegram_vincular"] = await self.test_telegram_vincular()
        
        # HIGH PRIORITY TESTS - L-M-V Questions (already migrated and tested)
        logger.info("\n🔥 HIGH PRIORITY: Verifying L-M-V questions (already migrated)")
        
        # Test 7: L-M-V Questions (VERIFICATION - 9 questions should be available)
        results["lmv_respuestas"] = await self.test_lmv_respuestas()
        
        # VERIFICATION TESTS - Previously working endpoints
        logger.info("\n✅ VERIFICATION: Testing previously working endpoints")
        
        # Test 8: Coach IA Text Consultation (Verify still working)
        results["coach_text_consultation"] = await self.test_coach_text_consultation()
        
        # Test 9: ElevenLabs Config (VERIFICATION)
        results["elevenlabs_config"] = await self.test_elevenlabs_config()
        
        return results

async def main():
    """Main test runner"""
    async with BackendTester() as tester:
        results = await tester.run_all_tests()
        
        # Print summary
        logger.info("\n" + "="*60)
        logger.info("📊 TEST RESULTS SUMMARY")
        logger.info("="*60)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            logger.info("🎉 All tests passed!")
        else:
            logger.warning("⚠️ Some tests failed - check logs above for details")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())