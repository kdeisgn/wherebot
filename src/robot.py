from typing import Optional

class Robot:
    """
    Minimal wrapper. If stretch_body is available, we init/startup.
    Otherwise we run in no-hardware mode without failing.
    """
    def __init__(self) -> None:
        self._robot = None
        try:
            import stretch_body.robot as rb  # type: ignore
            self._robot = rb.Robot()
            self._robot.startup()
            self.available = True
        except Exception:
            self.available = False

    def nod(self) -> None:
        """Simple acknowledgement motion if hardware is present."""
        if not self.available:
            print("[ROBOT] Not Available")
            return
        try:
            self._robot.head.move_to('look_down'); self._robot.push_command()
            self._robot.head.move_to('look_up');   self._robot.push_command()
        except Exception:
            pass

    def stop(self) -> None:
        try:
            if self._robot:
                self._robot.stop()
        except Exception:
            pass
