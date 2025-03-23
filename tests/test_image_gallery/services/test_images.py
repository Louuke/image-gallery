import hashlib
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest

from image_gallery.services.images import ImageService


class TestImageService:

    @pytest.fixture()
    def service(self, app) -> ImageService:
        return ImageService(app.config)

    def test_get_image_paths_newest_first(self, service: ImageService):
        image_paths = service.get_image_paths(-1)
        assert sorted(image_paths, key=lambda p: p.stat().st_ctime, reverse=True) == image_paths

        image_paths_min = service.get_image_paths(-1, min_items=100)
        assert 100 == len(image_paths_min)
        assert (image_paths * (100 // len(image_paths) + 1))[:100] == image_paths_min

    def test_get_image_paths_oldest_first(self, service: ImageService):
        image_paths = service.get_image_paths(1)
        assert sorted(image_paths, key=lambda p: p.stat().st_ctime) == image_paths

        image_paths_min = service.get_image_paths(1, min_items=100)
        assert 100 == len(image_paths_min)
        assert (image_paths * (100 // len(image_paths) + 1))[:100] == image_paths_min

    def test_get_image_paths_random(self, service: ImageService):
        image_paths = service.get_image_paths(0)
        for _ in range(10):
            if sorted(image_paths) != image_paths:
                assert True
                break

    def test_create_image_archive(self, service: ImageService):
        image_paths = [path for path in Path(service.gallery_directory).glob('*.*')]
        filenames = [path.name for path in image_paths]
        archive, mimetype = service.create_image_archive(filenames)
        assert mimetype == 'application/zip'
        with ZipFile(BytesIO(archive)) as zf:
            for path in image_paths:
                with zf.open(path.name) as f:
                    assert calculate_sha256(read_file(path)) == calculate_sha256(f.read())

    def test_read_image(self, service: ImageService):
        image_paths = [path for path in Path(service.gallery_directory).glob('*.*')]
        for path in image_paths:
            sha256 = calculate_sha256(read_file(path))
            data, mimetype = service.read_image(path.name)
            assert sha256 == calculate_sha256(data)
            assert mimetype is not None
            assert mimetype in ['image/jpeg', 'image/png', 'image/jpg']

    def test_paginate_image_paths(self):
        paths = [Path(f'path_{i}.jpg') for i in range(100)]
        page = 3
        items = 10
        paginated = ImageService.paginate_image_paths(paths, page, items)
        assert paginated == paths[20:30]

        page = 1
        items = 20
        paginated = ImageService.paginate_image_paths(paths, page, items)
        assert paginated == paths[:20]


def calculate_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_file(path: Path) -> bytes:
    with open(path, 'rb') as f:
        return f.read()
