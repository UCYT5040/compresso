import pytest
from pathlib import Path
from compresso import compress, decompress

@pytest.fixture
def assets_path() -> Path:
    """Fixture to provide the path to the assets directory."""
    return Path(__file__).parent / "assets"

def test_compress_decompress_all_assets(assets_path, tmp_path):
    """Test compressing and decompressing all files in the assets directory."""
    for asset in assets_path.iterdir():
        if asset.is_file():
            compressed_file = tmp_path / (asset.name + ".compressed")
            decompressed_file = tmp_path / (asset.name + ".decompressed")

            compress(asset, output=compressed_file, worker_timeout=15, max_rounds=3)
            decompress(compressed_file, output=decompressed_file)

            # Compare original and decompressed files
            with open(asset, "rb") as f1, open(decompressed_file, "rb") as f2:
                assert f1.read() == f2.read(), f"Mismatch for {asset.name}"
