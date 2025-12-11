import { NextResponse } from 'next/server';
import { readFile } from 'fs/promises';
import { join } from 'path';
import { parseSchedule, getServiceFromTaskName, calculateLastRun } from '@/utils/scheduleParser';

export async function GET() {
  try {
    // Read from single source of truth in src/configs
    const schedulePath = join(process.cwd(), '..', 'src', 'configs', 'schedule.json');
    const scheduleContent = await readFile(schedulePath, 'utf-8');
    const scheduleData = JSON.parse(scheduleContent);

    const tasks = scheduleData.tasks.map((task, index) => {
      const scheduleInfo = parseSchedule(task.schedule);

      return {
        id: `task-${index + 1}`,
        name: task.name,
        description: task.description,
        schedule: task.schedule,
        cronExpression: scheduleInfo.cronExpression,
        humanReadable: scheduleInfo.humanReadable,
        nextRun: scheduleInfo.nextRun.toISOString(),
        lastRun: calculateLastRun(scheduleInfo.nextRun, task.schedule).toISOString(),
        status: 'active' as const,
        service: getServiceFromTaskName(task.name),
        command: task.command,
      };
    });

    return NextResponse.json({ tasks });
  } catch (error) {
    console.error('Error loading schedule:', error);
    return NextResponse.json(
      { error: 'Failed to load schedule' },
      { status: 500 }
    );
  }
}
