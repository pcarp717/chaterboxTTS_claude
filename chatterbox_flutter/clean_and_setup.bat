@echo off
echo Cleaning Flutter project...
flutter clean
echo.
echo Getting Flutter packages...
flutter pub get
echo.
echo Enabling Windows desktop...
flutter config --enable-windows-desktop
echo.
echo Setup complete! Try running: flutter run -d windows
pause