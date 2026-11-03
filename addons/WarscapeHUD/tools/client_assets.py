"""Read local MPQ assets, including encrypted listfiles, without modifying them."""
from pathlib import Path
from io import BytesIO
import bz2
import struct
import zlib
import mpyq


def read(archive, name):
    try:
        return archive.read_file(name)
    except NotImplementedError:
        pass
    entry = archive.get_hash_table_entry(name)
    if entry is None:
        return None
    block = archive.block_table[entry.block_table_index]
    archive.file.seek(block.offset + archive.header['offset'])
    data = archive.file.read(block.archived_size)
    key = archive._hash(name.rsplit('\\', 1)[-1], 'TABLE')
    if block.flags & 0x20000:
        key = ((key + block.offset) ^ block.size) & 0xffffffff

    def decrypt(value, sector_key):
        length = len(value) // 4 * 4
        return archive._decrypt(value[:length], sector_key & 0xffffffff) + value[length:]

    def unpack(value, expected):
        if not block.flags & 0x200 or len(value) >= expected:
            return value
        if value[0] == 2:
            return zlib.decompress(value[1:])
        if value[0] == 16:
            return bz2.decompress(value[1:])
        raise ValueError(f'Unsupported MPQ compression {value[0]}: {name}')

    if block.flags & 0x1000000:
        return unpack(decrypt(data, key), block.size)
    size = 512 << archive.header['sector_size_shift']
    count = (block.size + size - 1) // size
    table_count = count + 1 + bool(block.flags & 0x4000000)
    positions = struct.unpack(f'<{table_count}I', decrypt(data[:table_count * 4], key - 1))
    result = BytesIO()
    for i in range(count):
        chunk = decrypt(data[positions[i]:positions[i+1]], key + i)
        result.write(unpack(chunk, min(size, block.size - i * size)))
    return result.getvalue()


class ClientAssets:
    def __init__(self, game):
        def priority(path):
            # Prefer locale patches over base locale files; record every archive
            # in the catalogue rather than hiding alternate source instances.
            stem = path.stem.lower()
            patch = int(stem.rsplit('-', 1)[-1]) if stem.rsplit('-', 1)[-1].isdigit() else 1
            return ('patch' in stem, patch, path.parent.name.lower() == 'enus', stem)
        paths = sorted(Path(game).joinpath('Data').rglob('*.MPQ'), key=priority, reverse=True)
        self.archives = [(p, mpyq.MPQArchive(str(p), listfile=False)) for p in paths]

    def get(self, name):
        for path, archive in self.archives:
            data = read(archive, name)
            if data:
                return data, path.name
        raise FileNotFoundError(name)

    def names(self):
        found = {}
        for path, archive in self.archives:
            data = read(archive, '(listfile)')
            if data:
                for name in data.decode('utf-8', errors='replace').splitlines():
                    found.setdefault(name.lower(), [name, []])[1].append(path.name)
        return found
