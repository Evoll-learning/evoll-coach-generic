-- ========================================
-- SCHEMA SUPABASE - PLATAFORMA EVOLL LIDERAZGO
-- ========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- TABLA: users
-- ========================================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    apellido TEXT NOT NULL,
    cargo TEXT,
    division TEXT,
    experiencia_anos INTEGER,
    tamano_equipo INTEGER,
    desafios_equipo TEXT,
    objetivos_personales TEXT,
    valores_comprometidos TEXT[],
    
    -- Telegram
    telegram_chat_id TEXT,
    notificaciones_activas BOOLEAN DEFAULT true,
    
    -- Gamificación
    puntos_totales INTEGER DEFAULT 0,
    nivel INTEGER DEFAULT 1,
    racha_dias INTEGER DEFAULT 0,
    ultima_actividad TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    onboarding_completed BOOLEAN DEFAULT false,
    
    -- Auth (Supabase Auth se encarga del password)
    auth_user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Index para búsquedas rápidas
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_telegram ON users(telegram_chat_id);
CREATE INDEX idx_users_auth ON users(auth_user_id);

-- ========================================
-- TABLA: respuestas_lmv
-- ========================================
CREATE TABLE IF NOT EXISTS respuestas_lmv (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Pregunta
    semana INTEGER NOT NULL,
    numero_envio TEXT,
    tipo TEXT CHECK (tipo IN ('Liderazgo', 'Management', 'Valores')),
    competencia TEXT,
    pregunta TEXT NOT NULL,
    
    -- Respuesta
    respuesta TEXT,
    fecha_respuesta TIMESTAMPTZ,
    tiempo_respuesta_segundos INTEGER,
    
    -- Evaluación
    evaluado BOOLEAN DEFAULT false,
    feedback TEXT,
    puntos_otorgados INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    enviado_via TEXT CHECK (enviado_via IN ('web', 'telegram', 'whatsapp'))
);

-- Indexes
CREATE INDEX idx_respuestas_user ON respuestas_lmv(user_id);
CREATE INDEX idx_respuestas_fecha ON respuestas_lmv(fecha_respuesta);
CREATE INDEX idx_respuestas_tipo ON respuestas_lmv(tipo);

-- ========================================
-- TABLA: conversaciones_coach
-- ========================================
CREATE TABLE IF NOT EXISTS conversaciones_coach (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID DEFAULT uuid_generate_v4(),
    
    -- Mensaje
    role TEXT CHECK (role IN ('user', 'assistant')) NOT NULL,
    content TEXT NOT NULL,
    
    -- Context
    contexto TEXT,
    tipo_consulta TEXT CHECK (tipo_consulta IN ('feedback', 'conflicto', 'estrategia', 'equipo', 'general')),
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    via TEXT CHECK (via IN ('web', 'vapi', 'audio'))
);

-- Indexes
CREATE INDEX idx_conversaciones_user ON conversaciones_coach(user_id);
CREATE INDEX idx_conversaciones_session ON conversaciones_coach(session_id);

-- ========================================
-- TABLA: telegram_messages
-- ========================================
CREATE TABLE IF NOT EXISTS telegram_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    chat_id TEXT NOT NULL,
    mensaje TEXT NOT NULL,
    fecha TIMESTAMPTZ DEFAULT NOW(),
    procesado BOOLEAN DEFAULT false,
    
    -- Asociación con pregunta L-M-V
    respuesta_lmv_id UUID REFERENCES respuestas_lmv(id) ON DELETE SET NULL
);

-- Index
CREATE INDEX idx_telegram_user ON telegram_messages(user_id);
CREATE INDEX idx_telegram_chat ON telegram_messages(chat_id);

-- ========================================
-- TABLA: posts_comunidad
-- ========================================
CREATE TABLE IF NOT EXISTS posts_comunidad (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    autor_nombre TEXT NOT NULL,
    contenido TEXT NOT NULL,
    tags TEXT[],
    likes INTEGER DEFAULT 0,
    comentarios INTEGER DEFAULT 0,
    fecha_creacion TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_posts_user ON posts_comunidad(user_id);
CREATE INDEX idx_posts_fecha ON posts_comunidad(fecha_creacion);

-- ========================================
-- TABLA: badges (Gamificación)
-- ========================================
CREATE TABLE IF NOT EXISTS badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo TEXT UNIQUE NOT NULL,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    icono TEXT,
    criterio_obtencion TEXT,
    puntos_requeridos INTEGER,
    rareza TEXT CHECK (rareza IN ('comun', 'raro', 'epico', 'legendario'))
);

-- ========================================
-- TABLA: user_badges
-- ========================================
CREATE TABLE IF NOT EXISTS user_badges (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_id UUID REFERENCES badges(id) ON DELETE CASCADE,
    obtenido_en TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, badge_id)
);

-- Index
CREATE INDEX idx_user_badges_user ON user_badges(user_id);

