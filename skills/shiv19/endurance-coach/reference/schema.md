# Database Schema Reference (One Table Per Line)

## Tables

- activities: id, name, sport_type, start_date, elapsed_time, moving_time, distance, total_elevation_gain, average_speed, max_speed, average_heartrate, max_heartrate, average_watts, max_watts, weighted_average_watts, kilojoules, suffer_score, average_cadence, calories, description, workout_type, gear_id, raw_json, synced_at
- streams: activity_id, time_data, distance_data, heartrate_data, watts_data, cadence_data, altitude_data, velocity_data
- athlete: id, firstname, lastname, weight, ftp, max_heartrate, raw_json, updated_at
- goals: id, event_name, event_date, event_type, notes, created_at
- sync_log: id, started_at, completed_at, activities_synced, status

## Views

- weekly_volume: week, sport_type, sessions, hours, km, avg_hr, avg_effort
- recent_activities: date, sport_type, name, minutes, km, hr, suffer_score

## Indexes

- idx_activities_date on activities(start_date)
- idx_activities_sport on activities(sport_type)
- idx_activities_sport_date on activities(sport_type, start_date)
