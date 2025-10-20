import requests
from typing import List, Dict, Optional
from django.conf import settings


class AniListAPI:
    """Servicio para interactuar con la API de AniList"""
    
    BASE_URL = 'https://graphql.anilist.co'
    
    @staticmethod
    def search_anime(query: str, limit: int = 20) -> List[Dict]:
        """
        Busca animes por título
        
        Args:
            query: Término de búsqueda
            limit: Número máximo de resultados
            
        Returns:
            Lista de animes con su información
        """
        graphql_query = '''
        query ($search: String, $perPage: Int) {
          Page(page: 1, perPage: $perPage) {
            media(search: $search, type: ANIME, sort: POPULARITY_DESC) {
              id
              title {
                romaji
                english
                native
              }
              description
              coverImage {
                large
                medium
              }
              bannerImage
              format
              status
              episodes
              duration
              genres
              averageScore
              popularity
              season
              seasonYear
              studios {
                nodes {
                  name
                }
              }
              siteUrl
            }
          }
        }
        '''
        
        variables = {
            'search': query,
            'perPage': limit
        }
        
        try:
            response = requests.post(
                AniListAPI.BASE_URL,
                json={'query': graphql_query, 'variables': variables},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for media in data.get('data', {}).get('Page', {}).get('media', []):
                results.append({
                    'external_id': str(media['id']),
                    'title': media['title']['romaji'] or media['title']['english'] or media['title']['native'],
                    'title_english': media['title'].get('english', ''),
                    'title_native': media['title'].get('native', ''),
                    'description': AniListAPI._clean_description(media.get('description', '')),
                    'cover_image': media['coverImage'].get('large', ''),
                    'banner_image': media.get('bannerImage', ''),
                    'format': media.get('format', ''),
                    'status': media.get('status', ''),
                    'episodes': media.get('episodes', 0),
                    'duration': media.get('duration', 0),
                    'genres': media.get('genres', []),
                    'score': media.get('averageScore', 0),
                    'popularity': media.get('popularity', 0),
                    'season': media.get('season', ''),
                    'year': media.get('seasonYear', 0),
                    'studios': [studio['name'] for studio in media.get('studios', {}).get('nodes', [])],
                    'url': media.get('siteUrl', ''),
                    'source': 'anilist'
                })
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar en AniList: {e}")
            return []
    
    @staticmethod
    def get_anime_by_id(anime_id: str) -> Optional[Dict]:
        """Obtiene información detallada de un anime por ID"""
        graphql_query = '''
        query ($id: Int) {
          Media(id: $id, type: ANIME) {
            id
            title {
              romaji
              english
              native
            }
            description
            coverImage {
              large
            }
            bannerImage
            format
            status
            episodes
            duration
            genres
            averageScore
            popularity
            season
            seasonYear
            studios {
              nodes {
                name
              }
            }
            siteUrl
          }
        }
        '''
        
        variables = {'id': int(anime_id)}
        
        try:
            response = requests.post(
                AniListAPI.BASE_URL,
                json={'query': graphql_query, 'variables': variables},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            media = data.get('data', {}).get('Media', {})
            
            if not media:
                return None
            
            return {
                'external_id': str(media['id']),
                'title': media['title']['romaji'] or media['title']['english'],
                'title_english': media['title'].get('english', ''),
                'description': AniListAPI._clean_description(media.get('description', '')),
                'cover_image': media['coverImage'].get('large', ''),
                'episodes': media.get('episodes', 0),
                'genres': media.get('genres', []),
                'score': media.get('averageScore', 0),
                'url': media.get('siteUrl', ''),
                'source': 'anilist'
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error al obtener anime de AniList: {e}")
            return None
    
    @staticmethod
    def _clean_description(description: str) -> str:
        """Limpia las etiquetas HTML de la descripción"""
        import re
        if not description:
            return ''
        # Remover tags HTML
        clean = re.sub('<[^<]+?>', '', description)
        # Limitar a 500 caracteres
        return clean[:500] + '...' if len(clean) > 500 else clean


class TVMazeAPI:
    """Servicio para interactuar con TVMaze"""
    BASE_URL = 'https://api.tvmaze.com'

    @staticmethod
    def _get_key() -> Optional[str]:
        return getattr(settings, 'TVMAZE_API_KEY', None)

    @staticmethod
    def search_shows(query: str, limit: int = 20) -> List[Dict]:
        """Busca shows en TVMaze usando /search/shows"""
        params = {'q': query}
        headers = {}
        key = TVMazeAPI._get_key()
        # TVMaze no requiere API key por defecto, pero si se proporciona la incluimos en headers
        if key:
            headers['Authorization'] = f'Bearer {key}'

        try:
            resp = requests.get(f"{TVMazeAPI.BASE_URL}/search/shows", params=params, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            results = []
            for item in data[:limit]:
                show = item.get('show', {})
                image = show.get('image') or {}
                cover = image.get('original') or image.get('medium') or ''
                premiered = show.get('premiered') or ''
                year = premiered.split('-')[0] if premiered else ''

                results.append({
                    'external_id': str(show.get('id', '')),
                    'title': show.get('name', ''),
          'description': (show.get('summary') or '')[:500],
          'cover_image': cover,
          'duration': show.get('runtime'),
          'episodes': show.get('_links', {}).get('episodes', None),
                    'media_type': 'show',
                    'year': year,
                    'score': show.get('rating', {}).get('average', 0),
                    'popularity': show.get('weight', 0),
                    'url': show.get('url', ''),
                    'source': 'tvmaze'
                })

            return results
        except requests.exceptions.RequestException as e:
            print(f"Error al buscar en TVMaze: {e}")
            return []