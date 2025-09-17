def convert_train_order_to_schedule(train_order, train_sections_df, sections_df, default_section_time=10):
    """
    Convert a list of train IDs (train_order) into detailed schedule dict:
    {train_id: [{section_id, start_time}, ...], ...}
    """
    schedule = {}
    grouped = train_sections_df.groupby('train_id')

    for train_id in train_order:
        if train_id not in grouped.groups:
            continue
        train_sections = train_sections_df.loc[grouped.groups[train_id]]
        train_sections = train_sections.sort_values('scheduled_entry_time')
        section_list = train_sections['section_id'].tolist()

        start_time = 0
        schedule[train_id] = []
        for section_id in section_list:
            if 'length_km' in sections_df.columns:
                section_length = sections_df.loc[sections_df['section_id'] == section_id, 'length_km'].values
                time_to_travel = section_length[0] if len(section_length) > 0 else default_section_time
            else:
                time_to_travel = default_section_time

            schedule[train_id].append({
                "section_id": section_id,
                "start_time": start_time
            })
            start_time += time_to_travel

    return schedule
