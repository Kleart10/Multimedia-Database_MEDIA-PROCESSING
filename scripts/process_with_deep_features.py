"""
Process media using deep features (MobileNetV2) when available.

This script will attempt to import PyTorch and run deep feature extraction for
specified media IDs. It falls back and reports detailed errors if imports fail
so you can apply package fixes manually.

Usage:
    venv\Scripts\python.exe scripts\process_with_deep_features.py [media_id]

If no media_id is provided, it will process all media with is_processed == True
but missing deep features fields.
"""
import sys
from pathlib import Path
import os
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models import Media, ImageFeatures


def process_media_deep(app, media_id):
    from app.extractors.image_extractor import ImageFeatureExtractor

    with app.app_context():
        media = Media.query.get(media_id)
        if not media:
            print(f"Media id={media_id} not found")
            return

        if media.media_type != 'image':
            print(f"Media id={media_id} is not an image, skipping deep feature extraction")
            return

        # Try loading model
        try:
            extractor = ImageFeatureExtractor(use_deep_features=True, force_cpu=True)
        except Exception as e:
            print('Failed to initialize ImageFeatureExtractor with deep features:')
            traceback.print_exc()
            return

        # Resolve file path
        file_path = media.file_path
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(os.path.join(app.root_path, '..', file_path))

        if not os.path.exists(file_path):
            # fallback: use first thumbnail if available
            if media.thumbnails:
                thumb = media.thumbnails[0].thumbnail_path
                if not os.path.isabs(thumb):
                    thumb = os.path.abspath(os.path.join(app.root_path, '..', thumb))
                if os.path.exists(thumb):
                    print(f'Original file missing, using thumbnail for deep features: {thumb}')
                    file_path = thumb
                else:
                    print(f'File not found: {file_path}')
                    return
            else:
                print(f'File not found: {file_path}')
                return

        try:
            features = extractor.extract_all_features(file_path)
        except Exception as e:
            print('Error during deep feature extraction:')
            traceback.print_exc()
            return

        # Update existing ImageFeatures record or create if missing
        imgf = ImageFeatures.query.filter_by(media_id=media.id).first()
        if not imgf:
            imgf = ImageFeatures(media_id=media.id)
            db.session.add(imgf)

        imgf.deep_features = features.get('deep_features').tolist() if features.get('deep_features') is not None else None
        imgf.combined_features = features.get('combined_features').tolist() if features.get('combined_features') is not None else None
        db.session.commit()
        print(f'Deep features stored for media id={media.id}')


def main():
    app = create_app()

    # Determine media ids to process
    media_ids = []
    if len(sys.argv) > 1:
        try:
            media_ids = [int(sys.argv[1])]
        except ValueError:
            print('Invalid media id')
            return
    else:
        with app.app_context():
            # Find image media where image_features.deep_features is NULL
            q = db.session.query(Media.id).join(ImageFeatures, isouter=True).filter(Media.media_type=='image')
            # We'll process all images (could refine to ones missing deep_features)
            media_ids = [r[0] for r in q.all()]

    for mid in media_ids:
        print('Processing deep features for media id=', mid)
        process_media_deep(app, mid)


if __name__ == '__main__':
    main()
