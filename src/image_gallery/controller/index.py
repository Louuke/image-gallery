from flask import Blueprint, render_template, request

from image_gallery.services.index import IndexService

index_bp = Blueprint('index', __name__)


@index_bp.get('/')
def index(service: IndexService):
    # Get query parameters
    sort = request.args.get('sort', -1, int)
    items = request.args.get('items', 20, int)
    page = request.args.get('page', 1, int)
    # Get the image paths and paginate them
    image_paths = service.get_image_paths(sort)
    images = service.paginate_images(image_paths, page, items)
    # Render the template
    template_vars = {
        'images': images,
        'header': service.gallery_header,
        'sort': sort,
        'items': items,
        'page': page,
        'total_pages': len(image_paths) // items + (len(image_paths) % items > 0)
    }
    return render_template('index.html', **template_vars)
