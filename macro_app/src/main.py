import json
import threading
import time
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox

import pyautogui

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


@dataclass
class Step:
    action: str
    image: str | None = None
    key: str | None = None
    seconds: float | None = None
    timeout_seconds: float | None = None
    confidence: float | None = None


@dataclass
class Task:
    name: str
    steps: list[Step]
    enabled: bool = False


class MacroRunner:
    def __init__(self, tasks: list[Task], status_callback):
        self.tasks = tasks
        self.status_callback = status_callback
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def _run_loop(self):
        self.status_callback("Macro running...")
        while not self._stop_event.is_set():
            for task in self.tasks:
                if not task.enabled:
                    continue
                self._run_task(task)
                if self._stop_event.is_set():
                    break
            time.sleep(0.2)
        self.status_callback("Macro stopped.")

    def _run_task(self, task: Task):
        self.status_callback(f"Running task: {task.name}")
        for step in task.steps:
            if self._stop_event.is_set():
                return
            if step.action == "wait":
                self._wait(step.seconds or 0)
            elif step.action == "press_key":
                if step.key:
                    pyautogui.press(step.key)
            elif step.action == "click_image":
                if step.image:
                    self._click_image(
                        step.image,
                        timeout_seconds=step.timeout_seconds or 5,
                        confidence=step.confidence or 0.8,
                    )
            else:
                self.status_callback(f"Unknown action: {step.action}")

    def _wait(self, seconds: float):
        end_time = time.time() + seconds
        while time.time() < end_time:
            if self._stop_event.is_set():
                return
            time.sleep(0.1)

    def _click_image(self, image_name: str, timeout_seconds: float, confidence: float):
        image_path = ASSETS_DIR / image_name
        if not image_path.exists():
            self.status_callback(f"Missing image: {image_path.name}")
            return
        end_time = time.time() + timeout_seconds
        while time.time() < end_time:
            if self._stop_event.is_set():
                return
            location = pyautogui.locateCenterOnScreen(
                str(image_path),
                confidence=confidence,
            )
            if location:
                pyautogui.moveTo(location.x, location.y, duration=0.2)
                pyautogui.click()
                return
            time.sleep(0.2)
        self.status_callback(f"Timed out waiting for {image_path.name}")


def load_tasks(path: Path) -> list[Task]:
    if not path.exists():
        messagebox.showerror(
            "Config Missing",
            f"Could not find config.json at {path}",
        )
        return []
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)
    tasks = []
    for task_data in raw.get("tasks", []):
        steps = [Step(**step) for step in task_data.get("steps", [])]
        tasks.append(Task(name=task_data.get("name", "Unnamed"), steps=steps))
    return tasks


class MacroApp(tk.Tk):
    def __init__(self, tasks: list[Task]):
        super().__init__()
        self.title("2D UI Macro")
        self.geometry("420x420")
        self.tasks = tasks
        self.runner = MacroRunner(tasks, self._set_status)
        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="Toggle tasks, then click Start").pack(pady=8)

        self.task_vars = []
        for task in self.tasks:
            var = tk.BooleanVar(value=task.enabled)
            checkbox = tk.Checkbutton(
                self,
                text=task.name,
                variable=var,
                command=self._sync_tasks,
            )
            checkbox.pack(anchor="w", padx=20)
            self.task_vars.append(var)

        control_frame = tk.Frame(self)
        control_frame.pack(pady=16)

        tk.Button(control_frame, text="Start", command=self._start).pack(
            side="left",
            padx=8,
        )
        tk.Button(control_frame, text="Stop", command=self._stop).pack(
            side="left",
            padx=8,
        )

        self.status_label = tk.Label(self, text="Macro stopped.")
        self.status_label.pack(pady=12)

        tk.Label(
            self,
            text="Press Stop before closing the app.",
            fg="#666666",
        ).pack(pady=4)

    def _sync_tasks(self):
        for task, var in zip(self.tasks, self.task_vars, strict=True):
            task.enabled = var.get()

    def _set_status(self, text: str):
        self.status_label.config(text=text)

    def _start(self):
        self._sync_tasks()
        if not any(task.enabled for task in self.tasks):
            messagebox.showinfo("No Tasks", "Enable at least one task first.")
            return
        self.runner.start()

    def _stop(self):
        self.runner.stop()


def main():
    tasks = load_tasks(CONFIG_PATH)
    if not tasks:
        return
    app = MacroApp(tasks)
    app.mainloop()


if __name__ == "__main__":
    main()
