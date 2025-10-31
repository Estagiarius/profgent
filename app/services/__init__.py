from .data_service import DataService

# Create a single, shared instance of the DataService.
# This instance will be imported by other parts of the application (e.g., tools)
# to ensure that everyone uses the same service object.
data_service = DataService()
