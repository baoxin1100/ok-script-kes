import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from ok.device.interaction_methods.adb import ADBInteraction


class TestAdbInteraction(unittest.TestCase):
    def make_interaction(self):
        device = SimpleNamespace(shell=Mock())
        manager = SimpleNamespace(device=device)
        with patch('ok.device.interaction_methods.adb.importlib.util.find_spec', return_value=None):
            interaction = ADBInteraction(manager, capture=None, device_width=1920, device_height=1080)
        return interaction, device.shell

    def test_keyboard_keys_use_android_keycode_names(self):
        interaction, shell = self.make_interaction()

        for key in ('0', '3', '9', 'e', 'F1', 'f12', 'enter'):
            interaction.send_key(key)

        self.assertEqual(
            [
                'input keyevent KEYCODE_0',
                'input keyevent KEYCODE_3',
                'input keyevent KEYCODE_9',
                'input keyevent KEYCODE_E',
                'input keyevent KEYCODE_F1',
                'input keyevent KEYCODE_F12',
                'input keyevent KEYCODE_ENTER',
            ],
            [call.args[0] for call in shell.call_args_list],
        )

    def test_explicit_numeric_keycode_remains_supported(self):
        interaction, shell = self.make_interaction()

        interaction.send_key('66')

        shell.assert_called_once_with('input keyevent 66')

    def test_adb_shell_swipe_uses_short_reverse_swipe_to_stop_inertia(self):
        interaction, shell = self.make_interaction()

        interaction.swipe(960, 756, 960, 324, 400, settle_time=0.3)

        self.assertEqual(
            [
                'input swipe 960 756 960 324 400',
                'input swipe 960 324 960 346 300',
            ],
            [call.args[0] for call in shell.call_args_list],
        )


if __name__ == '__main__':
    unittest.main()
