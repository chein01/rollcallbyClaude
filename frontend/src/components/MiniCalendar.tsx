'use client';

import { useState, useEffect } from 'react';
import { format, addDays, startOfWeek, isSameDay, isSameMonth } from 'date-fns';
import { Event } from '@/types/event';
import { CalendarIcon } from 'lucide-react';

interface MiniCalendarProps {
  events: Event[];
}

export function MiniCalendar({ events }: MiniCalendarProps) {
  const [currentDate] = useState(new Date());
  const [isMounted, setIsMounted] = useState(false);

  const startDate = startOfWeek(currentDate, { weekStartsOn: 1 }); // Start from Monday
  const weekDays = Array.from({ length: 7 }).map((_, i) => {
    const day = addDays(startDate, i);
    return {
      date: day,
      dayName: format(day, 'EEE').substring(0, 1), // First letter of day name
      dayNumber: format(day, 'd'),
      isToday: isSameDay(day, new Date()),
      isCurrentMonth: isSameMonth(day, currentDate),
      hasEvent: events.some(event => isSameDay(new Date(event.startDate), day))
    };
  });

  // Get current month name and year
  const monthYear = format(currentDate, 'MMMM yyyy');

  // Set mounted state
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Nếu chưa mounted, hiển thị phiên bản đơn giản
  if (!isMounted) {
    return (
      <div className="mini-calendar-container">
        <div className="mini-calendar-header">
          <h3 className="mini-calendar-title">
            <CalendarIcon className="inline-block mr-2 h-5 w-5" />
            This Week
          </h3>
        </div>
        <div className="priority-event-loading">Loading calendar...</div>
      </div>
    );
  }

  return (
    <div className="mini-calendar-container">
      <div className="mini-calendar-header">
        <h3 className="mini-calendar-title">
          <CalendarIcon className="inline-block mr-2 h-5 w-5" />
          This Week
        </h3>
        <span className="text-sm text-muted-foreground">{monthYear}</span>
      </div>

      <div className="mini-calendar-days">
        {weekDays.map((day, index) => (
          <div key={`day-${index}`} className="mini-calendar-day">
            {day.dayName}
          </div>
        ))}
      </div>

      <div className="mini-calendar-grid">
        {weekDays.map((day, index) => (
          <div
            key={`date-${index}`}
            className={`mini-calendar-date ${day.isToday ? 'today' : ''} ${day.isCurrentMonth ? 'active' : ''} ${day.hasEvent ? 'has-event' : ''}`}
          >
            {day.dayNumber}
          </div>
        ))}
      </div>
    </div>
  );
} 