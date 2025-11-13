import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Heart, MessageCircle, Send, Sparkles } from 'lucide-react';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

const ComunidadPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [posts, setPosts] = useState([]);
  const [nuevoPost, setNuevoPost] = useState('');
  const [selectedTags, setSelectedTags] = useState([]);
  const [loading, setLoading] = useState(false);

  const tagsDisponibles = ['#feedback', '#motivación', '#desafíos', '#logros', '#reflexión', '#equipo'];

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await axios.get(`${API_URL}/comunidad/posts`);
      setPosts(response.data);
    } catch (error) {
      console.error('Error fetching posts:', error);
    }
  };

  const handleCrearPost = async () => {
    if (!nuevoPost.trim()) {
      toast.error('Escribe algo antes de publicar');
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_URL}/comunidad/posts`, {
        contenido: nuevoPost,
        tags: selectedTags
      });
      toast.success('¡Post publicado!');
      setNuevoPost('');
      setSelectedTags([]);
      fetchPosts();
    } catch (error) {
      toast.error('Error al publicar');
    } finally {
      setLoading(false);
    }
  };

  const toggleTag = (tag) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  return (
    <div className="min-h-screen bg-[#0A1628]">
      {/* Header */}
      <header className="bg-[#132337] border-b border-[#2D3748] sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} data-testid="btn-back">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-xl font-bold text-white">Comunidad EvoLL</h1>
              <p className="text-sm text-gray-400">Comparte y aprende con otros líderes</p>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8 max-w-4xl">
        {/* Crear Nuevo Post */}
        <Card className="mb-8 bg-[#1A2F47] border-2 border-green-500/30 shadow-xl" data-testid="nuevo-post-card">
          <CardHeader>
            <CardTitle className="text-white">Comparte tu experiencia</CardTitle>
            <CardDescription className="text-gray-400">¿Qué has aprendido hoy? Compártelo con la comunidad</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              placeholder="Comparte tus reflexiones, logros o desafíos..."
              value={nuevoPost}
              onChange={(e) => setNuevoPost(e.target.value)}
              rows={4}
              className="text-slate-900"
              data-testid="textarea-nuevo-post"
            />
            <div>
              <p className="text-sm text-slate-700 mb-2 font-medium">Etiquetas:</p>
              <div className="flex flex-wrap gap-2">
                {tagsDisponibles.map((tag) => (
                  <Badge
                    key={tag}
                    variant={selectedTags.includes(tag) ? 'default' : 'outline'}
                    className={`cursor-pointer transition-all font-semibold ${
                      selectedTags.includes(tag) 
                        ? 'bg-green-600 hover:bg-green-700 text-white border-green-600' 
                        : 'bg-slate-700 text-white border-slate-600 hover:bg-slate-600'
                    }`}
                    onClick={() => toggleTag(tag)}
                    data-testid={`tag-${tag}`}
                  >
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
            <Button 
              onClick={handleCrearPost}
              disabled={loading}
              className="w-full bg-blue-900 hover:bg-blue-800"
              data-testid="btn-publicar"
            >
              {loading ? 'Publicando...' : 'Publicar'}
              <Send className="w-4 h-4 ml-2" />
            </Button>
          </CardContent>
        </Card>

        {/* Feed de Posts */}
        <div className="space-y-6">
          <h2 className="text-2xl font-bold text-slate-900">Feed de la comunidad</h2>
          {posts.length === 0 ? (
            <Card className="border-2 border-slate-100">
              <CardContent className="py-12 text-center">
                <Sparkles className="w-12 h-12 text-slate-400 mx-auto mb-4" />
                <p className="text-slate-600">Sé el primero en compartir algo con la comunidad</p>
              </CardContent>
            </Card>
          ) : (
            posts.map((post, index) => (
              <Card key={post.id || index} className="hover-lift border-2 border-slate-100" data-testid={`post-${index}`}>
                <CardHeader>
                  <div className="flex items-start space-x-4">
                    <Avatar>
                      <AvatarFallback className="bg-gradient-to-br from-blue-900 to-amber-500 text-white">
                        {post.autor_nombre.split(' ').map(n => n[0]).join('').toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <p className="font-semibold text-slate-900">{post.autor_nombre}</p>
                        <span className="text-xs text-slate-500">
                          {new Date(post.fecha_creacion).toLocaleDateString('es-ES')}
                        </span>
                      </div>
                      {post.tags && post.tags.length > 0 && (
                        <div className="flex gap-2 mt-2">
                          {post.tags.map((tag, idx) => (
                            <Badge key={idx} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-700 leading-relaxed">{post.contenido}</p>
                  <div className="flex items-center space-x-6 mt-4 text-slate-500">
                    <button className="flex items-center space-x-2 hover:text-red-500 transition-colors">
                      <Heart className="w-5 h-5" />
                      <span className="text-sm">{post.likes || 0}</span>
                    </button>
                    <button className="flex items-center space-x-2 hover:text-blue-500 transition-colors">
                      <MessageCircle className="w-5 h-5" />
                      <span className="text-sm">{post.comentarios || 0}</span>
                    </button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default ComunidadPage;