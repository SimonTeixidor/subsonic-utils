# Subsonic Rating Sync

Syncs album ratings from a Subsonic server to FLAC files, and optionally deletes 1-star albums.

## Docker Usage

### Build

```bash
docker build -t subsonic-rating-sync .
```

### Run

Create a `.env` file with your Subsonic credentials:

```
SUBSONIC_HOST=https://your-subsonic-server.com
SUBSONIC_USER=your_username
SUBSONIC_PASSWORD=your_password
SUBSONIC_PORT=443
```

### Dry Run (Preview)

```bash
docker run --rm -i -v /path/to/your/music:/music --env-file .env subsonic-rating-sync --dry-run
```

This will print operations without executing them:
- `[DRY RUN] Would write ALBUMRATING=4 to /music/library/Artist/Album/01 song.flac`
- `[DRY RUN] Would delete: /music/library/Artist/1StarAlbum`

### Actual Run

```bash
docker run --rm -i -v /path/to/your/music:/music --env-file .env subsonic-rating-sync
```

This will:
- Write ALBUMRATING tags to FLAC files for albums with ratings > 1
- Delete album directories for albums with rating = 1

## Configuration

- Mount your music directory to `/music` inside the container
- The script expects Subsonic paths to be relative to a `/music` prefix (e.g., `/music/library/Artist/Album`)

## Legacy (Non-Docker)

Install dependencies and run directly:

```bash
pip install -r requirements.txt
SUBSONIC_HOST=... SUBSONIC_USER=... SUBSONIC_PASSWORD=... SUBSONIC_PORT=... python sync_and_cleanup.py [--dry-run]
```
