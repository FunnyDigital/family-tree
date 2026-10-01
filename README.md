# Family Tree

A self-hosted family tree website. Browse an interactive tree, open any person for their
photographs, biodata and written story, and sign in as an admin to add and edit everything.

Built with **FastAPI + SQLite** on the back end and **Vue 3 + Tailwind** on the front, packaged as
two Docker containers so it deploys to a TrueNAS server with a single command.

---

## What it does

- **Interactive family tree** — every generation laid out in rows with couples linked and children
  connected to their parents. Separate families are spaced apart, each couple's line runs at its own
  height so two families' lines never merge, and a person's line is drawn straight down from their
  own parents. Pan, drag and zoom; click any card to open that person.
- **"Down from here" view** — on any profile, a button opens a tree of that person and their partner
  with every descendant beneath them, so you can follow one branch without the rest of the family
  around it.
- **Backup & restore** — the admin dashboard can download the whole tree as one file, and restore
  from one. Handy for keeping a copy, or moving everything to another machine without touching the
  server's filesystem.
- **Person profiles** — a photo gallery with a lightbox, a biodata table (born, died, places,
  occupation) and every family relationship as a clickable chip.
- **Photographs** — upload an album per person; the site makes a thumbnail automatically and keeps
  the full-size original. One photo is marked *primary* and becomes their portrait everywhere.
- **Stories & write-ups** — a free-text biography plus any number of titled stories per person.
- **Directory** — search everyone by name, place or occupation, and filter to living or remembered.
- **Admin panel (login)** — add/edit/delete people, record marriages and partnerships (including
  several marriages for one person), upload photos and write stories.
- **Public viewing** — the tree and profiles can be seen by anyone with the link; only editing
  requires the admin login.

## How the tree handles real families

Each person stores a father and a mother, and marriages are separate records. That means a person
can have several marriages (a remarriage or a step-family) and children are attached to the correct
couple — children from a first marriage and children from a second sit under the right parents.

**You only enter a marriage once.** Two people recorded as the parents of the same child *are* a
couple — that is what a marriage is — so filling in a child's father and mother is enough. The
marriage then appears as a normal line on the tree and on both people's profiles, with their children
underneath it, without entering the same relationship a second time.

If you want to add a date or change the status (divorced, widowed, and so on), open the person in the
admin panel: the marriage is already listed there with an **Add details** button that turns it into a
full record. A person with two spouses is drawn *between* them, so both marriage lines touch them
rather than one reaching across the other spouse.

Marriage lines sit just below each row, and the children of a couple drop from the middle of that
line, so an offspring group always hangs under the right parents and no line is ever drawn across
someone else's card.

The order of each row is worked out by repeatedly pulling children under their parents and parents
over their children, so a couple is generally drawn directly above their own offspring. Distinct
families in the same row are separated by a wider gap, so two couples never read as one group of
four, and each family's connector runs at a slightly different height so lines from different
families don't sit on top of each other.

---

## Architecture

```
        ┌──────────────────────────────┐
        │  frontend  (nginx, port 80)   │
        │  serves the Vue app           │
        │  proxies /api and /media      │
        └───────────────┬──────────────┘
                        │
        ┌───────────────▼──────────────┐
        │  backend  (FastAPI, 8000)     │
        │  REST API + serves photos     │
        │  SQLite database + uploads    │
        └───────────────┬──────────────┘
                        │ bind mount
              /mnt/<pool>/family-tree/data/
                 ├─ family.db        (all people, unions, photos, stories)
                 └─ uploads/         (original photographs + thumbnails)
```

Only two containers — no separate database server. Everything lives in one SQLite file plus an
uploads folder, which makes backup and snapshots on TrueNAS trivial.

---

## Run it on your own computer (no Docker)

One command starts everything. The backend also serves the built interface, so it is a single
process on a single address: **http://localhost:8000**.

1. Install **Python 3.11+** (python.org — tick *Add python.exe to PATH*) and **Node 20+**
   (nodejs.org — use the LTS button).
2. Double-click **`start.cmd`** in the project folder, or run
   `powershell -ExecutionPolicy Bypass -File start.ps1`.

The first run creates a Python environment, installs the dependencies and builds the interface —
a few minutes, with progress shown. After that it starts in seconds and opens your browser
automatically.

- **Address:** <http://localhost:8000>
- **Admin login:** `admin` / `family123` — set `$env:ADMIN_PASSWORD` before starting to choose
  your own (it is only used the first time the database is created).
- **Demo family:** starts enabled so the tree isn't empty. Delete those people in the admin panel,
  or set `$env:SEED_DEMO_DATA = "false"` before the first run to begin empty.
- **Your data:** everything is in `backend/data/` — the SQLite database and uploaded photographs.
  Copy that folder to back up, paste it back to restore.
- **Stop it:** press Ctrl+C in the window.

> Want hot-reload while editing code? Use the two-process setup under *Local development* below.

---

## Install on TrueNAS SCALE 24.10+ (one click)

GitHub builds the two images for free, then you install them from the TrueNAS **Apps** screen — no
terminal, no compiling anything yourself.

### The images (already published)

