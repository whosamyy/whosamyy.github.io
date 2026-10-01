import os
import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from sqlalchemy import create_mock_engine
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import create_app, as_utc
from models import db


class DeploymentTest(unittest.TestCase):
    def test_default_sqlite(self):
        with patch.dict(os.environ, {}, clear=True):
            app = create_app()
        self.assertEqual(app.config['SQLALCHEMY_DATABASE_URI'], 'sqlite:///lock_in_bro.db')
        client = app.test_client()
        self.assertEqual(client.get('/api/health').json, {'status': 'healthy'})
        for path in ['/', '/?client_id=', '/?client_id=missing', '/?client_id=invalid%2Fid']:
            self.assertEqual(client.get(path).status_code, 200)

    def test_postgres_driver_and_url(self):
        for scheme in ['postgres', 'postgresql', 'postgresql+psycopg']:
            # No credentials or real server, and engine construction does not connect.
            with patch.dict(os.environ, {'DATABASE_URL': f'{scheme}://localhost/test?sslmode=require'}):
                app = create_app()
            with app.app_context():
                self.assertEqual(db.engine.dialect.driver, 'psycopg')
                self.assertEqual(db.engine.url.host, 'localhost')
                self.assertEqual(db.engine.url.database, 'test')
                self.assertEqual(db.engine.url.query['sslmode'], 'require')
                db.engine.dispose()

    def test_postgres_schema_and_init_command(self):
        statements = []
        engine = create_mock_engine('postgresql+psycopg://', lambda sql, *a, **kw: statements.append(str(sql.compile(dialect=engine.dialect))))
        db.metadata.create_all(engine, checkfirst=False)
        ddl = '\n'.join(statements)
        self.assertIn('CREATE TABLE focus_session', ddl)
        self.assertIn('CREATE TABLE blocked_attempt', ddl)
        self.assertIn('FOREIGN KEY(session_id)', ddl)
        self.assertIn('blocked_domains JSON', ddl)
        self.assertIn('TIMESTAMP WITH TIME ZONE', ddl)
        with patch.dict(os.environ, {'DATABASE_URL': 'postgresql://localhost/test'}):
            app = create_app()
        with patch.object(db, 'create_all') as create_all:
            result = app.test_cli_runner().invoke(args=['init-db'])
        self.assertEqual(result.exit_code, 0, result.output)
        create_all.assert_called_once_with()
        self.assertIn('Database initialized.', result.output)

    def test_utc_dates(self):
        expected = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)
        self.assertEqual(as_utc(datetime(2026, 9, 30, 12)), expected)
        self.assertEqual(as_utc(datetime(2026, 9, 30, 14, tzinfo=timezone(timedelta(hours=2)))), expected)


if __name__ == '__main__':
    unittest.main()
