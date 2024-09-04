import os
from analytics.bi_weekly import BiWeeklyUpdate
from analytics.daily import DailyUpdate
from analytics.readme import READMEUpdater
from analytics.shields import BadgeDataUpdater

def daily_update(repo_owner, repo_name, access_token):
    """
    Perform the daily update tasks:
    1. Update daily stats.
    2. Update shields.
    3. Update README.
    """
    # Daily stats update
    daily_update = DailyUpdate(repo_owner, repo_name, access_token)
    daily_update.run()

    # Shields update
    badge_updater = BadgeDataUpdater(repo_owner, repo_name, access_token)
    badge_updater.run()

    # README update
    readme_updater = READMEUpdater(
        readme_path="README.md",
        plot_path="usage/analytics/plots/clones_plot.png",
        downloads_md_path="usage/analytics/plots/downloads_table.md",
        paths_md_path="usage/analytics/plots/paths_table.md",
        referrers_md_path="usage/analytics/plots/referrers_table.md"
    )
    readme_updater.run()

def biweekly_update(repo_owner, repo_name, access_token):
    """
    Perform the bi-weekly update tasks:
    1. Aggregate bi-weekly data.
    2. Update shields.
    3. Update README.
    """
    # Bi-weekly stats aggregation
    biweekly_update = BiWeeklyUpdate(repo_owner, repo_name, access_token)
    biweekly_update.run()

    # Shields update
    badge_updater = BadgeDataUpdater(repo_owner, repo_name, access_token)
    badge_updater.run()

    # README update
    readme_updater = READMEUpdater(
        readme_path="README.md",
        plot_path="usage/analytics/plots/clones_plot.png",
        downloads_md_path="usage/analytics/plots/downloads_table.md",
        paths_md_path="usage/analytics/plots/paths_table.md",
        referrers_md_path="usage/analytics/plots/referrers_table.md"
    )
    readme_updater.run()

def main():
    """
    Main entry point for the package.
    - Runs daily updates by default.
    - Runs bi-weekly updates if `--biweekly` is passed as a flag.
    """
    repo_owner = "sandialabs"
    repo_name = "snl-quest"
    access_token = os.getenv('QUEST_TOKEN')

    import argparse
    parser = argparse.ArgumentParser(description="Run GitHub stats aggregation and update.")
    parser.add_argument('--biweekly', action='store_true', help="Run bi-weekly updates instead of daily.")
    args = parser.parse_args()

    if args.biweekly:
        biweekly_update(repo_owner, repo_name, access_token)
    else:
        daily_update(repo_owner, repo_name, access_token)

if __name__ == "__main__":
    main()
