"use client";

import { useState } from "react";
import Calendar from "react-calendar";
import { bots } from "@/data/bots";
import styles from "./SchedulerCalendar.module.css";
import "react-calendar/dist/Calendar.css";

interface ScheduledTask {
  id: string;
  name: string;
  nextRun: string;
  schedule: string;
  humanReadable?: string;
  status: "active" | "paused" | "failed";
}

interface SchedulerCalendarProps {
  tasks: ScheduledTask[];
  onDateSelect?: (date: Date | null) => void;
  selectedDate?: Date | null;
}

export default function SchedulerCalendar({
  tasks,
  onDateSelect,
  selectedDate,
}: SchedulerCalendarProps) {
  const [value, setValue] = useState(selectedDate || new Date());

  const handleDateChange = (newValue: Date) => {
    setValue(newValue);
    if (onDateSelect) {
      onDateSelect(newValue);
    }
  };

  // Get bot from task name
  const getBotFromTaskName = (taskName: string) => {
    const match = taskName.match(/[🌅🌶️🍝🎨🚀💪🧙👻🎵]\s+(\w+)/);
    if (match) {
      const botName = match[1].toLowerCase();
      return bots.find((bot) => bot.id === botName);
    }
    return null;
  };

  // Check if task runs on a specific date based on schedule
  const taskRunsOnDate = (task: ScheduledTask, date: Date): boolean => {
    const schedule = (task.humanReadable || task.schedule).toLowerCase();
    const dayOfWeek = date.getDay(); // 0 = Sunday, 1 = Monday, etc.
    const dayOfMonth = date.getDate();

    // Daily tasks
    if (schedule.includes("every day") || schedule.includes("daily")) {
      return true;
    }

    // Weekly tasks - specific day
    if (schedule.includes("monday") && dayOfWeek === 1) return true;
    if (schedule.includes("tuesday") && dayOfWeek === 2) return true;
    if (schedule.includes("wednesday") && dayOfWeek === 3) return true;
    if (schedule.includes("thursday") && dayOfWeek === 4) return true;
    if (schedule.includes("friday") && dayOfWeek === 5) return true;
    if (schedule.includes("saturday") && dayOfWeek === 6) return true;
    if (schedule.includes("sunday") && dayOfWeek === 0) return true;

    // Bi-weekly (every 2 weeks) - check if it's the same day of week as nextRun
    if (schedule.includes("every 2 weeks") || schedule.includes("bi-weekly")) {
      const nextRun = new Date(task.nextRun);
      if (dayOfWeek === nextRun.getDay()) {
        const weeksDiff = Math.floor(
          (date.getTime() - nextRun.getTime()) / (7 * 24 * 60 * 60 * 1000),
        );
        return weeksDiff % 2 === 0;
      }
      return false;
    }

    // Every 4 weeks (monthly-ish)
    if (schedule.includes("every 4 weeks")) {
      const nextRun = new Date(task.nextRun);
      if (dayOfWeek === nextRun.getDay()) {
        const weeksDiff = Math.floor(
          (date.getTime() - nextRun.getTime()) / (7 * 24 * 60 * 60 * 1000),
        );
        return weeksDiff % 4 === 0;
      }
      return false;
    }

    // Default: check if it matches nextRun date exactly
    const nextRun = new Date(task.nextRun);
    return (
      date.getDate() === nextRun.getDate() &&
      date.getMonth() === nextRun.getMonth() &&
      date.getFullYear() === nextRun.getFullYear()
    );
  };

  // Get tasks for a specific date
  const getTasksForDate = (date: Date) => {
    return tasks.filter((task) => taskRunsOnDate(task, date));
  };

  // Custom tile content - show colored dots for bot activities
  const tileContent = ({ date, view }: { date: Date; view: string }) => {
    if (view !== "month") return null;

    const dayTasks = getTasksForDate(date);
    if (dayTasks.length === 0) return null;

    // Get unique bot colors for this day
    const botColors = new Set(
      dayTasks
        .map((task) => getBotFromTaskName(task.name))
        .filter((bot) => bot !== null)
        .map((bot) => bot!.color),
    );

    return (
      <div className={styles.taskIndicators}>
        {Array.from(botColors)
          .slice(0, 4)
          .map((color, idx) => (
            <span
              key={idx}
              className={styles.taskDot}
              style={{ backgroundColor: color }}
            />
          ))}
        {botColors.size > 4 && (
          <span className={styles.moreIndicator}>+{botColors.size - 4}</span>
        )}
      </div>
    );
  };

  // Add custom class to tiles with tasks
  const tileClassName = ({ date, view }: { date: Date; view: string }) => {
    if (view !== "month") return null;

    const dayTasks = getTasksForDate(date);
    const activeTasksCount = dayTasks.filter(
      (t) => t.status === "active",
    ).length;

    if (activeTasksCount > 0) {
      return styles.hasActiveTasks;
    }

    return null;
  };

  return (
    <div className={styles.calendarWrapper}>
      <Calendar
        onChange={(val) => handleDateChange(val as Date)}
        value={value}
        tileContent={tileContent}
        tileClassName={tileClassName}
        locale="en-US"
        minDetail="month"
        next2Label={null}
        prev2Label={null}
      />
    </div>
  );
}
