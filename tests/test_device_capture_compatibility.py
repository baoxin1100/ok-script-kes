import unittest
from types import SimpleNamespace

from ok.device.DeviceManager import supports_nemu_ipc


class TestDeviceCaptureCompatibility(unittest.TestCase):
    def test_mumu_versions_support_nemu_ipc(self):
        for emulator_type in ('MuMuPlayer', 'MuMuPlayerX', 'MuMuPlayer12'):
            preferred = {
                'emulator': SimpleNamespace(type=emulator_type),
            }
            self.assertTrue(supports_nemu_ipc(preferred))

    def test_ldplayer_does_not_support_nemu_ipc(self):
        preferred = {
            'emulator': SimpleNamespace(type='LDPlayer9'),
        }
        self.assertFalse(supports_nemu_ipc(preferred))

    def test_phone_without_emulator_does_not_support_nemu_ipc(self):
        self.assertFalse(supports_nemu_ipc({'device': 'adb'}))


if __name__ == '__main__':
    unittest.main()
