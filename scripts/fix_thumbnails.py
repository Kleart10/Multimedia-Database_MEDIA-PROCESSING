"""
Scan the uploads/thumbnails folder and ensure Thumbnail DB records exist
for the corresponding Media entries. This helps recover thumbnails created
on disk but not recorded in the database.

Run with:
    venv\Scripts\python.exe scripts\fix_thumbnails.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models import Media, Thumbnail


def main():
    app = create_app()
    with app.app_context():
        thumb_dir = Path(app.config['THUMBNAIL_FOLDER'])
        print('Thumbnail directory:', thumb_dir)

        if not thumb_dir.exists():
            print('Thumbnail directory does not exist; nothing to do')
            return

        for thumb in thumb_dir.iterdir():
            if not thumb.is_file():
                continue

            name = thumb.name
            # Expecting filenames like: thumb_<media_basename>.jpg or video_<id>_frame_N.jpg
            if name.startswith('thumb_'):
                base = name[len('thumb_'):].rsplit('.', 1)[0]
                # Find media where filename starts with base
                media = Media.query.filter(Media.filename.startswith(base)).first()
                if not media:
                    print(f'No media match for thumbnail {name} (base={base})')
                    continue

                # Check if thumbnail record exists
                exists = Thumbnail.query.filter_by(media_id=media.id, thumbnail_path=str(thumb)).first()
                if exists:
                    print(f'Thumbnail record already exists for media id={media.id}')
                    continue

                # Create relative path (store as app expects)
                rel_path = str(Path(app.config['THUMBNAIL_FOLDER']) / name)

                t = Thumbnail(
                    media_id=media.id,
                    thumbnail_path=rel_path,
                    thumbnail_type='default',
                    width=app.config.get('THUMBNAIL_SIZE'),
                    height=app.config.get('THUMBNAIL_SIZE')
                )
                db.session.add(t)
                media.is_processed = True
                db.session.commit()
                print(f'Inserted thumbnail for media id={media.id} -> {rel_path}')

        print('Done')


if __name__ == '__main__':
    main()
