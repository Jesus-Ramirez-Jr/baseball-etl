from pybaseball import schedule_and_record

df = schedule_and_record(2024, 'CHW')
print(df[df['Date'].str.contains('Apr 17')].to_string())
