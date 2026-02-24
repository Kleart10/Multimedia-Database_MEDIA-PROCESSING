"""
Process pending media without loading heavy deep-learning libraries.

This script safely processes `Media` records with `is_processed == False` by
using extractors with deep features disabled. It generates thumbnails and
stores basic features as JSON arrays to avoid PyTorch/NumPy compatibility issues
on Windows.

Run with:

    venv\Scripts\python.exe scripts\process_pending_media.py

"""
import sys
from pathlib import Path
import os
import time
import traceback

# Ensure project root is on sys.path when script is run directly
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models import Media, ImageFeatures, AudioFeatures, VideoFeatures, Thumbnail
from app.extractors import ImageExtractor, AudioExtractor, VideoExtractor


def resolve_path(app, path_str):
    if os.path.isabs(path_str):
        return path_str
    p = os.path.join(app.root_path, '..', path_str)
    return os.path.abspath(p)


def main():
    app = create_app()
    with app.app_context():
        pending = Media.query.filter_by(is_processed=False).all()
        print(f"Found {len(pending)} pending media items")

        for media in pending:
            print(f"Processing media id={media.id} filename={media.filename} type={media.media_type}")

            try:
                file_path = resolve_path(app, media.file_path)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")

                # IMAGE
                if media.media_type == 'image':
                    extractor = ImageExtractor(use_deep_features=False)
                    features = extractor.extract_all_features(file_path)

                    try:
                        meta = extractor.get_image_metadata(file_path)
                        media.width = meta.get('width')
                        media.height = meta.get('height')
                    except Exception:
                        pass

                    imgf = ImageFeatures(
                        media_id=media.id,
                        color_histogram=features.get('color_histogram').tolist() if features.get('color_histogram') is not None else None,
                        texture_lbp=features.get('texture_lbp').tolist() if features.get('texture_lbp') is not None else None,
                        deep_features=None,
                        combined_features=features.get('combined_features').tolist() if features.get('combined_features') is not None else None
                    )
                    db.session.add(imgf)

                    # Generate thumbnail
                    try:
                        thumb_name = f"thumb_{media.filename.rsplit('.',1)[0]}.jpg"
                        thumb_out = os.path.join(app.config['THUMBNAIL_FOLDER'], thumb_name)
                        os.makedirs(os.path.dirname(thumb_out), exist_ok=True)
                        thumb_path = extractor.generate_thumbnail(file_path, thumb_out, (app.config.get('THUMBNAIL_SIZE',256), app.config.get('THUMBNAIL_SIZE',256)))
                        if thumb_path:
                            t = Thumbnail(media_id=media.id, thumbnail_path=str(thumb_path), thumbnail_type='default', width=app.config.get('THUMBNAIL_SIZE',256), height=app.config.get('THUMBNAIL_SIZE',256))
                            db.session.add(t)
                    except Exception as e:
                        print('Thumbnail generation warning:', e)

                # AUDIO
                elif media.media_type == 'audio':
                    extractor = AudioExtractor()
                    features = extractor.extract_all_features(file_path)
                    try:
                        meta = extractor.get_audio_metadata(file_path)
                        media.duration = meta.get('duration')
                    except Exception:
                        pass

                    audf = AudioFeatures(
                        media_id=media.id,
                        mfcc_features=features.get('mfcc_features').tolist() if features.get('mfcc_features') is not None else None,
                        spectral_features=features.get('spectral_features').tolist() if features.get('spectral_features') is not None else None,
                        waveform_stats=features.get('waveform_stats').tolist() if features.get('waveform_stats') is not None else None,
                        combined_features=features.get('combined_features').tolist() if features.get('combined_features') is not None else None
                    )
                    db.session.add(audf)

                # VIDEO
                elif media.media_type == 'video':
                    extractor = VideoExtractor(use_deep_features=False)
                    features = extractor.extract_all_features(file_path)
                    try:
                        meta = extractor.get_video_metadata(file_path)
                        media.duration = meta.get('duration')
                        media.width = meta.get('width')
                        media.height = meta.get('height')
                    except Exception:
                        pass

                    vidf = VideoFeatures(
                        media_id=media.id,
                        keyframe_features=features.get('keyframe_features').tolist() if features.get('keyframe_features') is not None else None,
                        motion_features=features.get('motion_features').tolist() if features.get('motion_features') is not None else None,
                        scene_stats=features.get('scene_stats').tolist() if features.get('scene_stats') is not None else None,
                        combined_features=features.get('combined_features').tolist() if features.get('combined_features') is not None else None,
                        keyframe_timestamps=features.get('keyframe_timestamps')
                    )
                    db.session.add(vidf)

                media.is_processed = True
                db.session.commit()
                print(f"Processed media id={media.id}")

            except Exception as e:
                db.session.rollback()
                media.processing_error = str(e)
                try:
                    db.session.commit()
                except Exception:
                    pass
                print(f"Failed to process media id={media.id}: {e}")
                traceback.print_exc()

            time.sleep(0.5)


if __name__ == '__main__':
    main()
