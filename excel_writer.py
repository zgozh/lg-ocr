import os


def _field_defaults(template):
    return {field["name"]: field.get("default", "") for field in template["fields"]}


def normalize_people_records(llm_data, template):
    defaults = _field_defaults(template)
    normalized = []
    for person in llm_data:
        record = defaults.copy()
        for key, value in person.items():
            if key in record:
                record[key] = value
        normalized.append(record)
    return normalized


def build_output_rows(llm_data, template, image_path):
    records = normalize_people_records(llm_data, template)
    output = template["output"]
    image_name = os.path.basename(image_path)
    image_parent_name = os.path.basename(os.path.dirname(image_path))
    image_dir_name = os.path.basename(os.path.dirname(os.path.dirname(image_path)))

    rows = []
    for record in records:
        row = {}
        for column in output["columns"]:
            source = column["source"]
            header = column["header"]
            if source == "field":
                row[header] = record.get(column["field"], "")
            elif source == "constant":
                row[header] = column.get("value", "")
            elif source == "image_name":
                row[header] = image_name
            elif source == "image_parent_name":
                row[header] = image_parent_name
            elif source == "image_dir_name":
                row[header] = image_dir_name
            else:
                raise ValueError(f"Unsupported output column source: {source}")
        rows.append(row)

    if rows:
        for header, value in output.get("first_row_overrides", {}).items():
            rows[0][header] = value

    return rows


def extract_data_excel(llm_data, save_xlsx_path, image_path, template):
    import pandas as pd

    rows = build_output_rows(llm_data, template, image_path)
    if not rows:
        return save_xlsx_path

    output = template["output"]
    df1 = pd.DataFrame(rows)

    if os.path.exists(save_xlsx_path):
        original_data = pd.read_excel(save_xlsx_path, dtype=str)
        save_data = pd.concat([original_data, df1], axis=0)
    else:
        save_data = df1

    sheet_name = output.get("sheet_name", "Sheet")
    with pd.ExcelWriter(save_xlsx_path, engine="openpyxl", mode="w") as writer:
        save_data.to_excel(writer, index=False, sheet_name=sheet_name)
        worksheet = writer.sheets[sheet_name]
        for header in output.get("text_columns", []):
            if header not in save_data.columns:
                continue
            column_index = list(save_data.columns).index(header) + 1
            for row_index in range(2, worksheet.max_row + 1):
                worksheet.cell(row=row_index, column=column_index).number_format = "@"

    return save_xlsx_path
