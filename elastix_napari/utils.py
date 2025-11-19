from qtpy.QtWidgets import QMessageBox


def error(message):
    """
    Shows a pop up with the given error message.
    """
    print("ERROR: ", message)
    QMessageBox.critical(None, "Error", message)


def check_filename(filename):
    """
    Checks if filename adheres to the correct format.
    """
    if (filename.suffix == ".txt") or (filename.suffix == ".vtk"):
        return True
    else:
        return False
