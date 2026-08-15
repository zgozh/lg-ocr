def sort_texts_by_boxes(rec_texts, rec_boxes, row_threshold_ratio=0.3):
    if len(rec_texts) != len(rec_boxes):
        raise ValueError("rec_texts and rec_boxes length must match")
    if len(rec_texts) == 0:
        return []

    text_info = []
    for text, box in zip(rec_texts, rec_boxes):
        x1, y1, x2, y2 = box
        text_info.append(
            {
                "text": text,
                "y_center": (y1 + y2) / 2,
                "x_left": x1,
                "height": y2 - y1,
            }
        )

    avg_height = sum(info["height"] for info in text_info) / len(text_info)
    row_threshold = avg_height * row_threshold_ratio
    text_info_sorted_by_y = sorted(text_info, key=lambda x: x["y_center"])

    rows = []
    current_row = [text_info_sorted_by_y[0]]
    for info in text_info_sorted_by_y[1:]:
        if info["y_center"] - current_row[-1]["y_center"] <= row_threshold:
            current_row.append(info)
        else:
            rows.append(current_row)
            current_row = [info]
    rows.append(current_row)

    sorted_texts = []
    for row in rows:
        row_sorted_by_x = sorted(row, key=lambda x: x["x_left"])
        sorted_texts.extend(info["text"] for info in row_sorted_by_x)

    return sorted_texts
