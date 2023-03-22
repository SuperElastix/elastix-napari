from qtpy.QtWidgets import QMessageBox


def error(message):
    """
    Shows a pop up with the given error message.
    """
    e = QMessageBox()
    print("ERROR: ", message)
    e.setText(message)
    e.setIcon(QMessageBox.Critical)
    e.setWindowTitle("Error")
    e.show()
    return e


def check_filename(filename):
    """
    Checks if filename adheres to the correct format.
    """
    if (filename.suffix == '.txt') or (filename.suffix == '.vtk'):
        return True
    else:
        return False
