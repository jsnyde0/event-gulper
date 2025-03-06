from orchestration.siegessaeule_flow import scrape_siegessaeule

if __name__ == "__main__":
    # This serve call registers the deployment and starts a long-running process
    # that will poll the Prefect server for work (manual or scheduled).
    # You can adjust the parameters (and interval, cron or tags) as needed.
    scrape_siegessaeule.serve(
        name="scrape_siegessaeule",
        parameters={
            "start_date": "2025-02-20",
            "end_date": "2025-02-21",
            "batch_size": 10,
            "max_batches": None,
        },
        # interval=60,  # poll every 60 seconds
        pause_on_shutdown=True,
    )
