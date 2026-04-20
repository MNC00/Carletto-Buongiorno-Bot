class GoogleContentSheet:
    # Reads content datasets (quotes, saints, blasfemie) from a single Google Spreadsheet
    def __init__(self, sheets_service, spreadsheet_id: str) -> None:
        self._service = sheets_service
        self._spreadsheet_id = spreadsheet_id

    def load_values(self, sheet_name: str) -> list[str]:
        # Fetches the named sheet, locates the required 'value' column, and returns active non-empty entries
        response = (
            self._service.spreadsheets()
            .values()
            .get(spreadsheetId=self._spreadsheet_id, range=f"{sheet_name}!A:Z")
            .execute()
        )
        rows = response.get("values", [])
        if not rows:
            raise ValueError(f"{sheet_name} sheet is empty.")

        # First row is the header; we require a column named 'value'
        headers = [header.strip().lower() for header in rows[0]]
        try:
            value_index = headers.index("value")
        except ValueError as error:
            raise ValueError(f"{sheet_name} sheet is missing a 'value' column.") from error

        # Optional 'active' column: rows marked false/0/no/n are skipped
        active_index = headers.index("active") if "active" in headers else None

        values = []
        for row in rows[1:]:
            if value_index >= len(row):
                continue
            value = row[value_index].strip()
            if not value:
                continue
            if active_index is not None and active_index < len(row):
                active_value = row[active_index].strip().lower()
                if active_value in {"false", "0", "no", "n"}:
                    continue
            values.append(value)

        if not values:
            raise ValueError(f"{sheet_name} sheet has no active values.")

        return values