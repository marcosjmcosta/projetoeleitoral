import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
import main


class AuthenticationTests(unittest.TestCase):
    protected = (
        '/materias', '/materia/propaganda-eleitoral',
        '/materia/propaganda-eleitoral/referencias',
        '/agente22/contexto', '/agente23/contexto',
    )

    def setUp(self):
        self.key_patch = patch.object(main, 'PLUGIN_API_KEY', 'test-only-local-key')
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)
        self.client = TestClient(main.app)
        self.addCleanup(self.client.close)

    def test_invalid_credentials_never_reach_upstream(self):
        with patch.object(main, 'fetch_agentes_eleitoral', new_callable=AsyncMock) as upstream:
            for path in self.protected:
                for headers in ({}, {'Authorization': 'Bearer wrong'},
                                {'Authorization': 'Basic invalid'}):
                    with self.subTest(path=path, headers=headers):
                        response = self.client.get(path, headers=headers)
                        self.assertEqual(response.status_code, 401)
                        self.assertEqual(response.headers['www-authenticate'], 'Bearer')
            upstream.assert_not_awaited()

    def test_valid_key_allows_local_data(self):
        for path in ('/materias', '/agente22/contexto', '/agente23/contexto'):
            with self.subTest(path=path):
                response = self.client.get(path, headers={'Authorization': 'Bearer test-only-local-key'})
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response.json())

    def test_valid_key_allows_upstream_calls(self):
        with patch.object(main, 'fetch_agentes_eleitoral', new_callable=AsyncMock,
                          return_value={'conteudo': 'fixture'}) as upstream:
            for suffix in ('', '/referencias'):
                response = self.client.get('/materia/propaganda-eleitoral' + suffix,
                                          headers={'Authorization': 'Bearer test-only-local-key'})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json(), {'conteudo': 'fixture'})
                upstream.assert_awaited_with('/api/materias/propaganda-eleitoral' + suffix)

    def test_missing_or_placeholder_server_key_denies_access(self):
        for key in ('', 'DEFINA_UMA_CHAVE_FORTE_AQUI'):
            with patch.object(main, 'PLUGIN_API_KEY', key):
                for path in self.protected:
                    with self.subTest(key=key, path=path):
                        response = self.client.get(path, headers={'Authorization': 'Bearer test-only-local-key'})
                        self.assertEqual(response.status_code, 503)

    def test_public_endpoints_and_openapi(self):
        for path in ('/status', '/legal', '/.well-known/ai-plugin.json', '/docs', '/openapi.json'):
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)
        schema = self.client.get('/openapi.json').json()
        for path in ('/materias', '/materia/{materia_id}',
                     '/materia/{materia_id}/referencias', '/agente22/contexto', '/agente23/contexto'):
            self.assertEqual(schema['paths'][path]['get']['security'], [{'HTTPBearer': []}])


if __name__ == '__main__':
    unittest.main()
