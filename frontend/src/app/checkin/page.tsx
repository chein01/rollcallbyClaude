'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAppSelector } from '@/store';
import { format } from 'date-fns';
import { MapPin, Users, Star, Calendar } from 'lucide-react';
import './styles.css';

interface TodayEvent {
  id: string;
  title: string;
  description: string;
  date: string;
  time: string;
  location: string;
  participants: number;
  stars: number;
  isCheckedIn: boolean;
}

// Sample data for demonstration
const todayEvents: TodayEvent[] = [
  {
    id: '1',
    title: 'Morning Stand-up',
    description: 'Daily team sync to discuss progress and blockers',
    date: '2024-03-20',
    time: '09:00',
    location: 'Meeting Room A',
    participants: 12,
    stars: 15,
    isCheckedIn: false
  },
  {
    id: '2',
    title: 'Project Review',
    description: 'Monthly review of project milestones and deliverables',
    date: '2024-03-20',
    time: '14:00',
    location: 'Conference Room',
    participants: 8,
    stars: 20,
    isCheckedIn: true
  }
];

export default function CheckInPage() {
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const router = useRouter();
  const [events, setEvents] = useState<TodayEvent[]>(todayEvents);

  const handleCheckIn = (eventId: string) => {
    setEvents(events.map(event => 
      event.id === eventId 
        ? { ...event, isCheckedIn: true }
        : event
    ));
  };

  return (
    <main className="checkin-container">
      <div className="checkin-content">
        <div className="page-header">
          <h1 className="page-title">Today's Check-ins</h1>
          <p className="page-subtitle">
            {format(new Date(), 'EEEE, MMMM d, yyyy')}
          </p>
        </div>

        <div className="events-list">
          {events.map((event) => (
            <div key={event.id} className="event-card">
              <div className="event-time">
                <Calendar size={20} />
                <span>{event.time}</span>
              </div>
              
              <div className="event-details">
                <h3 className="event-title">{event.title}</h3>
                <p className="event-description">{event.description}</p>
                
                <div className="event-meta">
                  <div className="event-location">
                    <MapPin size={16} />
                    <span>{event.location}</span>
                  </div>
                  <div className="event-participants">
                    <Users size={16} />
                    <span>{event.participants} participants</span>
                  </div>
                  <div className="event-stars">
                    <Star size={16} />
                    <span>{event.stars} stars</span>
                  </div>
                </div>
              </div>

              <button 
                className={`checkin-button ${event.isCheckedIn ? 'checked-in' : ''}`}
                onClick={() => handleCheckIn(event.id)}
                disabled={event.isCheckedIn}
              >
                {event.isCheckedIn ? 'Checked In' : 'Check In'}
              </button>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
} 