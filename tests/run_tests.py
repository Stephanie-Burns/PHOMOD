import unittest
import logging

# Unified logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} | {levelname:<8} | {message}",
    datefmt="%Y-%m-%d %H:%M:%S",
    style="{",
    handlers=[
        logging.FileHandler("test_results.log", mode="w"),
        logging.StreamHandler()
    ]
)

log = logging.getLogger("test_logger")

if __name__ == "__main__":
    log.info("🚀 Running all tests...")

    loader = unittest.TestLoader()
    suite = loader.discover("tests")

    # **Use verbosity=0 to remove unittest's dot output**
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)

    # Logging the summary
    if result.wasSuccessful():
        log.info("✅ All tests passed!")
    else:
        log.error(f"❌ Some tests failed! {len(result.failures)} failures, {len(result.errors)} errors.")

    # Ensure failures return a non-zero exit code
    if not result.wasSuccessful():
        exit(1)
