def parse_apps_list(dokku_output):
    """
    Transform the Dokku apps:list output into an array of app names.
    """
    lines = dokku_output.strip().split("\n")
    apps = [app.strip() for app in lines[1:] if app.strip()]
    return apps


def parse_report(dokku_output):
    """
    Transform a Dokku report output into a dictionary of information.
    """
    lines = dokku_output.strip().split("\n")
    report = {}

    for line in lines[1:]:  # Skip the first line (header)
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        report[key] = value

    return report
