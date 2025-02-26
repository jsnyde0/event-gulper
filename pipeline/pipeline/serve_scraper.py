from pipeline.pipelines import scrape_siegessaeule_events

if __name__ == "__main__":
    # This serve call registers the deployment and starts a long-running process
    # that will poll the Prefect server for work (manual or scheduled).
    # You can adjust the parameters (and interval, cron or tags) as needed.
    scrape_siegessaeule_events.serve(
        name="siegessaeule-scraper-deployment",
        parameters={"target_date": "2025-02-20"},
        # interval=60,  # poll every 60 seconds
        pause_on_shutdown=True,
    )
