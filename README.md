# Music Separator

A web service where you can upload an audio file, automatically split the track into separate tracks (stems) using Demucs, and download the result as a ZIP archive.

## Demo

### Web interface

#### Upload page

![Service UI](docs/images/service_UI.PNG)

#### Result page

![Service Result UI](docs/images/service_result_UI.PNG)

#### Full workflow

![Workflow Demo](docs/run_service.gif)

## Features

* Accepts audio files via HTTP API;
* Creates a task and saves it in PostgreSQL;
* Sends the task to the RabbitMQ queue;
* Processes the file asynchronously using a Celery worker;
* Splits the track into stems using Demucs;
* Saves the result to a shared volume;
* Allows you to check the task status;
* Allows you to download the finished ZIP archive with the results.

## Architecture

The service has several parts:

* **FastAPI** — receives requests and sends responses;
* **PostgreSQL** — stores tasks and their statuses;
* **RabbitMQ** — the task queue;
* **Celery worker** — runs the heavy background processing;
* **Demucs** — splits the audio file into tracks.

## Main Workflow

1. The user sends a file to `POST /api/separate`.
2. The server creates a task with the `pending` status.
3. The task goes to RabbitMQ.
4. The Celery worker takes the task and changes the status to `processing`.
5. Demucs splits the audio file.
6. The result is packed into a ZIP archive.
7. The task status changes to `completed`.
8. The user downloads the archive via `GET /api/download/{job_id}`.

## API

### `POST /api/separate`

Uploads an audio file and creates a processing task.

**Supported formats:**

* `mp3`
* `wav`
* `flac`

**Response:**

```json
{
  "job_id": "0980261f-cc9e-414f-91cc-efbbc5176f99",
  "status": "pending"
}
```

### `GET /api/jobs/{job_id}`

Returns the current status of the task.

**Response example:**

```json
{
  "job_id": "0980261f-cc9e-414f-91cc-efbbc5176f99",
  "status": "completed",
  "filename": "Example.wav",
  "error": null
}
```

### `GET /api/download/{job_id}`

Downloads the ZIP archive with the results (if the task is finished successfully).

## How to Use

### 1. Create environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

For Windows:

```powershell
copy .env.example .env
```

The default values are already configured for Docker Compose.

### 2. Run the project with Docker Compose

Run this command from the project root folder:

```bash
docker compose up -d --build
```

After it starts, you can access:

* FastAPI: `http://localhost:8000`
* RabbitMQ Management: `http://localhost:15672`
* PostgreSQL: `localhost:5432`

### 3. Apply migrations

If the migrations did not apply automatically, run:

```bash
docker compose exec api alembic upgrade head
```

### 4. Send a file for processing

Example with `curl`:

```bash
curl.exe -X POST http://localhost:8000/api/separate -F "file=@E:\Downloads\Example.wav"
```

### 5. Check the task status

Use the `job_id`, from the previous response:

```bash
curl.exe http://localhost:8000/api/jobs/<job_id>
```

### 6. Download the result

When the status is `completed`, run:

```bash
curl.exe -O http://localhost:8000/api/download/<job_id>
```

## Environment Variables

The project uses Docker Compose networking.

Container names are used as hostnames:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/music_separator
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/music_separator_test
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672//
```

`postgres` and `rabbitmq` are Docker service names defined in `docker-compose.yml`.

## Task Statuses

* `pending` — the task is created and waiting for processing;
* `processing` — the task is running right now;
* `completed` — processing finished successfully;
* `failed` — an error happened during processing.

## Testing

The project includes:

* Unit tests;
* API tests;
* Integration tests with PostgreSQL.

## Where Files Are Stored

* Uploaded files are stored in a Docker volume mounted to `/app/uploads`;
* Generated stems and ZIP archives are stored in a Docker volume mounted to `/app/outputs`;
* API and Celery worker share the same volumes;
* Demucs logs are saved in the `logs` folder.

In Docker, these directories are mounted as shared volumes so that the API and the worker can use the same files.

## Notes

* Demucs might download the model when you process a file for the first time;
* You might need a VPN or a stable internet connection to download the model;
* The first run of the worker can take more time because it needs to download the model.

## Technologies

* Python 3.11
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* RabbitMQ
* Celery
* Demucs
* Docker

## Troubleshooting (Possible Errors)

### `relation "jobs" does not exist`

This means migrations are not applied. Run this command:

```bash
docker compose exec api alembic upgrade head
```

### `Cannot connect to amqp://...`

Check that RabbitMQ is running and your `RABBITMQ_URL` points to the correct address.

### `Demucs ended with the code 1`

Check the worker logs and the Demucs log file in the `logs` folder.

---

