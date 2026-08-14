import unittest

from ok.util.window import get_player_id_from_cmdline


class TestGetPlayerIdFromCmdline(unittest.TestCase):
    def test_mumu_15_prefers_v_over_restart_pid(self):
        cmdline = [
            r'D:\MuMuPlayer\nx_device\15.0\shell\MuMuNxDevice.exe',
            '-r', 'true', '--restart-last-pid', '68016', '-v', '0',
            '--vm', 'MuMuPlayer-15.0-0',
        ]

        self.assertEqual(0, get_player_id_from_cmdline(cmdline))

    def test_mumu_vm_name_is_used_when_v_is_absent(self):
        cmdline = [
            'MuMuNxDevice.exe', '--restart-last-pid', '68016',
            '--vm', 'MuMuPlayer-15.0-3',
        ]

        self.assertEqual(3, get_player_id_from_cmdline(cmdline))

    def test_index_format_remains_supported(self):
        self.assertEqual(2, get_player_id_from_cmdline(['emulator.exe', '--index=2']))

    def test_legacy_numeric_format_remains_supported(self):
        self.assertEqual(4, get_player_id_from_cmdline(['emulator.exe', '4']))


if __name__ == '__main__':
    unittest.main()
