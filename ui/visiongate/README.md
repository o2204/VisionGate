# VisionGate Flutter App

Cyberpunk-themed AI Smart Access Control dashboard for Flutter.

## Screens Implemented
- **Command Center** — live stats, neural activity bars, quick actions, hardware status
- **Face Recognition** — animated scan viewport with oval, corner brackets, scan line, match score
- **Hardware** — animated radar sweep, device grid, gate controls, WiFi/BLE status

## Setup

### 1. Download Google Fonts
Download and place these font files under `assets/fonts/`:

**Orbitron** (headers): https://fonts.google.com/specimen/Orbitron
- `Orbitron-Regular.ttf`
- `Orbitron-Bold.ttf`

**Rajdhani** (body): https://fonts.google.com/specimen/Rajdhani
- `Rajdhani-Regular.ttf`
- `Rajdhani-Medium.ttf`
- `Rajdhani-SemiBold.ttf`
- `Rajdhani-Bold.ttf`

Create the folder:
```
mkdir -p assets/fonts
```

### 2. Fix main.dart import
In `lib/main.dart`, change:
```dart
import 'screens/command_center_screen.dart';
```
to import `main_shell.dart`:
```dart
import 'screens/main_shell.dart';
```
And use `MainShell` as `home:`.

### 3. Run
```
flutter pub get
flutter run
```

## File Structure
```
lib/
  main.dart
  theme/
    app_theme.dart
  screens/
    main_shell.dart          ← sidebar navigation
    command_center_screen.dart
    face_recognition_screen.dart
    hardware_screen.dart
  widgets/
    cyber_card.dart
    glow_button.dart
assets/
  fonts/
    (place font files here)
pubspec.yaml
```

## Color Palette
| Token | Hex | Use |
|---|---|---|
| background | #0D0618 | App background |
| surface | #160D2A | Sidebar |
| card | #1A1030 | Cards |
| neonPink | #FF2D9B | Primary accent |
| neonPurple | #B026FF | Secondary accent |
| neonCyan | #00F5FF | Highlights |
| neonBlue | #2979FF | Gradients |
