/**
 * Parse human-readable schedule strings into next run times
 */

export interface ScheduleInfo {
  nextRun: Date;
  cronExpression: string;
  humanReadable: string;
}

export function parseSchedule(schedule: string): ScheduleInfo {
  const now = new Date();
  let nextRun = new Date(now);

  // Parse different schedule formats
  if (schedule.includes('every day at')) {
    const timeMatch = schedule.match(/at (\d{2}):(\d{2})/);
    if (timeMatch) {
      const [_, hours, minutes] = timeMatch;
      nextRun.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      // If time has passed today, schedule for tomorrow
      if (nextRun <= now) {
        nextRun.setDate(nextRun.getDate() + 1);
      }

      return {
        nextRun,
        cronExpression: `${minutes} ${hours} * * *`,
        humanReadable: `Daily at ${hours}:${minutes}`,
      };
    }
  }

  if (schedule.includes('every monday at')) {
    const timeMatch = schedule.match(/at (\d{2}):(\d{2})/);
    if (timeMatch) {
      const [_, hours, minutes] = timeMatch;
      nextRun.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      // Find next Monday
      const daysUntilMonday = (1 - now.getDay() + 7) % 7;
      nextRun.setDate(now.getDate() + (daysUntilMonday || 7));

      if (nextRun <= now) {
        nextRun.setDate(nextRun.getDate() + 7);
      }

      return {
        nextRun,
        cronExpression: `${minutes} ${hours} * * 1`,
        humanReadable: `Every Monday at ${hours}:${minutes}`,
      };
    }
  }

  if (schedule.includes('every friday at')) {
    const timeMatch = schedule.match(/at (\d{2}):(\d{2})/);
    if (timeMatch) {
      const [_, hours, minutes] = timeMatch;
      nextRun.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      // Find next Friday (5)
      const daysUntilFriday = (5 - now.getDay() + 7) % 7;
      nextRun.setDate(now.getDate() + (daysUntilFriday || 7));

      if (nextRun <= now) {
        nextRun.setDate(nextRun.getDate() + 7);
      }

      return {
        nextRun,
        cronExpression: `${minutes} ${hours} * * 5`,
        humanReadable: `Every Friday at ${hours}:${minutes}`,
      };
    }
  }

  if (schedule.includes('every saturday at')) {
    const timeMatch = schedule.match(/at (\d{2}):(\d{2})/);
    if (timeMatch) {
      const [_, hours, minutes] = timeMatch;
      nextRun.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      // Find next Saturday (6)
      const daysUntilSaturday = (6 - now.getDay() + 7) % 7;
      nextRun.setDate(now.getDate() + (daysUntilSaturday || 7));

      if (nextRun <= now) {
        nextRun.setDate(nextRun.getDate() + 7);
      }

      return {
        nextRun,
        cronExpression: `${minutes} ${hours} * * 6`,
        humanReadable: `Every Saturday at ${hours}:${minutes}`,
      };
    }
  }

  if (schedule.includes('every sunday at')) {
    const timeMatch = schedule.match(/at (\d{2}):(\d{2})/);
    if (timeMatch) {
      const [_, hours, minutes] = timeMatch;
      nextRun.setHours(parseInt(hours), parseInt(minutes), 0, 0);

      // Find next Sunday (0)
      const daysUntilSunday = (7 - now.getDay()) % 7;
      nextRun.setDate(now.getDate() + (daysUntilSunday || 7));

      if (nextRun <= now) {
        nextRun.setDate(nextRun.getDate() + 7);
      }

      return {
        nextRun,
        cronExpression: `${minutes} ${hours} * * 0`,
        humanReadable: `Every Sunday at ${hours}:${minutes}`,
      };
    }
  }

  if (schedule.includes('every 2 weeks')) {
    // Set to 14 days from now
    nextRun.setDate(now.getDate() + 14);
    nextRun.setHours(12, 0, 0, 0);

    return {
      nextRun,
      cronExpression: '0 12 */14 * *',
      humanReadable: 'Every 2 weeks',
    };
  }

  if (schedule.includes('every 4 weeks')) {
    // Set to 28 days from now
    nextRun.setDate(now.getDate() + 28);
    nextRun.setHours(12, 0, 0, 0);

    return {
      nextRun,
      cronExpression: '0 12 */28 * *',
      humanReadable: 'Every 4 weeks',
    };
  }

  // Default fallback
  return {
    nextRun: new Date(now.getTime() + 60 * 60 * 1000), // 1 hour from now
    cronExpression: '0 * * * *',
    humanReadable: schedule,
  };
}

export function getServiceFromTaskName(taskName: string): string {
  if (taskName.includes('Cassia')) return 'scheduler';
  if (taskName.includes('Pepper')) return 'scheduler';
  if (taskName.includes('Nigella')) return 'scheduler';
  if (taskName.includes('Anya')) return 'scheduler';
  if (taskName.includes('Nyx')) return 'scheduler';
  if (taskName.includes('Freya')) return 'scheduler';
  if (taskName.includes('Sage')) return 'scheduler';
  return 'scheduler';
}

export function calculateLastRun(nextRun: Date, schedule: string): Date {
  const lastRun = new Date(nextRun);

  if (schedule.includes('every day')) {
    lastRun.setDate(lastRun.getDate() - 1);
  } else if (schedule.includes('monday') || schedule.includes('friday') ||
             schedule.includes('saturday') || schedule.includes('sunday')) {
    lastRun.setDate(lastRun.getDate() - 7);
  } else if (schedule.includes('every 2 weeks')) {
    lastRun.setDate(lastRun.getDate() - 14);
  } else if (schedule.includes('every 4 weeks')) {
    lastRun.setDate(lastRun.getDate() - 28);
  } else {
    lastRun.setDate(lastRun.getDate() - 1);
  }

  return lastRun;
}
