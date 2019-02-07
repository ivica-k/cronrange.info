## cron_range [![Build Status](https://travis-ci.com/ivica-k/chalice_cronrange.svg?branch=master)](https://travis-ci.com/ivica-k/chalice_cronrange)
Displays the next N number of executions for a given cron expression. Consists of a `cronrange` library based on [croniter](https://github.com/kiorky/croniter) that you can run from the CLI, and from an API running on [AWS Lambda](https://github.com/aws/chalice) with API Gateway which you can also run locally

#### virtual env
```bash
make venv
```

#### CLI usage
```bash
python chalicelib/cronrange.py
```
##### Options
| Option            | Description                                                                        | Default value          |
|-------------------|------------------------------------------------------------------------------------|------------------------|
| `-c/--cron`       | A cron expression (string)                                                         | `None`                 |
| `-n/--executions` | Number of next executions to show.                                                 | 5                      |
| `-d/--start_date` | Date and time in DD.MM.YYYY. HH:MM format from which to calculate cron executions. | Current date and time. |

##### Examples
```bash
python chalicelib/cronrange.py -c "*/5 * * * *"
python chalicelib/cronrange.py -c "5 * * * *" -d "23.11.1999. 19:30"
python chalicelib/cronrange.py -c "5 * * * *" -d "23.11.1999. 19:30" -n 50
```

#### API usage
##### Local server
```bash
make local
curl -H "Content-Type:application/json" \
 -d '{"executions": "10", "cron":"*/5 * * * *"}' \
 localhost:8000
```

##### JSON structure
| Key               | Description                                                                        | Default value          |
|-------------------|------------------------------------------------------------------------------------|------------------------|
| `cron` | A cron expression (string)                                                         | `None`                 |
| `executions`      | Number of next executions to show.                                                 | 5                      |
| `start_date`        | Date and time in DD.MM.YYYY. HH:MM format from which to calculate cron executions. | Current date and time. |

#### Tests
```bash
make test
```
