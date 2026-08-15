import os
import tempfile
import unittest
from pathlib import Path

from ok.capture.adb.nemu_ipc import get_nemu_ipc_dll_candidates


class TestNemuIpcVersions(unittest.TestCase):
    def test_discovers_supported_versions_and_prefers_newest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for version in ('11.0', '12.0', '15.0', '16.1', 'invalid'):
                (root / 'nx_device' / version).mkdir(parents=True)

            candidates = get_nemu_ipc_dll_candidates(temp_dir)
            relative = [os.path.relpath(path, temp_dir).replace('\\', '/') for path in candidates]

            self.assertEqual(
                [
                    'nx_device/16.1/shell/sdk/external_renderer_ipc.dll',
                    'nx_device/15.0/shell/sdk/external_renderer_ipc.dll',
                    'nx_device/12.0/shell/sdk/external_renderer_ipc.dll',
                ],
                relative[:3],
            )
            self.assertFalse(any('11.0' in path for path in relative))


if __name__ == '__main__':
    unittest.main()
