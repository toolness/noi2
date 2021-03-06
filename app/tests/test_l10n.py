import os
from flask import Flask
from nose.tools import eq_

from .test_views import ViewTestCase
from app import l10n

def test_flask_security_strings_do_not_interpolate():
    app = Flask('test')
    l10n.configure_app(app)
    eq_(unicode(app.config['SECURITY_MSG_EMAIL_ALREADY_ASSOCIATED'][0]),
        '%(email)s is already associated with an account.')

def test_all_translations_exist():
    dirs = os.listdir('/noi/app/translations')
    for locale in l10n.TRANSLATIONS:
        if str(locale) not in dirs:
            raise Exception('Locale %s does not exist' % locale)

class LocalizationTests(ViewTestCase):
    def test_locale_is_en_by_default(self):
        res = self.client.get('/')
        assert '<html lang="en"' in res.data

    def test_locale_in_session_is_respected(self):
        assert 'es' in l10n.VALID_LOCALE_CODES
        with self.client.session_transaction() as sess:
            l10n.change_session_locale('es', session=sess)
        res = self.client.get('/')
        assert '<html lang="es"' in res.data

    def test_locale_in_accept_language_header_is_respected(self):
        assert 'es' in l10n.VALID_LOCALE_CODES
        res = self.client.get('/', headers={
            'Accept-Language': 'es'
        })
        assert '<html lang="es"' in res.data
