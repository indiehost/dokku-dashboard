def parse_apps_list(dokku_output):
    """
    Transform the Dokku apps:list output into an array of app names.
    """
    lines = dokku_output.strip().split("\n")
    apps = [app.strip() for app in lines[1:] if app.strip()]
    return apps


def parse_app_report(dokku_output):
    """
    Transform the Dokku apps:report output into a dictionary of app information.
    """
    lines = dokku_output.strip().split("\n")
    return lines


def parse_domains_report(dokku_output):
    """
    Transform the Dokku domains:report output into a dictionary of app domains information.
    """
    lines = dokku_output.strip().split("\n")
    domains_info = {}

    for line in lines[1:]:  # Skip the first line (header)
        key, value = line.split(":", 1)
        key = key.strip().lower().replace(" ", "_")
        value = value.strip()
        domains_info[key] = value

    return domains_info
