import io
import json
import sys
import copy
import math
import collections
from datetime import datetime, timedelta
from jinja2 import Template

one_week = timedelta(days=7)
	
	
def create_training_calendar(periods, schedule, plan):
	current_date = parse_date(plan['start_date'])
	end_date = parse_date(plan['end_date'])
	num_weeks = (end_date - current_date).days / 7
	calendar = []
	
	for period, duration_percentage in plan['periods'].items():
		period_weeks = int(round(num_weeks * duration_percentage))
		weeks = []
		for week in range(1, period_weeks+1):
			weeks.append((copy.copy(current_date), list(get_week_plan(periods[period], schedule, plan, week / float(period_weeks)))))
			current_date += one_week
		calendar.append((period, weeks))
	
	return calendar
			
			
def get_week_plan(period, schedule, plan, progress):
	for day, day_plan in schedule.items():
		if day_plan['activity'] == 'rest':
			yield (day, 'Rest', None)
		elif day_plan['activity'] == 'run':
			yield (day, 'Run', get_day_run_plan(plan['start']['run'], period['run'], day_plan, progress))
		elif day_plan['activity'] == 'lift':
			yield (day, 'Lift', get_day_lift_plan(plan['start']['lift'], period['lift'], day_plan))
		else:
			raise Exception('Unknown activity: "%s"' % day_plan['activity'])
			
			
def get_day_run_plan(base, period, day_plan, progress):
	base_distance = base[day_plan['duration']]
	distance_increase = base_distance * period['distance'][day_plan['duration']]['change']
	current_distance = progress * distance_increase + base_distance
	intensity = period['intensity'][day_plan['intensity']]
	return {
		'distance': current_distance,
		'intensity': intensity
	}
	
	
def get_day_lift_plan(base, period, day_plan):
	exercises = []
	for exercise in day_plan['exercises']:
		exercises.append({
			'name': exercise,
			'weight': int(math.ceil(period['intensity'] * base[exercise])),
			'sets': period['sets'],
			'reps': period['reps'],
			'rest': period['rest']
		})
	return exercises
	
	
def parse_date(date_str):
	y,m,d = map(int, date_str.split('-'))
	return datetime(year=y, month=m, day=d)
	
	
def calendar_to_html(calendar, title=''):
	template = Template(io.open('templates/calendar.j2', 'r', encoding='utf-8').read())
	return template.render(title=title, calendar=calendar)
	
	
if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Usage: %s <plan> <schedule>"
		sys.exit(1)
		
	periods = json.load(open('periods.json', 'r'))
	plan = json.load(open(sys.argv[1], 'r'))
	schedule = json.load(open(sys.argv[2], 'r'), object_pairs_hook=collections.OrderedDict)
	calendar = create_training_calendar(periods, schedule, plan)
	title = sys.argv[1].split('.')[0].split('/')[-1]
	print calendar_to_html(calendar, title=title)
	
	