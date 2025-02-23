
import unittest
import logging


import logging


logging.basicConfig(
    level=logging.DEBUG,  # Or INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("test_results.log", mode="w"),  # Log file
        logging.StreamHandler()  # Console output
    ]
)

log = logging.getLogger("test_logger")

if __name__ == "__main__":
    log.info("🚀 Running all tests...")

    loader = unittest.TestLoader()
    suite = loader.discover("tests")

    runner = unittest.TextTestRunner(verbosity=1)  # Lower verbosity for cleaner output
    result = runner.run(suite)

    # Log summary
    if result.wasSuccessful():
        log.info("✅ All tests passed!")
    else:
        log.error(f"❌ Some tests failed! {len(result.failures)} failures, {len(result.errors)} errors.")

    if not result.wasSuccessful():
        exit(1)
