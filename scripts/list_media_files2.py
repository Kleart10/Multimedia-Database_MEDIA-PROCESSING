from app import create_app
from app.models import Media
import os

project_root = os.getcwd()
app = create_app()
with app.app_context():
    media_list = Media.query.order_by(Media.id).all()
    if not media_list:
        print('No media records found')
    for m in media_list:
        p = m.file_path or ''
        p_abs = p if os.path.isabs(p) else os.path.join(project_root, p)
        exists = os.path.exists(p_abs)
        print(f"{m.id}\t{m.media_type}\t{p}\t{'EXISTS' if exists else 'MISSING'}\t{p_abs}")
        for t in m.thumbnails:
            th = t.thumbnail_path or ''
            th_abs = th if os.path.isabs(th) else os.path.join(project_root, th)
            print(f"  thumbnail:\t{th}\t{'EXISTS' if os.path.exists(th_abs) else 'MISSING'}\t{th_abs}")
