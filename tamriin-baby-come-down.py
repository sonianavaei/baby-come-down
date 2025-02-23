class File:
    """
    Represents a file with a name, content, and optional password for protected files.
    """

    def __init__(self, name, content="", password=None):
        """
        Initializes a file with a name and optional content and password.

        Args:
            name (str): The name of the file.
            content (str): The text content of the file. Default is empty.
            password (str): An optional password for the file. Default is None.
        """
        self.name = name
        self.content = content
        self.password = password

    def read(self, password=None):
        """
        Reads the content of the file. If the file is password-protected, check the password.

        Args:
            password (str): The password for the file (if required).

        Returns:
            str: The content of the file.

        Raises:
            PermissionError: If the password is incorrect for a protected file.
        """
        if self.password and self.password != password:
            raise PermissionError("Incorrect password.")
        return self.content

    def write(self, new_content):
        """Replaces the file content with new content."""
        self.content = new_content

    def delete_line(self, line_no):
        """Deletes a specific line from the file content."""
        lines = self.content.splitlines()
        if 0 <= line_no < len(lines):
            del lines[line_no]
        self.content = "\n".join(lines)

    def search(self, keyword):
        """Checks if a keyword exists in the file content."""
        return keyword in self.content

class Folder:
    """
    Represents a folder containing files and/or other subfolders.
    """

    def __init__(self, name):
        """Initializes a folder with a name."""
        self.name = name
        self.children = {}

    def add(self, item):
        """Adds a file or folder to this folder."""
        if item.name in self.children:
            raise ValueError(f"'{item.name}' already exists in this folder.")
        self.children[item.name] = item

    def remove(self, name):
        """Removes a file or folder from this folder."""
        if name not in self.children:
            raise FileNotFoundError(f"'{name}' not found in this folder.")
        del self.children[name]

    def find(self, name):
        """Finds and returns a file or folder by name."""
        if name not in self.children:
            raise FileNotFoundError(f"'{name}' not found.")
        return self.children[name]

    def list_items(self):
        """Returns a list of all files and folders in this folder."""
        return list(self.children.keys())

class FileSystem:
    """
    Simulates a file system to manage files and folders with basic Linux-like commands.
    """

    def __init__(self):
        """Initializes a file system with a root folder."""
        self.root = Folder("root")
        self.current = self.root

    def parse_path(self, path):
        """
        Parses a path and returns the target folder or file.

        Args:
            path (str): The path to parse.

        Returns:
            File or Folder: The object at the given path.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        parts = path.strip("/").split("/")
        node = self.root if path.startswith("/") else self.current
        for part in parts:
            if part == "..":
                # Go up to root (simplified, no parent navigation)
                node = self.root
            elif part:
                node = node.find(part)
        return node

    def mkdir(self, name):
        """Creates a new folder in the current directory."""
        self.current.add(Folder(name))

    def ls(self):
        """Lists all items in the current folder."""
        return self.current.list_items()

    def cd(self, path):
        """Changes the current folder to the specified path."""
        destination = self.parse_path(path)
        if isinstance(destination, Folder):
            self.current = destination
        else:
            raise NotADirectoryError("Path is not a folder.")

    def cat(self, path, password=None):
        """Prints the content of a file at the given path."""
        file = self.parse_path(path)
        if isinstance(file, File):
            return file.read(password)
        else:
            raise FileNotFoundError("Path is not a file.")

    def mv(self, src_path, dest_path, password=None):
        """
        Moves or renames a file or folder.

        Args:
            src_path (str): Source path.
            dest_path (str): Destination path.
        """
        src = self.parse_path(src_path)
        dest_folder = self.parse_path("/".join(dest_path.split("/")[:-1]))
        new_name = dest_path.split("/")[-1]

        if isinstance(src, File) and src.password:
            if src.password != password:
                raise PermissionError("Incorrect password for protected file.")
        src.name = new_name
        dest_folder.add(src)
        self.current.remove(src.name)

    def cp(self, src_path, dest_path, password=None):
        """Copies a file from src_path to dest_path."""
        src = self.parse_path(src_path)
        dest_folder = self.parse_path("/".join(dest_path.split("/")[:-1]))
        new_name = dest_path.split("/")[-1]

        if isinstance(src, File):
            if src.password and src.password != password:
                raise PermissionError("Incorrect password for protected file.")
            dest_folder.add(File(new_name, src.content, src.password))
        else:
            raise FileNotFoundError("Source must be a file.")

    def rm(self, path, password=None):
        """Removes a file or folder."""
        target = self.parse_path(path)
        if isinstance(target, File) and target.password:
            if target.password != password:
                raise PermissionError("Incorrect password for protected file.")
        self.current.remove(target.name)

# Example usage
if __name__ == "__main__":
    fs = FileSystem()
    fs.mkdir("docs")
    fs.cd("docs")
    fs.current.add(File("file1.txt", content="Hello, World!", password=None))
    print(fs.ls())  # ['file1.txt']
    print(fs.cat("file1.txt"))  # "Hello, World!"
    fs.cd("..")
    print(fs.ls())  # ['docs']

