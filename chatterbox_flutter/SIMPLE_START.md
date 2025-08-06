# Simple Manual Start

Let's troubleshoot step by step. Run these commands one at a time:

## Step 1: Check if Flutter works
```powershell
flutter doctor
```

## Step 2: Enable desktop support  
```powershell
flutter config --enable-windows-desktop
```

## Step 3: Get Flutter packages
```powershell
flutter pub get
```

## Step 4: Check if dependencies install
```powershell
pip install fastapi uvicorn pydantic
```

## Step 5: Start backend manually
```powershell
python python_backend/main.py
```
*Leave this running and open a new terminal*

## Step 6: In a new terminal, start Flutter
```powershell
cd chatterbox_flutter
flutter run -d windows
```

---

## Or try the new simple script:
```powershell
./start_flutter.ps1
```

This will show exactly where the problem is occurring!