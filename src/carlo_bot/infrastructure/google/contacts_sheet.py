class GoogleContactsSheet:
    # Reads the contacts sheet from a Google Spreadsheet using the Sheets API v4
    def __init__(self, sheets_service, spreadsheet_id: str, sheet_name: str) -> None:
        self._service = sheets_service
        self._spreadsheet_id = spreadsheet_id
        self._sheet_name = sheet_name

    def load_contacts(self) -> list[dict]:
        # Fetches all columns from the sheet, maps header row to field names, returns normalised contact dicts
        response = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=self._spreadsheet_id, range=f"{self._sheet_name}!A:Z")
            .execute()
        )
        rows = response.get("values", [])
        if not rows:
            raise ValueError("Contacts sheet is empty.")

        # First row is treated as header; subsequent rows are data records
        headers = [header.strip().lower() for header in rows[0]]
        contacts = []
        for row in rows[1:]:
            # Skips entirely blank rows
            if not any(cell.strip() for cell in row):
                continue
            record = _row_to_record(headers, row)
            contacts.append(
                {
                    "name": record.get("nome", "").strip(),
                    "email": record.get("e-mail", "").strip(),
                    "active": _parse_bool(record.get("active", "true")),
                }
            )

        if not contacts:
            raise ValueError("Contacts sheet has no valid contacts.")

        return contacts


def _row_to_record(headers: list[str], row: list[str]) -> dict[str, str]:
    # Zips header names with row values; pads short rows with empty strings to avoid IndexError
    padded = row + [""] * max(0, len(headers) - len(row))
    return {header: value for header, value in zip(headers, padded, strict=False)}


def _parse_bool(value: str) -> bool:
    # Treats anything that is not an explicit false-ish string as True
    return value.strip().lower() not in {"false", "0", "no", "n"}