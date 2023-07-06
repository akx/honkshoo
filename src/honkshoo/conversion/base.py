import tqdm

from honkshoo.excs import EDFReadError


class Converter:
    def finalize(self):
        pass

    def read_edf(self, edf_path: str):
        raise NotImplementedError

    def read_edfs(self, edfs):
        with tqdm.tqdm(edfs) as pbar:
            for edf_path in pbar:
                pbar.set_description(f"Reading {edf_path}")
                try:
                    self.read_edf(edf_path)
                except EDFReadError as e:
                    pbar.write(f"Error reading {edf_path}: {e}")
        self.finalize()
