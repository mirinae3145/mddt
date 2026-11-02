# Running pixtwin unattended

This guide sets up a weekly scheduled run that scans the library and reports duplicates without a person watching.
Scheduled runs never call `move`, so nothing changes until a person reviews the report.

The job runs `pixtwin scan` followed by `pixtwin report --json`.
Because `report` exits with 1 when duplicates exist, the job can alert on that exit code.
The other codes are listed under [exit codes](cli.md#exit-codes).

1. Choose the scheduler: cron on any system, or a systemd timer on Linux.
1. Make the scheduler run `pixtwin scan PATH` and then `pixtwin report --json` once a week.
1. Make the scheduler alert when `report` exits with 1.
1. Review the report yourself and run `pixtwin move` when you are ready.

With systemd, an example unit pair is `pixtwin-scan.service` and `pixtwin-scan.timer`.
Logs from scheduled runs go to the places described under [logging](cli.md#logging).
