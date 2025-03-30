'use client';

import { Event } from '@/types/event';
import { format, startOfWeek, addDays, isToday, isSameDay } from 'date-fns';
import { vi } from 'date-fns/locale';
import './MiniCalendar.css';

interface MiniCalendarProps {
  events: Event[];
}

export function MiniCalendar({ events }: MiniCalendarProps) {
  const today = new Date();
  const startOfCurrentWeek = startOfWeek(today, { weekStartsOn: 1 }); // Bắt đầu từ thứ 2

  // Tạo mảng các ngày trong tuần
  const weekDays = Array.from({ length: 7 }, (_, i) => {
    const date = addDays(startOfCurrentWeek, i);
    const eventsOnDay = events.filter(event => 
      isSameDay(new Date(event.startDate), date)
    );
    
    return {
      date,
      events: eventsOnDay,
      isToday: isToday(date)
    };
  });

  return (
    <div className="mini-calendar">
      <div className="calendar-header">
        <h3 className="calendar-title">Lịch tuần này</h3>
        <span className="calendar-date">
          {format(today, 'MMMM yyyy', { locale: vi })}
        </span>
      </div>

      <div className="calendar-grid">
        {weekDays.map(({ date, events, isToday }) => {
          const hasEvents = events.length > 0;
          const needsCheckIn = events.some(event => !event.isCheckedIn);

          return (
            <div 
              key={date.toString()} 
              className={`calendar-day ${isToday ? 'today' : ''} ${hasEvents ? 'has-events' : ''} ${needsCheckIn ? 'needs-checkin' : ''}`}
            >
              <div className="day-header">
                <span className="day-name">
                  {format(date, 'EEEEEE', { locale: vi })}
                </span>
                <span className="day-number">
                  {format(date, 'd')}
                </span>
              </div>
              {hasEvents && (
                <div className="event-dots">
                  {events.map(event => (
                    <div 
                      key={event.id}
                      className={`event-dot ${!event.isCheckedIn ? 'needs-checkin' : ''}`}
                      title={event.title}
                    />
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
} 