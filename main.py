
from config.logger_config import configure_logger
app_logger = configure_logger("PHOMODLogger", log_to_console=True, log_to_file=True)

from phomod_controller import PhomodController
from phomod_ui import PhomodUI

if __name__ == "__main__":
    app_logger.info("👩‍🚀 Initializing application...")

    controller = PhomodController()
    ui = PhomodUI(controller)
    ui.mainloop()

    app_logger.info("💤 Application shut down.")
