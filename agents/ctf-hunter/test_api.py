import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Check for common API vulnerabilities and interesting endpoints
endpoints = [
    ('https://id.oppo.com/graphql', 'POST'),
    ('https://id.oppo.com/admin/', 'GET'),
    ('https://id.oppo.com/debug/', 'GET'),
    ('https://id.oppo.com/actuator/', 'GET'),
    ('https://id.oppo.com/health', 'GET'),
    ('https://id.oppo.com/metrics', 'GET'),
    ('https://id.oppo.com/api/health', 'GET'),
    ('https://id.oppo.com/api-docs', 'GET'),
    ('https://id.oppo.com/swagger.json', 'GET'),
    ('https://id.oppo.com/openapi.json', 'GET'),
    ('https://id.oppo.com/api/swagger', 'GET'),
    ('https://id.oppo.com/v3/swagger-ui.html', 'GET'),
]

print("Testing various endpoints...")
for url, method in endpoints:
    try:
        req = urllib.request.Request(url, method=method)
        req.add_header('User-Agent', 'Mozilla/5.0')
        req.add_header('Origin', 'https://evil.com')
        response = urllib.request.urlopen(req, timeout=5, context=ctx)
        
        cors_header = response.headers.get('Access-Control-Allow-Origin', 'Not-Set')
        content_type = response.headers.get('Content-Type', 'unknown')
        
        print(f'[+] {method} {url} -> {response.status}')
        print(f'    CORS: {cors_header}, Content-Type: {content_type}')
    except urllib.error.HTTPError as e:
        if e.code in [301, 302, 307, 308]:
            loc = e.headers.get("Location", "unknown")
            print(f'[Redirect] {method} {url} -> {e.code} -> {loc}')
        elif e.code not in [404, 403]:
            print(f'[HTTP Error] {method} {url} -> {e.code}')
    except Exception as e:
        print(f'[Error] {url}: {str(e)[:60]}')

print('\nChecking for CORS misconfigs...')
cors_test_urls = [
    'https://id.oppo.com/api/v3/',
    'https://id.heytap.com/api/v3/',
    'https://id.realme.com/api/v3/',
]

for url in cors_test_urls:
    try:
        req = urllib.request.Request(url, method='OPTIONS')
        req.add_header('Origin', 'https://attacker.com')
        req.add_header('Access-Control-Request-Method', 'POST')
        response = urllib.request.urlopen(req, timeout=5, context=ctx)
        acao = response.headers.get('Access-Control-Allow-Origin', 'Not-Set')
        acac = response.headers.get('Access-Control-Allow-Credentials', 'Not-Set')
        print(f'CORS {url}: ACAO={acao}, ACAC={acac}')
    except Exception as e:
        pass
