import importlib
import math
import time

from ok.device.capture_methods.base import BaseCaptureMethod
from ok.device.capture_methods.nemu_ipc import NemuIpcCaptureMethod
from ok.device.interaction_methods.base import BaseInteraction
from ok.device.interaction_methods.keys import ADB_KEY_MAP
from ok.device.interaction_methods.swipe import insert_swipe
from ok.util.logger import Logger

logger = Logger.get_logger(__name__)

class ADBInteraction(BaseInteraction):

    def __init__(self, device_manager, capture, device_width, device_height):
        super().__init__(capture)
        self.device_manager = device_manager
        self._u2 = None
        self._u2_device = None
        self._touch_position = None
        self.use_u2 = importlib.util.find_spec("uiautomator2")

    def send_key(self, key, down_time=0.02):
        key_text = str(key).strip()
        mapped_key = ADB_KEY_MAP.get(key_text.lower())
        if mapped_key is None:
            upper_key = key_text.upper()
            if len(upper_key) == 1 and upper_key.isalnum():
                mapped_key = f"KEYCODE_{upper_key}"
            elif upper_key.startswith('F') and upper_key[1:].isdigit() \
                    and 1 <= int(upper_key[1:]) <= 12:
                mapped_key = f"KEYCODE_{upper_key}"
            else:
                mapped_key = key_text
        self.device_manager.device.shell(f"input keyevent {mapped_key}")

    def input_text(self, text):
        # Convert each character to its Unicode code point
        # unicode_code_points = [ord(char) for char in text]
        #
        # # Iterate over the Unicode code points and send input key events
        # for code_point in unicode_code_points:
        self.device_manager.shell(f"input text {text}")

    @property
    def u2(self):
        if self._u2 is None or self._u2_device != self.device_manager.device:
            logger.info(f'init u2 device')
            import uiautomator2
            self._u2_device = self.device_manager.device
            self._u2 = uiautomator2.connect(self._u2_device)
        return self._u2

    def swipe_nemu(self, from_x, from_y, to_x, to_y, duration, settle_time=0):
        p2 = (to_x, to_y)
        points = insert_swipe(p0=(from_x, from_y), p3=p2)

        for point in points:
            self.capture.nemu_impl.down(*point)
            time.sleep(0.010)

        start = time.time()
        while time.time() - start < settle_time:
            self.capture.nemu_impl.down(*p2)
            time.sleep(0.140)

        self.capture.nemu_impl.up()

        time.sleep(0.1)

    def swipe_u2(self, from_x, from_y, to_x, to_y, duration, settle_time=0):
        """
        Performs a timed swipe gesture using low-level touch events, allowing
        a pause ('settle_time') at the end point before lifting the touch.
        The move itself is typically fast.
        Args:
            from_x (int): Starting X coordinate.
            from_y (int): Starting Y coordinate.
            to_x (int): Ending X coordinate.
            to_y (int): Ending Y coordinate.
            duration (int): Intended movement duration in milliseconds.
            settle_time (float): Seconds to pause at (to_x, to_y) before touch up.
        """
        # Touch down at the starting point
        self.u2.touch.down(from_x, from_y)
        # Optional small delay after touching down before starting move
        time.sleep(0.02)
        dx = to_x - from_x
        dy = to_y - from_y
        steps = max(1, int(max(abs(dx), abs(dy)) / 16))
        move_interval = max(0.0, duration / 1000) / steps
        logger.debug(
            f'swipe_u2 from=({from_x},{from_y}) to=({to_x},{to_y}) '
            f'duration_ms={duration} settle_time={settle_time} '
            f'steps={steps} move_interval={move_interval:.4f}'
        )
        for i in range(1, steps + 1):
            progress = i / steps
            current_x = int(from_x + dx * progress)
            current_y = int(from_y + dy * progress)
            self.u2.touch.move(current_x, current_y)
            if move_interval > 0:
                time.sleep(move_interval)
        # Move to the ending point (move itself is usually quick)
        self.u2.touch.move(to_x, to_y)
        # Pause for settle_time seconds *before* lifting the finger
        if settle_time > 0:
            settle_end = time.monotonic() + settle_time
            while time.monotonic() < settle_end:
                # Keep emitting a stationary move so games do not treat the
                # gesture as released early and start inertial scrolling.
                self.u2.touch.move(to_x, to_y)
                time.sleep(min(0.05, max(0.0, settle_end - time.monotonic())))
        # Lift the touch up at the ending point
        self.u2.touch.up(to_x, to_y)

    def swipe(self, from_x, from_y, to_x, to_y, duration, settle_time=0):
        if isinstance(self.capture, NemuIpcCaptureMethod):
            self.swipe_nemu(from_x, from_y, to_x, to_y, duration, settle_time)
        elif self.use_u2:
            self.swipe_u2(from_x, from_y, to_x, to_y, duration, settle_time)
        else:
            logger.debug(
                f'swipe_adb_shell from=({from_x},{from_y}) to=({to_x},{to_y}) '
                f'duration_ms={duration} settle_time={settle_time}'
            )
            self.device_manager.device.shell(
                f"input swipe {round(from_x)} {round(from_y)} {round(to_x)} {round(to_y)} {duration}")
            if settle_time > 0:
                dx = from_x - to_x
                dy = from_y - to_y
                distance = math.hypot(dx, dy)
                if distance > 0:
                    brake_distance = max(12.0, min(30.0, distance * 0.05))
                    brake_x = to_x + dx / distance * brake_distance
                    brake_y = to_y + dy / distance * brake_distance
                    settle_ms = max(1, round(settle_time * 1000))
                    logger.debug(
                        f'swipe_adb_shell brake from=({to_x},{to_y}) '
                        f'to=({brake_x:.1f},{brake_y:.1f}) duration_ms={settle_ms}'
                    )
                    self.device_manager.device.shell(
                        f"input swipe {round(to_x)} {round(to_y)} "
                        f"{round(brake_x)} {round(brake_y)} {settle_ms}"
                    )

    def click(self, x=-1, y=-1, move_back=False, name=None, down_time=0.01, move=True, key=None):
        super().click(x, y, name=name)
        x = round(x)
        y = round(y)
        if isinstance(self.capture, NemuIpcCaptureMethod):
            self.capture.nemu_impl.click_nemu_ipc(x, y)
        else:
            self.device_manager.shell(f"input tap {x} {y}")

    def mouse_down(self, x=-1, y=-1, name=None, key="left"):
        """按下并保持触摸，直到调用 mouse_up。"""
        x = round(x)
        y = round(y)
        self._touch_position = (x, y)
        if isinstance(self.capture, NemuIpcCaptureMethod):
            self.capture.nemu_impl.down(x, y)
        elif self.use_u2:
            self.u2.touch.down(x, y)
        else:
            self.device_manager.shell(f"input motionevent DOWN {x} {y}")

    def mouse_up(self, key="left"):
        """释放由 mouse_down 保持的触摸。"""
        x, y = self._touch_position or (0, 0)
        try:
            if isinstance(self.capture, NemuIpcCaptureMethod):
                self.capture.nemu_impl.up()
            elif self.use_u2:
                self.u2.touch.up(x, y)
            else:
                self.device_manager.shell(f"input motionevent UP {x} {y}")
        finally:
            self._touch_position = None

    def back(self):
        self.send_key('KEYCODE_BACK')
