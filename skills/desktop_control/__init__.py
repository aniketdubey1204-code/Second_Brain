"""
Desktop Control - Advanced Mouse, Keyboard, and Screen Automation
The best ever possible responsive desktop control for OpenClaw
"""

import pyautogui
import time
import sys
from typing import Tuple, Optional, List, Union
from pathlib import Path
import logging

# Configure PyAutoGUI
pyautogui.MINIMUM_DURATION = 0  # Allow instant movements
pyautogui.MINIMUM_SLEEP = 0     # No forced delays
pyautogui.PAUSE = 0             # No pause between function calls

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DesktopController:
    """
    Advanced desktop automation controller with mouse, keyboard, and screen operations.
    Designed for maximum responsiveness and reliability.
    """
    
    def __init__(self, failsafe: bool = True, require_approval: bool = False):
        """
        Initialize desktop controller.
        
        Args:
            failsafe: Enable failsafe (move mouse to corner to abort)
            require_approval: Require user confirmation for actions
        """
        self.failsafe = failsafe
        self.require_approval = require_approval
        pyautogui.FAILSAFE = failsafe
        
        # Get screen info
        self.screen_width, self.screen_height = pyautogui.size()
        logger.info(f"Desktop Controller initialized. Screen: {self.screen_width}x{self.screen_height}")
        logger.info(f"Failsafe: {failsafe}, Require Approval: {require_approval}")
    
    # ========== MOUSE OPERATIONS ==========
    
    def move_mouse(self, x: int, y: int, duration: float = 0, smooth: bool = True) -> None:
        """
        Move mouse to absolute screen coordinates.
        
        Args:
            x: X coordinate (pixels from left)
            y: Y coordinate (pixels from top)
            duration: Movement time in seconds (0 = instant)
            smooth: Use smooth movement (cubic bezier)
        """
        if self._check_approval(f"move mouse to ({x}, {y})"):
            if smooth and duration > 0:
                pyautogui.moveTo(x, y, duration=duration, tween=pyautogui.easeInOutQuad)
            else:
                pyautogui.moveTo(x, y, duration=duration)
            logger.debug(f"Moved mouse to ({x}, {y}) in {duration}s")
    
    def move_relative(self, x_offset: int, y_offset: int, duration: float = 0) -> None:
        """
        Move mouse relative to current position.
        
        Args:
            x_offset: Pixels to move horizontally (+ = right, - = left)
            y_offset: Pixels to move vertically (+ = down, - = up)
            duration: Movement time in seconds
        """
        if self._check_approval(f"move mouse relative ({x_offset}, {y_offset})"):
            pyautogui.move(x_offset, y_offset, duration=duration)
            logger.debug(f"Moved mouse relative ({x_offset}, {y_offset})")
    
    def click(self, x: Optional[int] = None, y: Optional[int] = None, 
              button: str = 'left', clicks: int = 1, interval: float = 0.1) -> None:
        """
        Perform mouse click.
        
        Args:
            x, y: Coordinates to click (None = current position)
            button: 'left', 'right', 'middle'
            clicks: Number of clicks (1 = single, 2 = double, etc.)
            interval: Delay between multiple clicks
        """
        position_str = f"at ({x}, {y})" if x is not None else "at current position"
        if self._check_approval(f"{button} click {position_str}"):
            pyautogui.click(x=x, y=y, clicks=clicks, interval=interval, button=button)
            logger.info(f"{button.capitalize()} click {position_str} (x{clicks})")
    
    def double_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Convenience method for double-click."""
        self.click(x, y, clicks=2)
    
    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Convenience method for right-click."""
        self.click(x, y, button='right')
    
    def middle_click(self, x: Optional[int] = None, y: Optional[int] = None) -> None:
        """Convenience method for middle-click."""
        self.click(x, y, button='middle')
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int,
             duration: float = 0.5, button: str = 'left') -> None:
        """
        Drag and drop operation.
        
        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates
            duration: Drag duration in seconds
            button: Mouse button to use ('left', 'right', 'middle')
        """
        if self._check_approval(f"drag from ({start_x}, {start_y}) to ({end_x}, {end_y})"):
            pyautogui.moveTo(start_x, start_y)
            time.sleep(0.05)
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, button=button)
            logger.info(f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})")
    
    def scroll(self, clicks: int, direction: str = 'vertical', 
               x: Optional[int] = None, y: Optional[int] = None) -> None:
        """
        Scroll mouse wheel.
        
        Args:
            clicks: Scroll amount (+ = up/left, - = down/right)
            direction: 'vertical' or 'horizontal'
            x, y: Position to scroll at (None = current position)
        """
        if x is not None and y is not None:
            pyautogui.moveTo(x, y)
        
        if direction == 'vertical':
            pyautogui.scroll(clicks)
        else:
            pyautogui.hscroll(clicks)
        logger.debug(f"Scrolled {direction} {clicks} clicks")
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse coordinates.
        
        Returns:
            (x, y) tuple
        """
        pos = pyautogui.position()
        return (pos.x, pos.y)
    
    # ========== KEYBOARD OPERATIONS ==========
    
    def type_text(self, text: str, interval: float = 0, wpm: Optional[int] = None) -> None:
        """
        Type text with configurable speed.
        
        Args:
            text: Text to type
            interval: Delay between keystrokes (0 = instant)
            wpm: Words per minute (overrides interval)
        """
        if wpm is not None:
            chars_per_second = (wpm * 5) / 60
            interval = 1.0 / chars_per_second
        
        if self._check_approval(f"type text: '{text[:50]}...'"):
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: '{text[:50]}{'...' if len(text) > 50 else ''}' (interval={interval:.3f}s)")
    
    def press(self, key: str, presses: int = 1, interval: float = 0.1) -> None:
        """
        Press and release a key.
        
        Args:
            key: Key name (e.g., 'enter', 'space', 'a', 'f1')
            presses: Number of times to press
            interval: Delay between presses
        """
        if self._check_approval(f"press '{key}' {presses}x"):
            pyautogui.press(key, presses=presses, interval=interval)
            logger.info(f"Pressed '{key}' {presses}x")
    
    def hotkey(self, *keys, interval: float = 0.05) -> None:
        """
        Execute keyboard shortcut (e.g., Ctrl+C, Alt+Tab).
        
        Args:
            *keys: Keys to press together (e.g., 'ctrl', 'c')
            interval: Delay between key presses
        """
        keys_str = '+'.join(keys)
        if self._check_approval(f"hotkey: {keys_str}"):
            pyautogui.hotkey(*keys, interval=interval)
            logger.info(f"Executed hotkey: {keys_str}")
    
    def key_down(self, key: str) -> None:
        """Press and hold a key without releasing."""
        pyautogui.keyDown(key)
        logger.debug(f"Key down: '{key}'")
    
    def key_up(self, key: str) -> None:
        """Release a held key."""
        pyautogui.keyUp(key)
        logger.debug(f"Key up: '{key}'")
    
    # ========== SCREEN OPERATIONS ==========
    
    def screenshot(self, region: Optional[Tuple[int, int, int, int]] = None,
                   filename: Optional[str] = None):
        """
        Capture screen or region.
        
        Args:
            region: (left, top, width, height) for partial capture
            filename: Path to save image (None = return PIL Image)
        
        Returns:
            PIL Image object (if filename is None)
        """
        img = pyautogui.screenshot(region=region)
        
        if filename:
            img.save(filename)
            logger.info(f"Screenshot saved to: {filename}")
        else:
            logger.debug(f"Screenshot captured (region={region})")
            return img
    
    def get_pixel_color(self, x: int, y: int) -> Tuple[int, int, int]:
        """Get RGB color of pixel at coordinates."""
        color = pyautogui.pixel(x, y)
        return color
    
    def find_on_screen(self, image_path: str, confidence: float = 0.8,
                       region: Optional[Tuple[int, int, int, int]] = None):
        """
        Find image on screen using template matching.
        Requires OpenCV (opencv-python).
        
        Args:
            image_path: Path to template image
            confidence: Match threshold 0-1 (0.8 = 80% match)
            region: Search region (left, top, width, height)
        
        Returns:
            (x, y, width, height) of match, or None if not found
        """
        try:
            location = pyautogui.locateOnScreen(image_path, confidence=confidence, region=region)
            if location:
                logger.info(f"Found '{image_path}' at {location}")
                return location
            else:
                logger.debug(f"'{image_path}' not found on screen")
                return None
        except Exception as e:
            logger.error(f"Error finding image: {e}")
            return None
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen resolution."""
        return (self.screen_width, self.screen_height)
    
    # ========== WINDOW OPERATIONS ==========
    
    def get_all_windows(self) -> List[str]:
        """Get list of all open window titles."""
        try:
            import pygetwindow as gw
            windows = gw.getAllTitles()
            windows = [w for w in windows if w.strip()]
            return windows
        except ImportError:
            logger.error("pygetwindow not installed. Run: pip install pygetwindow")
            return []
        except Exception as e:
            logger.error(f"Error getting windows: {e}")
            return []
    
    def activate_window(self, title_substring: str) -> bool:
        """Bring window to front by title (partial match)."""
        try:
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle(title_substring)
            if windows:
                windows[0].activate()
                logger.info(f"Activated window: '{windows[0].title}'")
                return True
            else:
                logger.warning(f"No window found with title containing: '{title_substring}'")
                return False
        except ImportError:
            logger.error("pygetwindow not installed")
            return False
        except Exception as e:
            logger.error(f"Error activating window: {e}")
            return False

    # ---------- High‑level helper ----------
    def open_url_in_app(self, app_name: str, url: str, new_tab: bool = True, timeout: float = 5.0) -> bool:
        """Robustly open a URL in the specified application.
        
        Steps:
        1. Activate the app window; if not found, launch via Run dialog.
        2. Wait until the window becomes the active window (polling up to *timeout* seconds).
        3. If *new_tab* is True, send ``Ctrl+T``; otherwise ensure the address bar is focused.
        4. Focus address bar (Ctrl+L), type the URL, and press Enter.
        5. Return True on success, False on failure.
        """
        # 1. Try to bring the app to front; if it fails, launch via Run dialog.
        if not self.activate_window(app_name):
            logger.info(f"Launching {app_name} via Run dialog")
            self.hotkey('win')
            time.sleep(0.5)
            self.type_text(app_name)
            self.press('enter')
            time.sleep(2)  # give the app time to start
        # 2. Wait for the app to become the active window
        start = time.time()
        while time.time() - start < timeout:
            active = self.get_active_window() or ''
            if app_name.lower() in active.lower():
                break
            time.sleep(0.3)
        else:
            logger.error(f"{app_name} did not become active within {timeout}s")
            return False
        # 3. Open a new tab if requested
        if new_tab:
            self.hotkey('ctrl', 't')
            time.sleep(0.5)
        # 4. Focus address bar and navigate
        self.hotkey('ctrl', 'l')
        time.sleep(0.2)
        self.type_text(url)
        self.press('enter')
        logger.info(f"Opened URL '{url}' in {app_name}")
        return True

    # ---------- High‑level auto‑open helper ----------
    def open_url(self, url: str, new_tab: bool = True, timeout: float = 5.0) -> bool:
        """Open a URL using the preferred browser.
        
        Preference order:
        1. **Comet** – primary browser as per user instruction.
        2. **Chrome** – fallback if Comet cannot be activated.
        
        The method will attempt to open the URL in Comet first and, on failure,
        automatically fallback to Chrome, without requiring any extra steps from
        the caller.
        """
        # Try Comet first
        if self.open_url_in_app('Comet', url, new_tab=new_tab, timeout=timeout):
            return True
        # Fallback to Chrome if Comet failed
        logger.warning('Falling back to Chrome for URL opening')
        return self.open_url_in_app('Chrome', url, new_tab=new_tab, timeout=timeout)
    
    def get_active_window(self) -> Optional[str]:
        """Get title of currently focused window."""
        try:
            import pygetwindow as gw
            active = gw.getActiveWindow()
            return active.title if active else None
        except ImportError:
            logger.error("pygetwindow not installed")
            return None
        except Exception as e:
            logger.error(f"Error getting active window: {e}")
            return None
    
    # ========== CLIPBOARD OPERATIONS ==========
    
    def copy_to_clipboard(self, text: str) -> None:
        """Copy text to clipboard."""
        try:
            import pyperclip
            pyperclip.copy(text)
            logger.info(f"Copied to clipboard: '{text[:50]}...'")
        except ImportError:
            logger.error("pyperclip not installed. Run: pip install pyperclip")
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
    
    def get_from_clipboard(self) -> Optional[str]:
        """Get text from clipboard."""
        try:
            import pyperclip
            text = pyperclip.paste()
            logger.debug(f"Got from clipboard: '{text[:50]}...'")
            return text
        except ImportError:
            logger.error("pyperclip not installed. Run: pip install pyperclip")
            return None
        except Exception as e:
            logger.error(f"Error getting clipboard: {e}")
            return None
    
    # ========== UTILITY METHODS ==========
    
    def pause(self, seconds: float) -> None:
        """Pause automation for specified duration."""
        logger.info(f"Pausing for {seconds}s...")
        time.sleep(seconds)
    
    def is_safe(self) -> bool:
        """Check if it's safe to continue automation (failsafe not triggered)."""
        if not self.failsafe:
            return True
        x, y = self.get_mouse_position()
        corner_tolerance = 5
        corners = [
            (0, 0),
            (self.screen_width - 1, 0),
            (0, self.screen_height - 1),
            (self.screen_width - 1, self.screen_height - 1)
        ]
        for cx, cy in corners:
            if abs(x - cx) <= corner_tolerance and abs(y - cy) <= corner_tolerance:
                logger.warning(f"Mouse in corner ({x}, {y}) - FAILSAFE TRIGGERED")
                return False
        return True
    
    def _check_approval(self, action: str) -> bool:
        """If approval mode is on, ask the user via stdin. Returns True if approved."""
        if not self.require_approval:
            return True
        response = input(f"Allow: {action}? [y/n]: ").strip().lower()
        approved = response in ['y', 'yes']
        if not approved:
            logger.warning(f"Action declined: {action}")
        return approved
    
    # ========== QUICK ACCESS FUNCTIONS ==========
    
    def alert(self, text: str = '', title: str = 'Alert', button: str = 'OK') -> None:
        pyautogui.alert(text=text, title=title, button=button)
    
    def confirm(self, text: str = '', title: str = 'Confirm', buttons: List[str] = None) -> str:
        if buttons is None:
            buttons = ['OK', 'Cancel']
        return pyautogui.confirm(text=text, title=title, buttons=buttons)
    
    def prompt(self, text: str = '', title: str = 'Input', default: str = '') -> Optional[str]:
        return pyautogui.prompt(text=text, title=title, default=default)

