Pig Portal - QA Smoke Checklist

Prereqs
- Start system: `docker compose --env-file .env -f infrastructure/docker-compose.yml up --build -d`
- Open `http://localhost` → portal loads

Steps
1) Login as Owner
- Go to `/login`, enter `owner@farm.test` / `Passw0rd!` → redirected to Dashboard

2) Add a pig
- Go to Pigs → Add Pig → ear_tag `SMOKE-1` → Save → appears in list

3) Add a weight
- Open `SMOKE-1` → Weights tab → add today’s weight → row appears; chart updates

4) Record a service
- From Pigs pick a sow or create one → Record Service with a boar → expected farrow auto-fills (+114d)

5) Record a litter and set wean date
- Go to Litters → create with farrow_date, counts → later PATCH wean_date → accepted

6) Add a treatment
- On pig Health tab, add a health event → visible in list

7) Upload a photo
- Pig Files tab → upload small image → thumbnail shows

8) Create a task
- Tasks → create “Weigh SMOKE-1” due today → appears in Tasks and Dashboard; mark done

9) Run ADG report
- Reports → ADG for `SMOKE-1` between two dates → shows values & chart

10) Export pigs CSV
- Pigs → Export CSV → file downloads with headers

11) Role UX
- Logout → login as `worker@farm.test` / `Passw0rd!` → Settings page hidden/forbidden; can add weight on a pig