-- ========================================
-- TABLA: actividades (Tracking)
-- ========================================
CREATE TABLE IF NOT EXISTS actividades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    tipo TEXT CHECK (tipo IN ('login', 'respuesta_lmv', 'coach_consulta', 'modulo_completado', 'badge_obtenido')),
    descripcion TEXT,
    puntos_ganados INTEGER DEFAULT 0,
    
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index
CREATE INDEX idx_actividades_user ON actividades(user_id);
CREATE INDEX idx_actividades_fecha ON actividades(created_at);

-- ========================================
-- TABLA: user_sessions (Time tracking)
-- ========================================
CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    pagina TEXT,
    tiempo_inicio TIMESTAMPTZ DEFAULT NOW(),
    tiempo_fin TIMESTAMPTZ,
    duracion_segundos INTEGER,
    
    -- Metadata
    dispositivo TEXT,
    navegador TEXT
);

-- Index
CREATE INDEX idx_sessions_user ON user_sessions(user_id);

-- ========================================
-- ROW LEVEL SECURITY (RLS)
-- ========================================

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE respuestas_lmv ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversaciones_coach ENABLE ROW LEVEL SECURITY;
ALTER TABLE telegram_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;
ALTER TABLE actividades ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_sessions ENABLE ROW LEVEL SECURITY;

-- Policies: Users can only see their own data
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = auth_user_id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = auth_user_id);

CREATE POLICY "Users can view own responses" ON respuestas_lmv
    FOR SELECT USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = user_id));

CREATE POLICY "Users can insert own responses" ON respuestas_lmv
    FOR INSERT WITH CHECK (auth.uid() = (SELECT auth_user_id FROM users WHERE id = user_id));

CREATE POLICY "Users can view own conversations" ON conversaciones_coach
    FOR SELECT USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = user_id));

CREATE POLICY "Users can insert own conversations" ON conversaciones_coach
    FOR INSERT WITH CHECK (auth.uid() = (SELECT auth_user_id FROM users WHERE id = user_id));

CREATE POLICY "Users can view own badges" ON user_badges
    FOR SELECT USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = user_id));

CREATE POLICY "Users can view own activities" ON actividades
    FOR SELECT USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = user_id));

CREATE POLICY "Users can view own sessions" ON user_sessions
    FOR SELECT USING (auth.uid() = (SELECT auth_user_id FROM users WHERE id = user_id));

-- Badges table is public (everyone can see badges)
CREATE POLICY "Badges are viewable by everyone" ON badges
    FOR SELECT USING (true);

-- ========================================
-- FUNCIONES AUXILIARES
-- ========================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- DATOS INICIALES: Badges
-- ========================================

INSERT INTO badges (codigo, nombre, descripcion, icono, rareza, puntos_requeridos) VALUES
('primer_paso', 'Primer Paso', 'Completa tu primer módulo', '🚀', 'comun', 0),
('reflexivo', 'Líder Reflexivo', 'Responde 10 preguntas L-M-V', '💭', 'comun', 100),
('constante', 'Constancia', 'Mantén una racha de 7 días', '🔥', 'raro', 200),
('comunicador', 'Gran Comunicador', 'Consulta 20 veces al Coach IA', '💬', 'raro', 300),
('maestro', 'Maestro del Liderazgo', 'Completa todos los módulos', '🏆', 'epico', 1000),
('inspirador', 'Líder Inspirador', 'Alcanza 5000 puntos', '⭐', 'legendario', 5000)
ON CONFLICT (codigo) DO NOTHING;

-- ========================================
-- VIEWS ÚTILES
-- ========================================

-- View: Leaderboard
CREATE OR REPLACE VIEW leaderboard AS
SELECT 
    u.id,
    u.nombre,
    u.apellido,
    u.puntos_totales,
    u.nivel,
    u.racha_dias,
    COUNT(DISTINCT ub.badge_id) as total_badges,
    RANK() OVER (ORDER BY u.puntos_totales DESC) as ranking
FROM users u
LEFT JOIN user_badges ub ON u.id = ub.user_id
GROUP BY u.id, u.nombre, u.apellido, u.puntos_totales, u.nivel, u.racha_dias
ORDER BY u.puntos_totales DESC;

-- View: User progress
CREATE OR REPLACE VIEW user_progress AS
SELECT 
    u.id as user_id,
    u.nombre,
    u.apellido,
    COUNT(DISTINCT r.id) as respuestas_totales,
    COUNT(DISTINCT CASE WHEN r.tipo = 'Liderazgo' THEN r.id END) as respuestas_liderazgo,
    COUNT(DISTINCT CASE WHEN r.tipo = 'Management' THEN r.id END) as respuestas_management,
    COUNT(DISTINCT CASE WHEN r.tipo = 'Valores' THEN r.id END) as respuestas_valores,
    COUNT(DISTINCT c.id) as consultas_coach,
    u.puntos_totales,
    u.nivel,
    u.racha_dias
FROM users u
LEFT JOIN respuestas_lmv r ON u.id = r.user_id
LEFT JOIN conversaciones_coach c ON u.id = c.user_id
GROUP BY u.id, u.nombre, u.apellido, u.puntos_totales, u.nivel, u.racha_dias;
