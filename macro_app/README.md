# 2D UI Macro

This is a lightweight macro-style desktop program that recognizes UI images on screen, moves the cursor, and clicks based on toggleable tasks. It is designed to be a configurable template that you can adapt to a 2D UI-based game.

## Features

- Toggleable tasks (checkboxes) similar to macro tools.
- Image-based button recognition using template matching.
- Sequential action steps (click image, wait, press key).

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Place cropped button images in the `assets/` folder.
3. Update `config.json` with the steps for each task.
4. Run the app:

```bash
python src/main.py
```

## Config format

Each task contains a list of steps. Supported actions:

- `click_image`: click on a matching image.
- `wait`: pause for a number of seconds.
- `press_key`: send a key press.

Example:

```json
{
  "name": "Auto Battle",
  "steps": [
    { "action": "click_image", "image": "battle_button.png", "timeout_seconds": 10, "confidence": 0.8 },
    { "action": "wait", "seconds": 2 }
  ]
}
```

## Notes

- For best results, use consistent game resolution and UI scale.
- Template matching is sensitive to color and scaling. Use crisp, tight crops.
- This tool requires the game window to be visible on screen.