The images are built and public, ready to pull:

- `ghcr.io/funnydigital/family-tree-backend:latest`
- `ghcr.io/funnydigital/family-tree-frontend:latest`

`.github/workflows/build-images.yml` rebuilds and republishes them on every push to `main`. Because
the repository is public the packages are public too, so TrueNAS pulls them with no login.

> If you ever move this into a **private** repo, the packages default to private. Either flip each one
> to public (your profile → **Packages** → package → **Package settings** → **Change visibility →
> Public**) or add a registry credential in TrueNAS using a token with the `read:packages` scope.

### One-time: a place for your data

Create a dataset so your family data is covered by snapshots — **Datasets → Add Dataset** (for
example pool `tank`, name `apps/family-tree`). Note its path, e.g. `/mnt/tank/apps/family-tree`.

### Install

1. In TrueNAS go to **Apps → Custom App → Install via YAML**.
2. Name it `family-tree`, paste the contents of `deploy/truenas-custom-app.yaml` — the image paths
   are already filled in — and change two things:
   - the data path → `/mnt/tank/apps/family-tree/data` (your dataset)
   - `SECRET_KEY`, `ADMIN_PASSWORD`, and `SITE_TITLE`
3. Click **Install**. TrueNAS pulls the images and starts both containers.
4. Open `http://<truenas-ip>:8080` and sign in at `/login`.

**Updating later:** push a change to GitHub; when the workflow finishes, open the app in TrueNAS and
press **Restart** — the `pull_policy: always` setting fetches the newest `latest`.

> Want a domain name or HTTPS? Point your existing reverse proxy at `http://<truenas-ip>:8080`.
> Nothing in the app needs changing.

---

## Alternative: build on the server over SSH

Prefer not to use GitHub? Copy the project to the NAS and build it there instead.

1. **Copy the project onto your server**, onto a dataset:

   ```bash
   scp -r family-tree admin@<truenas-ip>:/mnt/tank/apps/family-tree
   ssh admin@<truenas-ip>
   cd /mnt/tank/apps/family-tree
   ```

2. **Create your settings file and edit it:**

   ```bash
   cp .env.example .env
   nano .env
   ```

   Set `ADMIN_PASSWORD` and `SECRET_KEY`, and point `DATA_DIR` at a dataset:

   ```env
   FRONTEND_PORT=8080
   DATA_DIR=/mnt/tank/apps/family-tree/data
   SECRET_KEY=<paste a long random string>
   ADMIN_USERNAME=admin
   ADMIN_PASSWORD=<a strong password>
   SITE_TITLE=The <Your Name> Family
   SEED_DEMO_DATA=true
   ```

   > The host path must be absolute. Create the folder first:
   > `mkdir -p /mnt/tank/apps/family-tree/data`.

3. **Build and start it:**

   ```bash
   docker compose up -d --build
   docker compose logs -f          # watch the backend start and create the admin user
   ```

