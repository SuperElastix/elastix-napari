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
    if '.txt' in str(filename[0]) or '.vtk' in str(filename[0]):
        return True
    else:
        return False
