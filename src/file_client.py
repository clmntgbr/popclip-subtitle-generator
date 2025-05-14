import os


class FileClient:
    @staticmethod
    def delete_file(file_path: str) -> bool:
        try:
            os.remove(file_path)
            print(f"file successfully deleted: {file_path}")
            return True
        except Exception as e:
            print(f"error deleting file: {e}")
            return False
