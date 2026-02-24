from app import create_app, db
from app.models import Media, ImageFeatures

app = create_app()
with app.app_context():
    m = Media.query.get(1)
    if m:
        print(f'Media ID 1: {m.media_type} - is_processed: {m.is_processed}')
        if m.image_features:
            imgf = m.image_features
            deep_feat_present = imgf.deep_features is not None
            combined_feat_present = imgf.combined_features is not None
            print(f'  ImageFeatures: deep_features present: {deep_feat_present}, combined_features present: {combined_feat_present}')
            if deep_feat_present:
                print(f'    deep_features length: {len(imgf.deep_features)}')
            if combined_feat_present:
                print(f'    combined_features length: {len(imgf.combined_features)}')
        else:
            print('  No ImageFeatures record')
    else:
        print('Media ID 1 not found')
