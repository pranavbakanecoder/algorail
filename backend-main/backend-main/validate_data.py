import pandas as pd

# Load CSVs
stations = pd.read_csv("data/data/stations.csv")
trains = pd.read_csv("data/data/trains.csv")
sections = pd.read_csv("data/data/sections.csv")
train_sections = pd.read_csv("data/data/train_sections.csv")
disruptions = pd.read_csv("data/data/disruptions.csv")


print("✅ Loaded all CSVs")

# -------------------
# 1. Schema check
# -------------------
expected_trains_cols = {"train_id","train_name","train_type","priority","max_speed_kmph","platform_requirement","scheduled_start_time","origin_station","destination_station","route_nodes","route_sections","delay_minutes"}
expected_sections_cols = {"section_id","from_station","to_station","length_km","track_type","max_trains_allowed","block_length_km","num_blocks","junction_flag"}
expected_train_sections_cols = {"train_id","section_id","scheduled_entry_time","scheduled_exit_time","planned_stop_next_station","dwell_minutes_next_station"}

print("\nSchema check:")
print("Trains OK?", set(trains.columns) >= expected_trains_cols)
print("Sections OK?", set(sections.columns) >= expected_sections_cols)
print("Train_Sections OK?", set(train_sections.columns) >= expected_train_sections_cols)

# -------------------
# 2. Time format check (HH:MM)
# -------------------
def is_hhmm(time_str):
    try:
        pd.to_datetime(time_str, format="%H:%M")
        return True
    except:
        return False

bad_times = []
for col in ["scheduled_start_time"]:
    bad_times.extend([t for t in trains[col] if not is_hhmm(str(t))])

bad_times.extend([t for t in train_sections["scheduled_entry_time"] if not is_hhmm(str(t))])
bad_times.extend([t for t in train_sections["scheduled_exit_time"] if not is_hhmm(str(t))])

print("\nTime format check:")
if bad_times:
    print("❌ Bad time values:", bad_times[:10])
else:
    print("✅ All times are in HH:MM format")

# -------------------
# 3. Foreign key checks
# -------------------
missing_trains = [tid for tid in train_sections["train_id"].unique() if tid not in trains["train_id"].unique()]
missing_sections = [sid for sid in train_sections["section_id"].unique() if sid not in sections["section_id"].unique()]

print("\nForeign key check:")
if not missing_trains and not missing_sections:
    print("✅ All foreign keys match")
else:
    if missing_trains:
        print("❌ Missing trains:", missing_trains[:10])
    if missing_sections:
        print("❌ Missing sections:", missing_sections[:10])
