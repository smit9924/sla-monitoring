import functions_framework


@functions_framework.cloud_event
def parse_csv(cloud_event):
    """
    Cloud Storage-triggered function: fires automatically whenever a new
    object finishes uploading to the configured bucket

    The trigger fires for *every* uploaded object, not just .csv ones —
    Eventarc can't filter by filename, so we filter here instead.
    """
    data = cloud_event.data
    bucket = data["bucket"]
    name = data["name"]

    if not name.lower().endswith(".csv"):
        print(f"Ignoring non-CSV file: {name}")
        return

    print(f"Hello, World! Triggered by {name} in bucket {bucket}.")
