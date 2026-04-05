# PathMind Website Control (Simple)

## 1) Start website
Open PowerShell in project root and run:

```powershell
.\start_fullstack.ps1
```

This starts:
- Backend API: `http://localhost:8000`
- Frontend website: `http://localhost:3000/app.html`

## 2) Stop website
In PowerShell (project root), run:

```powershell
.\stop_fullstack.ps1
```

## 3) If signup/login shows "Failed to fetch" or backend connection error
It means backend is not running.

Start backend manually:

```powershell
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Then refresh website:
- `Ctrl + Shift + R`

## 4) Check health quickly
- Backend health: `http://localhost:8000/health`
- API docs: `http://localhost:8000/api/docs`
- Frontend: `http://localhost:3000/app.html`

## 5) Where to see your login ID
After login/signup:
- Toast message now shows your user ID.
- In dashboard -> `Profile`, you can see `User ID`.