4. **Open the site:** `http://<truenas-ip>:8080`, sign in at `/login`, and start adding your family.
   (If you set `SEED_DEMO_DATA=true`, delete the example people once you're ready.)

To update later: `git pull`, then `docker compose up -d --build`.

---

## Local development

Run the two halves separately for a fast edit-reload loop.

**Backend** (Python 3.12, or 3.11):

```bash
cd backend
python -m venv .venv
```

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SEED_DEMO_DATA="true"; python -c "from app.seed import seed_database; seed_database()"
uvicorn app.main:app --reload --port 8000
```

```bash
# Linux / macOS
source .venv/bin/activate
pip install -r requirements.txt
SEED_DEMO_DATA=true python -c "from app.seed import seed_database; seed_database()"
uvicorn app.main:app --reload --port 8000
```

API docs are then at <http://localhost:8000/docs>.

**Frontend** (Node 20+):

```bash
cd frontend
npm install --include=dev       # --include=dev matters if NODE_ENV=production
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/api` and `/media` to the backend on port 8000.

---

## Configuration (`.env`)

| Variable | Default | Description |
|---|---|---|
| `FRONTEND_PORT` | `8080` | Host port the site is served on |
| `DATA_DIR` | `./data` | Host folder mounted to `/app/data` (SQLite file + uploads) |
| `SECRET_KEY` | — | Signs login tokens — set a long random value |
| `ADMIN_USERNAME` | `admin` | Initial admin user, created on first start |
| `ADMIN_PASSWORD` | `family123` | Initial admin password — change it |
| `SITE_TITLE` | `Our Family Tree` | Shown in the header, footer and browser tab |
| `SEED_DEMO_DATA` | `false` | Seed a small example family on first start |
| `MAX_UPLOAD_BYTES` | `26214400` | Maximum size for one uploaded photograph (25 MB) |

---

## Using the admin panel

1. **Add a person** — *Admin → People → Add a person*. Fill in names, dates (a full date like
   `1948-04-05` or just a year like `1948` are both fine), places, occupation and set the father
   and mother if they are already in the tree.
2. **Record a marriage** — open the person, *Marriages & partnerships → Add union*, pick the partner
   and choose a status (married, partnered, divorced, widowed, separated). Add a second union for a
   remarriage; children then attach to whichever couple they belong to.
3. **Upload photographs** — in the person's editor, drop images into the upload box. Use the star to
   choose the primary portrait and add captions underneath.
4. **Write their story** — the biography field holds the main write-up; *Add a story* creates extra
   titled pieces. Blank lines start a new paragraph; `**bold**`, `*italic*` and
   `[links](https://example.com)` are supported.

## Changing the admin password

`ADMIN_PASSWORD` is only used the first time the database is created — editing it later does nothing,
because the account already exists. To change the password of an account that already exists, use the
bundled tool:

```bash
cd backend
python -m app.set_password            # prompts, and picks the only account
python -m app.set_password admin      # or name the account explicitly
```

Inside the running container:

```bash
docker exec -it <backend-container> python -m app.set_password
```

It reads the password from the terminal (never from the command line, so it stays out of your shell
history), asks you to repeat it, and refuses to change anything if the two do not match.

### If you are locked out

Because `ADMIN_PASSWORD` is only read when the account is first created, a forgotten password (or a
first start where the placeholder in the YAML was never edited) leaves no way in. Set
`ADMIN_PASSWORD_RESET=true` alongside `ADMIN_PASSWORD` and restart the app — the password is applied
on the next start:

```yaml
- ADMIN_PASSWORD=<the password you want>
- ADMIN_PASSWORD_RESET=true
```

The startup log says which account it changed, which is useful if the username is not the one you
expected:

```
[seed] Reset the password for admin user 'admin' from ADMIN_PASSWORD
```

Once you are back in, **remove the `ADMIN_PASSWORD_RESET` line** and redeploy. While it is set, every
restart re-applies `ADMIN_PASSWORD`, which would silently undo any password you set another way. (If
the password already matches, it is a no-op — but removing it keeps things predictable.)

## Backups

The easiest way is the **Backup & restore** card on the admin dashboard: *Download backup* gives you
a single file containing everyone; *Choose a backup file* restores it. Restoring replaces the people,
marriages, photographs and stories, but leaves your admin login alone. You can use this to move a
tree between machines without any shell access.

Everything also lives under `DATA_DIR`:

- `family.db` — all people, marriages, photo records and stories.
- `uploads/` — the original photographs and their thumbnails.

Back up that folder (or snapshot the dataset) and you have a complete copy of the site. Restoring is
just putting the folder back and starting the containers.

---

## API reference (short)

Public (no login): `GET /api/tree`, `GET /api/persons`, `GET /api/persons/{id}`,
`GET /api/persons/{id}/photos`, `GET /media/*`.

Admin (Bearer token from `POST /api/auth/token`): `POST/PUT/DELETE /api/persons`,
`POST/PUT/DELETE /api/unions`, `POST /api/persons/{id}/photos` (multipart),
`PUT/DELETE /api/photos/{id}`, `PUT /api/photos/{id}/primary`, `POST/PUT/DELETE /api/stories`,
`GET /api/stats`.

Full interactive docs at `/docs`.

---

## Project structure

```
family-tree/
├── start.cmd / start.ps1       # run it locally, one command, no Docker
├── docker-compose.yml          # build locally (the SSH path)
├── .env.example
├── deploy/
│   └── truenas-custom-app.yaml # paste into TrueNAS → Apps → Custom App
├── .github/workflows/
│   └── build-images.yml        # builds + publishes both images to GHCR
├── backend/
│   ├── Dockerfile, entrypoint.sh, requirements.txt
│   └── app/
│       ├── main.py           # FastAPI app, mounts /media, registers routers
│       ├── config.py         # env config + data paths
│       ├── database.py       # SQLAlchemy engine (SQLite + WAL + foreign keys)
│       ├── models.py         # User, Person, Union, Photo, Story
│       ├── schemas.py        # request models
│       ├── auth.py, deps.py  # JWT login, password hashing, current-user dependency
│       ├── media.py          # photo save + Pillow thumbnails
│       ├── genealogy.py      # parent/child/spouse helpers, generation numbering
│       ├── serializers.py    # API response shapes
│       ├── seed.py           # admin user + optional demo family
│       └── routes/           # auth, persons, unions, photos, stories, tree, stats, meta
└── frontend/
    ├── Dockerfile, nginx.conf, vite.config.js, tailwind.config.js
    └── src/
        ├── router/           # public routes + guarded /admin
        ├── services/api.js   # fetch wrapper with the auth token
        ├── composables/      # useTreeLayout (tree engine), useAuth, useReveal, useSite
        ├── components/       # Icon, cards, gallery, lightbox, tree/, admin/
        └── views/            # Home, Tree, Person, Directory, Login, admin/*
```

## Notes

- Images are validated by content type and size, and thumbnails are generated with Pillow.
  Only raster formats are supported (JPG, PNG, WEBP, GIF); there is no SVG upload.
- Write-ups render as safe paragraphs with light formatting — no raw HTML — so content can't inject
  scripts.
- The tree is designed for the standard family shapes (couples, remarriages, step-families). It does
  not model adoptions or other GEDCOM-style edge cases.
