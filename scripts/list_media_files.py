from app import create_app
from app.models import Media
import os

app = create_app()
with app.app_context():
    media_list = Media.query.order_by(Media.id).all()
    if not media_list:
        print('No media records found')
    for m in media_list:
        p = m.file_path or ''
        p_abs = p if os.path.isabs(p) else os.path.join(app.root_path, p)
        exists = os.path.exists(p_abs)
        print(f"{m.id}\t{m.media_type}\t{p}\t{'EXISTS' if exists else 'MISSING'}\t{p_abs}")
        if m.thumbnail_url:
            th = m.thumbnail_url
            th_abs = th if os.path.isabs(th) else os.path.join(app.root_path, th)
            print(f"  thumbnail:\t{th}\t{'EXISTS' if os.path.exists(th_abs) else 'MISSING'}\t{th_abs}")
