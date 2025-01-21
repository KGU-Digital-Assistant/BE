import unittest

from ulid import ULID

from config import Settings

class SettingsTest(unittest.TestCase):
    def settings_test(self):
        settings = Settings()

        assert(settings.POSTGRES_USER != '')


class UlidTest(unittest.TestCase):
    def ulid_test(self):
        new_id = ULID()

        self.assertNotEqual(new_id, '', "ULID should not be an empty string.")  # 조건 실패 시 메시지 출력

if __name__ == '__main__':
    unittest.main()