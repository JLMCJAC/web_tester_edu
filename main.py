"""Punto de entrada principal para ejecutar WEB TESTER EDU."""

from ui.app import WebTesterApp

if __name__ == "__main__":
    app = WebTesterApp()
    app.mainloop()