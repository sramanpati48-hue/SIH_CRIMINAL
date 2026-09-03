"""Memory-conscious CSV streaming reader with robust error handling."""

import csv
from typing import Generator, Any, TypeVar, Type
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)

MAX_ROWS = 50000

class IngestionRowError(Exception):
    def __init__(self, row_number: int, field_name: str, message: str):
        self.row_number = row_number
        self.field_name = field_name
        self.message = message
        super().__init__(f"Row {row_number}, Field '{field_name}': {message}")


def stream_csv_file(file_path: str, schema: Type[T]) -> Generator[tuple[int, T | None, list[IngestionRowError]], None, None]:
    """
    Stream a CSV file row by row, validating against a Pydantic schema.
    Yields (row_number, parsed_record, errors).
    """
    # Detect empty files / validate size in a higher layer (e.g. FastAPI UploadFile.size)
    # Here we focus on reading safely.
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                yield 1, None, [IngestionRowError(1, "file", "File is empty or headers are missing.")]
                return

            # Check if headers match the schema minimally (pydantic handles extra='forbid' or missing fields)
            for row_idx, row in enumerate(reader, start=2): # Row 1 is header
                if row_idx > MAX_ROWS + 1:
                    yield row_idx, None, [IngestionRowError(row_idx, "file", f"Exceeded maximum row limit of {MAX_ROWS}.")]
                    break
                
                try:
                    # Clean up empty strings to None if they are supposed to be optional, 
                    # but Pydantic handles empty strings for required strings usually (and our validator checks length).
                    cleaned_row = {k: (v.strip() if v else None) for k, v in row.items()}
                    record = schema(**cleaned_row)
                    yield row_idx, record, []
                except ValidationError as ve:
                    errors = []
                    for err in ve.errors():
                        loc = err["loc"][0] if err["loc"] else "unknown"
                        msg = err["msg"]
                        errors.append(IngestionRowError(row_idx, str(loc), msg))
                    yield row_idx, None, errors
                except Exception as e:
                    yield row_idx, None, [IngestionRowError(row_idx, "row", f"Malformed row or unexpected error: {str(e)}")]

    except Exception as e:
        yield 0, None, [IngestionRowError(0, "file", f"Failed to read CSV: {str(e)}")]
