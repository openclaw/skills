# Zoho Projects API Reference

## Endpoints

### Projects
- GET `/projects/` — List all projects
- GET `/projects/{id}/` — Get project details
- POST `/projects/` — Create project
- PUT `/projects/{id}/` — Update project
- DELETE `/projects/{id}/` — Delete project

### Tasks
- GET `/projects/{id}/tasks/` — List tasks
- POST `/projects/{id}/tasks/` — Create task
- PUT `/projects/{id}/tasks/{task_id}/` — Update task
- DELETE `/projects/{id}/tasks/{task_id}/` — Delete task

### Milestones
- GET `/projects/{id}/milestones/` — List milestones
- POST `/projects/{id}/milestones/` — Create milestone

### Task Lists
- GET `/projects/{id}/tasklists/` — List task lists
- POST `/projects/{id}/tasklists/` — Create task list

### Timesheets
- GET `/projects/{id}/logs/` — List time logs
- POST `/projects/{id}/tasks/{task_id}/logs/` — Add time log

### Bugs
- GET `/projects/{id}/bugs/` — List bugs
- POST `/projects/{id}/bugs/` — Create bug

## Task Fields
- name, start_date (MM-DD-YYYY), end_date, priority (None/Low/Medium/High), owner, description, tasklist_id, percent_complete

## Project Fields
- name, description, status (active/archived), start_date, end_date, owner
