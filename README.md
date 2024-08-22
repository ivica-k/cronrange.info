## cron_range [![Build Status](https://travis-ci.com/ivica-k/chalice_cronrange.svg?branch=master)](https://travis-ci.com/ivica-k/chalice_cronrange)
Displays the next N number of executions for a given cron expression from a given datetime. Now with support for 
[AWS EventBridge expressions](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)!

## Usage
### Web
#### Visit [cronrange.info](https://cronrange.info/)

### CLI

Use [cronrange-cli](https://github.com/ivica-k/cronrange-cli)

### Local API server
```bash
make local
curl -H "Content-Type:application/json" \
 -d '{"executions": "10", "cron":"*/5 * * * *"}' \
 localhost:8000
```

##### JSON structure
| Key          | Description                                                                          | Default value            |
|--------------|--------------------------------------------------------------------------------------|--------------------------|
| `cron`       | A cron expression (string)                                                           | `None`                   |
| `executions` | Number of next executions to show.                                                   | 10                       |
| `start_date` | Date and time in `DD.MM.YYYY. HH:MM` format from which to calculate cron executions. | Current date and time.   |

### AWS EventBridge support
AWS EventBridge implementation of cron does not use 0 based day of week, instead it is `1-7 SUN-SAT` (instead of `0-6`), 
as well as supporting additional expression features such as first-weekday and last-day-of-month. [Source](https://en.wikipedia.org/wiki/Cron#Overview)

Because of that, `cronrange` does not support the full range of expression wildcards available on AWS EventBridge.

| Wildcard | Example expression | Supported |
|----------|--------------------|-----------|
| `L`      | `*/5 * L * ? *`    | Yes       |
| `W`      | `*/30 * 1W * ? *`  | No        |
| `#`      | `*/30 * ? * 3#2 *` | No        |
| `?`      | `0 8 1 * ? *`      | Yes       |

Classic cron expression wildcards such as `,`, `/`, `-` and `*` are supported.

### For developers

#### Virtualenv setup
```bash
make venv
```

#### Running tests
```bash
make test
```

#### Running a local server
```bash
make local
```