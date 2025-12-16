# Investigation de l'API Total Global Sports

Date: 2025-12-16T14:42:31.546715

## Résumé

- Endpoints testés: 86
- Endpoints accessibles: 0
- Endpoints bloqués: 86
- Patterns découverts: 0

## Endpoints Bloqués (échantillon)

- GET https://public.totalglobalsports.com/api/events - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /api/events (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/api/v1/events - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /api/v1/events (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/api/v2/events - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /api/v2/events (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/api/tournaments - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /api/tournaments (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/api/schedules - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /api/schedules (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/api/games - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /api/games (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/api/teams - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /api/teams (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/public/event - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /public/event (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/public/events - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /public/events (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))
- GET https://public.totalglobalsports.com/public/tournament - HTTPSConnectionPool(host='public.totalglobalsports.com', port=443): Max retries exceeded with url: /public/tournament (Caused by ProxyError('Unable to connect to proxy', OSError('Tunnel connection failed: 403 Forbidden')))

## Recommandations


✗ Aucun endpoint API public n'a été trouvé.

Options:
1. **Contacter TGS directement** pour demander accès à l'API
2. **Web Scraping** des pages publiques HTML
3. **Reverse engineering** de l'application web (avec autorisation)
4. **Utiliser le mode développeur du navigateur** pour observer les appels API réels